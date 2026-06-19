# =====================================================================
# [필수 조건] OpenMP 중복 초기화 에러(Error #15) 우회를 위한 환경 변수 세팅
# 반드시 다른 무거운 라이브러리(easyocr, torch 등)를 임포트하기 전에 실행해야 합니다.
# =====================================================================
import os

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import json
import re
from easyocr import Reader
from pdf2image import convert_from_path


def parse_pdf_via_ocr(pdf_path):
    print(f"[*] '{pdf_path}'를 이미지로 변환 후 OCR 분석을 시작합니다...")

    # PDF를 이미지로 렌더링 (300 DPI 설정)
    pages = convert_from_path(pdf_path, dpi=300)
    print(f"[*] 총 {len(pages)}개의 페이지 변환 완료.")

    # 한글과 영어를 동시에 인식하는 OCR 리더기 초기화
    reader = Reader(["ko", "en"])
    full_text_lines = []

    for idx, page in enumerate(pages):
        print(f"[*] {idx + 1} 페이지 문항 시각 탐색 및 텍스트 변환 중...")
        results = reader.readtext(page)

        # 다단 엉킴 방지를 위한 좌/우 영역 좌표 분할 정렬 알고리즘
        img_width, _ = page.size
        mid_x = img_width / 2

        left_col = []
        right_col = []

        for bbox, text, _ in results:
            top_left_x = bbox[0][0]
            top_left_y = bbox[0][1]

            if top_left_x < mid_x:
                left_col.append((top_left_y, text.strip()))
            else:
                right_col.append((top_left_y, text.strip()))

        left_col.sort(key=lambda x: x[0])
        right_col.sort(key=lambda x: x[0])

        for _, txt in left_col:
            if txt:
                full_text_lines.append(txt)
        for _, txt in right_col:
            if txt:
                full_text_lines.append(txt)

    # 3. 추출된 OCR 텍스트 라인 구조화 정돈
    questions_list = []
    current_q = None

    # 다양한 형태의 보기 인덱스 패턴 정의 (①, (1), [1], 1 등)
    opt_pattern = re.compile(r"^([①②③④1234\(\)\[\]])\s*(.*)")

    for line in full_text_lines:
        if (
            "국가공무원" in line
            or "가책형" in line
            or "컴퓨터일반" in line
            or "PAGE" in line
        ):
            continue

        # '문 1.', '문 20.' 문제의 서두 감지
        if line.startswith("문") and ("." in line or " " in line):
            num_part = "".join([c for c in line.split()[0:2] if c.isdigit()])
            if num_part:
                if current_q:
                    questions_list.append(current_q)

                split_parts = line.split(".", 1)
                q_text = split_parts[1].strip() if len(split_parts) > 1 else ""

                current_q = {
                    "number": int(num_part),
                    "question": q_text,
                    "options": {"1": "", "2": "", "3": "", "4": ""},
                    "last_idx": None,
                }
                continue

        # 문제 본문 결합 및 보기 적재
        if current_q:
            opt_match = opt_pattern.match(line)
            if opt_match:
                marker = opt_match.group(1)
                content = opt_match.group(2).strip()

                norm_idx = None
                if marker in ["①", "1", "(1)", "[1]"]:
                    norm_idx = "1"
                elif marker in ["②", "2", "(2)", "[2]"]:
                    norm_idx = "2"
                elif marker in ["③", "3", "(3)", "[3]"]:
                    norm_idx = "3"
                elif marker in ["④", "4", "(4)", "[4]"]:
                    norm_idx = "4"

                if norm_idx:
                    current_q["last_idx"] = norm_idx
                    current_q["options"][norm_idx] = content
            else:
                if current_q["last_idx"]:
                    current_q["options"][current_q["last_idx"]] += " " + line
                else:
                    current_q["question"] += "\n" + line

    if current_q:
        questions_list.append(current_q)

    for q in questions_list:
        if "last_idx" in q:
            del q["last_idx"]
        q["question"] = q["question"].strip()

    return questions_list


if __name__ == "__main__":
    pdf_filename = "컴퓨터일반-가.pdf"
    output_filename = "ocr_result.json"

    try:
        final_data = parse_pdf_via_ocr(pdf_filename)

        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(final_data, f, ensure_ascii=False, indent=4)

        print(f"\n[+] OCR 매핑 프로세스 성공! 결과 저장: {output_filename}")

    except Exception as e:
        print(f"[-] OCR 가동 중 오류 발생: {e}")