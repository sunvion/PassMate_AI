import json
import re


def parse_computer_general_pdf_text(file_path):
    # 1. 지원 가능한 인코딩으로 안전하게 파일 읽기
    encodings = ["utf-8", "cp949", "utf-8-sig", "euc-kr"]
    content = None

    for encoding in encodings:
        try:
            with open(file_path, "r", encoding=encoding) as f:
                content = f.read()
            print(f" 성공: '{encoding}' 인코딩으로 파일 로드 완료.")
            break
        except UnicodeDecodeError:
            continue

    if content is None:
        raise UnicodeDecodeError(
            "파일의 인코딩을 지원하는 방식을 찾을 수 없습니다."
        )

    # 2. 텍스트 데이터 전처리 (오류 유발 요인 원천 차단)
    # 인자 개수 오류를 방지하기 위해 정규식 sub 대신 기본 replace와 정돈된 sub만 사용
    content = content.replace("\\", "")  # 백슬래시 제거

    # 페이지 구분선 및 시험지 정보 제거
    content = re.sub(r"--- PAGE \d+ ---", "", content)
    content = re.sub(r"\\", "", content)
    content = re.sub(r"\d+년도 국가공무원 9급 공채 필기시험", "", content)
    content = re.sub(r"컴퓨터일반\s+가책형\s+\d+쪽", "", content)

    # 3. '문 1.', '문 2.' 패턴을 기준으로 문제 단락 분할
    question_pattern = re.compile(r"(문\s*\d+\.)")
    parts = question_pattern.split(content)

    questions_list = []

    for i in range(1, len(parts), 2):
        q_num_raw = parts[i].strip()
        q_body_raw = parts[i + 1]

        q_num = int(re.search(r"\d+", q_num_raw).group())

        # 4. 보기 기호 분리
        options_pattern = re.compile(r"([①②③④①234])")
        body_parts = options_pattern.split(q_body_raw)

        question_text = body_parts[0].strip()
        question_text = re.sub(r"\n+", "\n", question_text)

        options = {"1": "", "2": "", "3": "", "4": ""}

        for j in range(1, len(body_parts), 2):
            opt_marker = body_parts[j]
            opt_text = (
                body_parts[j + 1].strip() if j + 1 < len(body_parts) else ""
            )
            opt_text = re.sub(r"\s+", " ", opt_text)

            if opt_marker in ["①", "1"]:
                options["1"] = opt_text
            elif opt_marker in ["②", "2"]:
                options["2"] = opt_text
            elif opt_marker in ["③", "3"]:
                options["3"] = opt_text
            elif opt_marker in ["④", "4"]:
                options["4"] = opt_text

        questions_list.append(
            {"number": q_num, "question": question_text, "options": options}
        )

    return questions_list


if __name__ == "__main__":
    filename = "컴퓨터일반-가.pdf"

    try:
        parsed_results = parse_computer_general_pdf_text(filename)

        output_filename = "정리된_컴퓨터일반_문제.json"
        with open(output_filename, "w", encoding="utf-8") as json_file:
            json.dump(parsed_results, json_file, ensure_ascii=False, indent=4)

        print(
            f" 파싱 완료: 총 {len(parsed_results)}개의 문제가 '{output_filename}'으로 저장되었습니다."
        )

    except FileNotFoundError:
        print(f"❌ 오류: 현재 폴더 내에 '{filename}' 파일이 존재하지 않습니다.")
    except Exception as e:
        print(f"❌ 오류 상세 정보: {e}")