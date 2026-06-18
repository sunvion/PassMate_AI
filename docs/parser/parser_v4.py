import json
import pypdf


def parse_pure_pdf_exam(file_path):
    print(f"[*] '{file_path}' 파일로부터 텍스트 레이어 추출을 시작합니다...")

    content = ""

    # [할 일] 바이너리 모드("rb")로 PDF를 열어 각 페이지의 텍스트를 직접 추출
    with open(file_path, "rb") as f:
        reader = pypdf.PdfReader(f)
        print(f"[*] 총 {len(reader.pages)} 페이지가 감지되었습니다.")

        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                content += page_text + "\n"

    if not content.strip():
        raise ValueError(
            "PDF 내부에서 텍스트를 추출하지 못했습니다. 스캔된 이미지 형태의 PDF인지 확인이 필요합니다."
        )

    # 3. 추출된 텍스트 가공 프로세스 (줄바꿈 단위 분할)
    raw_lines = content.split("\n")
    lines = [line.strip() for line in raw_lines if line.strip()]

    questions_list = []
    current_q = None

    # 원문자 및 깨진 보기 번호 대응용 매핑 테이블
    marker_map = {"①": "1", "②": "2", "③": "3", "④": "4"}

    for line in lines:
        # 무관한 시험지 메타데이터(헤더/푸터) 패스
        if "PAGE" in line or "국가공무원" in line or "가책형" in line:
            continue

        # '문 X.' 패턴 감지하여 신규 문제 블록 생성
        if line.startswith("문") and "." in line:
            header_part = line.split(".")[0]
            num_str = "".join([c for c in header_part if c.isdigit()])

            if num_str:
                if current_q:
                    questions_list.append(current_q)

                q_num = int(num_str)
                q_text = line.split(".", 1)[1].strip()

                current_q = {
                    "number": q_num,
                    "question": q_text,
                    "options": {"1": "", "2": "", "3": "", "4": ""},
                    "current_target_opt": None,
                }
                continue

        # 문제 내부 지문 및 보기 데이터 분류 정리
        if current_q:
            first_char = line[0]

            matched_opt = None
            if first_char in marker_map:
                matched_opt = marker_map[first_char]
            elif first_char in ["1", "2", "3", "4"] and (
                len(line) > 1 and (line[1] == " " or line[1].isalpha())
            ):
                matched_opt = first_char

            if matched_opt:
                current_q["current_target_opt"] = matched_opt
                current_q["options"][matched_opt] = line[1:].strip()
            else:
                target = current_q["current_target_opt"]
                if target:
                    current_q["options"][target] += " " + line
                else:
                    current_q["question"] += "\n" + line

    if current_q:
        questions_list.append(current_q)

    # 임시 핸들러 키 제거
    for q in questions_list:
        if "current_target_opt" in q:
            del q["current_target_opt"]

    return questions_list


if __name__ == "__main__":
    # 질문자님의 원본 파일명 설정
    target_pdf = "컴퓨터일반-가.pdf"

    try:
        results = parse_pure_pdf_exam(target_pdf)

        output_json = "parsed_result.json"
        with open(output_json, "w", encoding="utf-8") as jf:
            json.dump(results, jf, ensure_ascii=False, indent=4)

        print(f"\n[+] 파싱 완성과정 성공! 총 {len(results)}문제가 추출되었습니다.")
        print(f"[+] 저장된 파일: {output_json}")

    except FileNotFoundError:
        print(f"[-] 파일 에러: '{target_pdf}' 파일이 폴더 내에 존재하지 않습니다.")
    except Exception as e:
        print(f"[-] 시스템 예외 발생: {e}")