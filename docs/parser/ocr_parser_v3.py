import os

# [조건] OpenMP 중복 초기화 에러 우회 환경 변수 설정
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import json
import re
import sys
from easyocr import Reader
import numpy as np  # [필수] PIL 형식을 Numpy Array로 변환하기 위한 라이브러리
from pdf2image import convert_from_path


def get_conda_poppler_path():
    """현재 아나콘다 환경 내에 빌드된 poppler 실행 파일 경로를 탐색합니다."""
    executable_dir = os.path.dirname(sys.executable)
    poppler_bin = os.path.join(executable_dir, "Library", "bin")
    if os.path.exists(poppler_bin):
        return poppler_bin
    return None


def parse_pdf_via_ocr(pdf_path):
    print(f"[*] '{pdf_path}'를 이미지로 변환 후 OCR 분석을 시작합니다...")

    poppler_path = get_conda_poppler_path()
    if poppler_path:
        print(f"[*] 아나콘다 Poppler 엔진 연동 성공: {poppler_path}")

    # PDF의 페이지들을 PIL 이미지 객체 리스트로 렌더링
    pages = convert_from_path(pdf_path, dpi=300, poppler_path=poppler_path)
    print(f"[*] 총 {len(pages)}개의 페이지 이미지 렌더링 완료.")

    # CPU 기반 OCR 리더기 인스턴스 기동 (한글, 영어 대응)
    reader = Reader(["ko", "en"])
    full_text_lines = []

    for idx, page in enumerate(pages):
        print(f"[*] {idx + 1} 페이지 문항 시각 탐색 및 구조 분석 중...")

        # =================================================================
        # [할 일] Invalid input type 에러 원천 차단
        # PIL 이미지 객체를 easyocr이 지원하는 numpy array 형식으로 변환합니다.
        # =================================================================
        page_numpy = np.array(page)

        # 변환된 numpy 데이터를 엔진에 주입
        results = reader.readtext(page_numpy)

        # 다단 엉킴 방지 좌표 분할 알고리즘 가동
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

        # Y축 좌표 기준 상단에서 하단 순서로 라인 정렬
        left_col.sort(key=lambda x: x[0])
        right_col.sort(key=lambda x: x[0])

        for _, txt in left_col:
            if txt:
                full_text_lines.append(txt)
        for _, txt in right_col:
            if txt:
                full_text_lines.append(txt)

    # 3. 추출된 순수 시각 문자열 데이터 계층형 JSON 구조화 단계
    questions_list = []
    current_q = None

    # 다양한 형태의 보기 넘버링 마커 감지 패턴 정규식
    opt_pattern = re.compile(
        r"^([①②③④1234]|\([1234]\)|\[[1234]\])\s*(.*)"
    )

    for line in full_text_lines:
        if (
            "국가공무원" in line
            or "가책형" in line
            or "컴퓨터일반" in line
            or "PAGE" in line
            or "쪽" in line
        ):
            continue

        # '문 X.' 패턴 매칭 검증
        if line.startswith("문") and ("." in line or " " in line):
            tokens = line.split()
            num_part = "".join([c for c in tokens[0:2] if c.isdigit()])
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

        # 지문 결합 및 보기 속성 배정
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

    # 파싱 상태 추적용 임시 데이터 정화
    for q in questions_list:
        if "last_idx" in q:
            del q["last_idx"]
        q["question"] = q["question"].strip()

    return questions_list


if __name__ == "__main__":
    pdf_filename = "컴퓨터일반-가.pdf"
    output_filename = "ocr_final_result.json"

    try:
        final_data = parse_pdf_via_ocr(pdf_filename)

        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(final_data, f, ensure_ascii=False, indent=4)

        print(
            f"\n[+] OCR 다단 파싱 엔진 완벽 작동 성공! 저장 경로: {output_filename}"
        )
        print(f"[+] 총 {len(final_data)}개의 핵심 기출 문항이 구조화되었습니다.")

    except Exception as e:
        print(f"[-] 크리티컬 장애 발생: {e}")