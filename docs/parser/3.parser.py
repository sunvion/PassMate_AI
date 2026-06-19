# 3.parser.py
from __future__ import annotations

import os
import re
import json
from dataclasses import dataclass
from typing import List, Dict, Optional, Any, Tuple

import fitz
import pdfplumber


PDF_PATH = "컴퓨터일반-가.pdf"

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
IMAGE_DIR = os.path.join(OUTPUT_DIR, "images")
JSON_PATH = os.path.join(OUTPUT_DIR, "questions.json")

EXAM_TYPE = "CS_GENERAL"
SUBJECT = "컴퓨터일반"

QUESTION_RE = re.compile(r"^\s*(?:문|물|민|미)\s*(\d+)\s*[\.:\)]?\s*$")
QUESTION_INLINE_RE = re.compile(r"^\s*(?:문|물|민|미)\s*(\d+)\s*[\.:\)]?\s*(.*)$")

OPTION_PATTERNS = [
    re.compile(r"^\s*([1-4])\s*[\.\)]?\s*(.*)$"),
    re.compile(r"^\s*([①②③④])\s*(.*)$"),
    re.compile(r"^\s*([가나다라마바사])\s*[\.\)]?\s*(.*)$"),
]


@dataclass
class WordBox:
    text: str
    x0: float
    top: float
    x1: float
    bottom: float
    page_num: int
    block_no: int = 0
    line_no: int = 0
    word_no: int = 0

    @property
    def cx(self) -> float:
        return (self.x0 + self.x1) / 2


@dataclass
class QuestionChunk:
    number: int
    page_num: int
    col: str
    bbox: List[float]
    text: str
    words: List[WordBox]
    question_type: str = "NORMAL"
    image_url: Optional[str] = None


def ensure_dirs() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(IMAGE_DIR, exist_ok=True)


def normalize_text(s: str) -> str:
    s = s.replace("\u00a0", " ").replace("\u200b", "")
    s = re.sub(r"[ \t]+", " ", s)
    return s.strip()


def extract_words_with_pdfplumber(pdf_path: str) -> List[WordBox]:
    all_words: List[WordBox] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_idx, page in enumerate(pdf.pages, start=1):
            words = page.extract_words(
                keep_blank_chars=False,
                use_text_flow=True,
                horizontal_ltr=True,
                extra_attrs=["fontname", "size"]
            ) or []
            for i, w in enumerate(words):
                txt = normalize_text(w.get("text", ""))
                if not txt:
                    continue
                all_words.append(
                    WordBox(
                        text=txt,
                        x0=float(w["x0"]),
                        top=float(w["top"]),
                        x1=float(w["x1"]),
                        bottom=float(w["bottom"]),
                        page_num=page_idx,
                        block_no=int(w.get("block_no", 0) or 0),
                        line_no=int(w.get("line_no", 0) or 0),
                        word_no=int(w.get("word_no", i) or i),
                    )
                )
    return all_words


def group_words_by_page(words: List[WordBox]) -> Dict[int, List[WordBox]]:
    pages: Dict[int, List[WordBox]] = {}
    for w in words:
        pages.setdefault(w.page_num, []).append(w)
    for p in pages:
        pages[p].sort(key=lambda x: (x.top, x.x0, x.word_no))
    return pages


def infer_split_x(words: List[WordBox], page_width: float) -> float:
    if not words:
        return page_width / 2
    xs = sorted(w.cx for w in words)
    if len(xs) < 20:
        return page_width / 2

    gaps = []
    for i in range(len(xs) - 1):
        gap = xs[i + 1] - xs[i]
        if gap > page_width * 0.08:
            gaps.append((gap, xs[i], xs[i + 1]))

    if not gaps:
        return page_width / 2

    _, a, b = max(gaps, key=lambda t: t[0])
    return (a + b) / 2


def lines_from_words(words: List[WordBox], y_tol: float = 4.5) -> List[List[WordBox]]:
    if not words:
        return []
    words = sorted(words, key=lambda w: (w.top, w.x0))
    lines: List[List[WordBox]] = []
    current = [words[0]]
    current_y = words[0].top

    for w in words[1:]:
        if abs(w.top - current_y) <= y_tol:
            current.append(w)
            current_y = (current_y * (len(current) - 1) + w.top) / len(current)
        else:
            current.sort(key=lambda x: x.x0)
            lines.append(current)
            current = [w]
            current_y = w.top

    current.sort(key=lambda x: x.x0)
    lines.append(current)
    return lines


