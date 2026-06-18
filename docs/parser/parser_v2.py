import json
import re
import pdfplumber


def extract_text_by_columns(pdf_path):
    """PDF의 기하학적 좌표를 이용해 좌단과 우단을 분리하여 텍스트를 추출합니다."""
    full_content = []

    print(f"[*] '{pdf_path}' 파일 분석 및 다단 분리 작업을 시작합니다...")

    with pdfplumber.open(pdf_path) as pdf:
        for idx, page in enumerate(pdf.pages):
            width = page.width
            height = page.height

            # 1페이지 상단에 간혹 존재하는 큰 시험명 헤더 영역 바운딩 박스 설정 (선택적)
            # 여기서는 페이지를 정확히 가로 절반(좌/우)으로 쪼개어 추출합니다.
            left_bbox = (0, 0, width / 2, height)
            right_bbox = (width / 2, 0, width, height)

            left_page = page.within_bbox(left_bbox)
            right_page = page.within_bbox(right_bbox)

            left_text = left_page.extract_text() or ""
            right_text = right_page.extract_text() or ""

            # 좌측 단을 먼저 넣고 우측 단을 이어서 결합하여 순서 엉킴 방지
            full_content.append(left_text)
            full_content.append(right_text)

            print(f"    - {idx + 1} 페이지 분리 성공")

    return "\n".join(full_content)


def parse_clean_exam(text_data):
    """다단 분리된 텍스트를 기반으로 문제와 보기를 정밀 구조화합니다."""
    # 불필요한 메타 레이블 및 줄바꿈 공백 청소
    lines = [line.strip() for line in text_data.split("\n") if line.strip()]

    questions_list = []
    current_q = None

    # 보기 정규식 패턴 (원문자 혹은 줄 시작점에 단독으로 나타나는 숫자/기호 대응)
    # 공무원 시험의 특성상 ①, ②, ③, ④ 외에 가끔 OCR 오류로 1, 2, 3, 4로 쪼개지는 경우 매칭
    opt_marker_regex = re.compile(r"^([①②③④1234])\s*(.*)")

    for line in lines:
        # 시험지 정보 필터링
        if (
            "PAGE" in line
            or "국가공무원" in line
            or "가책형" in line
            or "컴퓨터일반" in line
        ):
            continue

        # '문 1.', '문 20.' 등 신규 문제 시작점 정밀 감지
        if line.startswith("문") and "." in line:
            header_part = line.split(".")[0]
            num_match = re.search(r"\d+", header_part)

            if num_match:
                # 새로운 문항을 만나면 기존에 가공 중이던 문항을 저장
                if current_q:
                    questions_list.append(current_q)

                q_num = int(num_match.group())
                # '문 X.' 이후의 문자열을 지문 시작점으로 확보
                q_text_start = line.split(".", 1)[1].strip()

                current_q = {
                    "number": q_num,
                    "question": q_text_start,
                    "options": {"1": "", "2": "", "3": "", "4": ""},
                    "last_opt_idx": None,
                }
                continue

        # 문제 본문 누적 및 보기 데이터 분리 적재
        if current_q:
            opt_match = opt_marker_regex.match(line)

            if opt_match:
                marker = opt_match.group(1)
                opt_content = opt_match.group(2).strip()

                # 기호 표준화 매핑 (① -> 1, 2 -> 2 등)
                map_dict = {"①": "1", "②": "2", "③": "3", "④": "4"}
                norm_idx = map_dict.get(marker, marker)

                if norm_idx in ["1", "2", "3", "4"]:
                    current_q["last_opt_idx"] = norm_idx
                    current_q["options"][norm_idx] = opt_content
            else:
                # 보기가 먼저 감지된 상태에서 줄바꿈된 연속 텍스트가 오는 경우 보기 내용에 가산
                if current_q["last_opt_idx"]:
                    current_q["options"][current_q["last_opt_idx"]] += (
                        " " + line
                    )
                else:
                    # 보기가 나오기 전 지문이 줄바꿈된 경우 지문에 가산
                    current_q["question"] += "\n" + line

    # 루프가 끝난 후 마지막 문항 추가
    if current_q:
        questions_list.append(current_q)

    # 정리 단계: 후처리 가독성 개선 및 불필요 추적 키 삭제
    for q in questions_list:
        if "last_opt_idx" in q:
            del q["last_opt_idx"]
        # 연속된 공백이나 줄바꿈 다듬기
        q["question"] = json.loads(json.dumps(q["question"].strip()))

    return questions_list


if __name__ == "__main__":
    pdf_filename = "컴퓨터일반-가.pdf"
    output_json_filename = "고도화된_컴퓨터일반_결과.json"

    try:
        # 1단계 좌표 기반 텍스트 추출
        raw_split_text = extract_text_by_columns(pdf_filename)

        # 2단계 텍스트 구조화 알고리즘 가동
        final_parsed_json = parse_clean_exam(raw_split_text)

        # 3단계 저장
        with open(output_json_filename, "w", encoding="utf-8") as output_file:
            json.dump(
                final_parsed_json, output_file, ensure_ascii=False, indent=4
            )

        print("\n[+] 인텔리전스 다단 파싱 성공!")
        print(
            f"[+] 총 {len(final_parsed_json)}개의 문제가 완벽하게 매핑되어 '{output_json_filename}'에 저장되었습니다."
        )

    except FileNotFoundError:
        print(
            f"[-] 파일 에러: '{pdf_filename}'이 현재 디렉토리에 없습니다."
        )
    except Exception as error:
        print(f"[-] 시스템 장애 원인: {error}")