def line_text(line: List[WordBox]) -> str:
    parts = [w.text for w in sorted(line, key=lambda x: x.x0)]
    txt = " ".join(parts)
    txt = re.sub(r"\s+([,.)\]])", r"\1", txt)
    txt = re.sub(r"([(\[])\s+", r"\1", txt)
    txt = re.sub(r"\s+", " ", txt)
    return txt.strip()


def line_bbox(line: List[WordBox]) -> List[float]:
    return [
        min(w.x0 for w in line),
        min(w.top for w in line),
        max(w.x1 for w in line),
        max(w.bottom for w in line),
    ]


def detect_question_number(txt: str) -> Optional[int]:
    m = QUESTION_INLINE_RE.match(txt)
    if m:
        return int(m.group(1))
    m = QUESTION_RE.match(txt)
    if m:
        return int(m.group(1))
    return None


def merge_bbox(a: Optional[List[float]], b: List[float]) -> List[float]:
    if a is None:
        return list(b)
    return [min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3])]


def classify_question(body: str) -> str:
    text = body.lower()
    code_keywords = ["int main", "#include", "printf(", "scanf(", "return 0", "{", "}"]
    table_keywords = ["릴레이션", "기본키", "외래키", "테이블", "고객아이디", "select", "from"]
    image_keywords = ["그림", "도표", "회로", "구조도", "이미지"]

    if any(k.lower() in text for k in code_keywords):
        return "CODE"
    if any(k.lower() in text for k in table_keywords):
        return "TABLE"
    if any(k.lower() in text for k in image_keywords):
        return "IMAGE"
    return "NORMAL"


def parse_options_from_body(body: str) -> Tuple[List[str], Dict[str, str], List[str]]:
    lines = [normalize_text(x) for x in body.splitlines() if normalize_text(x)]
    question_lines: List[str] = []
    options: Dict[str, str] = {}
    code_lines: List[str] = []

    in_options = False
    current_opt: Optional[str] = None

    option_patterns = [
        re.compile(r"^\s*([1-4])\s*[\.\)]?\s*(.*)$"),
        re.compile(r"^\s*([①②③④])\s*(.*)$"),
        re.compile(r"^\s*([가나다라마바사])\s*[\.\)]?\s*(.*)$"),
        re.compile(r"^\s*[·•\-]\s*(.*)$"),
    ]

    for ln in lines:
        matched = False

        for pat in option_patterns:
            m = pat.match(ln)
            if m:
                text = m.group(1)
                rest = m.group(2).strip() if m.lastindex and m.lastindex >= 2 else ""

                if text in ["①", "②", "③", "④"]:
                    key = {"①": "1", "②": "2", "③": "3", "④": "4"}[text]
                elif text in ["가", "나", "다", "라", "마", "바", "사"]:
                    key = text
                else:
                    key = text

                options[key] = rest
                in_options = True
                current_opt = key
                matched = True
                break

        if matched:
            continue

        if in_options and current_opt:
            if ln and not QUESTION_RE.match(ln) and not QUESTION_INLINE_RE.match(ln):
                if current_opt in options:
                    options[current_opt] = (options[current_opt] + " " + ln).strip()
                else:
                    options[current_opt] = ln
                continue

        if not in_options:
            question_lines.append(ln)

        if any(tok in ln for tok in ["int main", "#include", "printf(", "scanf(", "{", "}"]):
            code_lines.append(ln)

    return question_lines, options, code_lines


def build_question_chunks_for_page(page_num: int, page_words: List[WordBox], split_x: float) -> List[QuestionChunk]:
    left = [w for w in page_words if w.cx < split_x]
    right = [w for w in page_words if w.cx >= split_x]
    chunks: List[QuestionChunk] = []

    for col_name, col_words in (("L", left), ("R", right)):
        if not col_words:
            continue

        lines = lines_from_words(col_words)
        current_num: Optional[int] = None
        current_lines: List[List[WordBox]] = []
        current_words: List[WordBox] = []
        current_bbox: Optional[List[float]] = None

        for ln in lines:
            txt = line_text(ln)
            qnum = detect_question_number(txt)
            bbox = line_bbox(ln)

            if qnum is not None:
                if current_num is not None and current_lines:
                    body = "\n".join(line_text(x) for x in current_lines).strip()
                    chunks.append(
                        QuestionChunk(
                            number=current_num,
                            page_num=page_num,
                            col=col_name,
                            bbox=current_bbox or bbox,
                            text=body,
                            words=current_words.copy(),
                            question_type=classify_question(body),
                        )
                    )
                current_num = qnum
                current_lines = [ln]
                current_words = ln.copy()
                current_bbox = bbox
                continue

            if current_num is not None:
                current_lines.append(ln)
                current_words.extend(ln)
                current_bbox = merge_bbox(current_bbox, bbox)

        if current_num is not None and current_lines:
            body = "\n".join(line_text(x) for x in current_lines).strip()
            chunks.append(
                QuestionChunk(
                    number=current_num,
                    page_num=page_num,
                    col=col_name,
                    bbox=current_bbox or [0, 0, 0, 0],
                    text=body,
                    words=current_words.copy(),
                    question_type=classify_question(body),
                )
            )

    return chunks


def merge_same_number_questions(chunks: List[QuestionChunk]) -> List[QuestionChunk]:
    if not chunks:
        return []
    chunks = sorted(chunks, key=lambda q: (q.number, q.page_num, q.col, q.bbox[1], q.bbox[0]))
    merged: List[QuestionChunk] = []
    for q in chunks:
        if not merged or merged[-1].number != q.number:
            merged.append(q)
            continue
        prev = merged[-1]
        prev.text = (prev.text.rstrip() + "\n" + q.text.lstrip()).strip()
        prev.bbox = merge_bbox(prev.bbox, q.bbox)
        prev.words.extend(q.words)
        if prev.question_type == "NORMAL":
            prev.question_type = q.question_type
    return merged


def crop_question_image(doc: fitz.Document, q: QuestionChunk, output_path: str) -> None:
    page = doc[q.page_num - 1]
    rect = fitz.Rect(*q.bbox)
    pad = 10
    rect = fitz.Rect(
        max(0, rect.x0 - pad),
        max(0, rect.y0 - pad),
        min(page.rect.width, rect.x1 + pad),
        min(page.rect.height, rect.y1 + pad),
    )
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), clip=rect, alpha=False)
    pix.save(output_path)


def build_json_row(q: QuestionChunk) -> Dict[str, Any]:
    question_lines, options, code_lines = parse_options_from_body(q.text)
    question_text = question_lines[0] if question_lines else q.text[:200]

    return {
        "exam_type": EXAM_TYPE,
        "subject": SUBJECT,
        "year": None,
        "number": q.number,
        "question": [question_text],
        "body": q.text,
        "options": options,
        "answer": [],
        "explanation": None,
        "points": 5,
        "category": "기출문제",
        "question_type": q.question_type,
        "image_url": q.image_url,
        "video_url": None,
        "code_lines": code_lines,
        "image_crop_area": {
            "page": q.page_num,
            "bbox": [round(v, 2) for v in q.bbox],
        },
    }


def save_json(data: List[Dict[str, Any]], path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def parse_pdf_to_questions(pdf_path: str) -> List[Dict[str, Any]]:
    ensure_dirs()

    all_words = extract_words_with_pdfplumber(pdf_path)
    print("all_words:", len(all_words))

    pages = group_words_by_page(all_words)
    print("pages:", len(pages))

    fitz_doc = fitz.open(pdf_path)
    chunks: List[QuestionChunk] = []

    for page_num in range(1, fitz_doc.page_count + 1):
        page = fitz_doc[page_num - 1]
        page_words = pages.get(page_num, [])
        print("page", page_num, "words", len(page_words))
        if not page_words:
            continue

        split_x = infer_split_x(page_words, float(page.rect.width))
        page_chunks = build_question_chunks_for_page(page_num, page_words, split_x)
        print("page", page_num, "chunks", [c.number for c in page_chunks])
        chunks.extend(page_chunks)

    chunks = merge_same_number_questions(chunks)
    chunks = sorted(chunks, key=lambda x: x.number)

    print("merged chunks:", len(chunks))
    if not chunks:
        fitz_doc.close()
        raise RuntimeError("No questions parsed. Check question regex, column split, or line grouping.")

    for q in chunks:
        img_path = os.path.join(IMAGE_DIR, f"q{q.number}.png")
        crop_question_image(fitz_doc, q, img_path)
        q.image_url = f"images/q{q.number}.png"

    fitz_doc.close()

    json_rows = [build_json_row(q) for q in chunks]
    print("json rows:", len(json_rows))
    save_json(json_rows, JSON_PATH)
    print("saved json:", JSON_PATH)

    return json_rows


def main() -> None:
    if not os.path.exists(PDF_PATH):
        raise FileNotFoundError(f"PDF not found: {PDF_PATH}")
    parse_pdf_to_questions(PDF_PATH)


if __name__ == "__main__":
    main()

print(os.path.exists(JSON_PATH))
print(os.path.getsize(JSON_PATH))
print(os.path.exists(os.path.join(IMAGE_DIR, "q1.png")))