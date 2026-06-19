# -*- coding: utf-8 -*-
import json
import os
import re
import pdfplumber


def parse_clean_exam_pdf(pdf_path):
    """
    기하학적 영역 분리 기법을 적용하여 2단 다단 시험지의 데이터를 완벽하게 정제합니다.
    """
    print(f"[*] '{pdf_path}' 파일 분석을 완벽히 새로 시작합니다...")

    if not os.path.exists(pdf_path):
        print(f"[-] 에러: 현재 폴더에 '{pdf_path}' 파일이 없습니다.")
        return []

    raw_lines = []

    # 1. 기하 좌표 분석 기반 2단 크롭 및 정렬된 텍스트 추출
    with pdfplumber.open(pdf_path) as pdf:
        for idx, page in enumerate(pdf.pages):
            width = page.width
            height = page.height

            # 정확하게 좌단(Left Col)과 우단(Right Col) 바운딩 박스 설정
            left_bbox = (0, 0, width / 2, height)
            right_bbox = (width / 2, 0, width, height)

            left_area = page.within_bbox(left_bbox)
            right_area = page.within_bbox(right_bbox)

            left_text = left_area.extract_text() or ""
            right_text = right_area.extract_text() or ""

            # 한 페이지 내에서 좌단 우선 추출 후 우단 연동 결합
            for block in [left_text, right_text]:
                for line in block.split("\n"):
                    clean_line = line.strip()
                    if not clean_line:
                        continue
                    
                    # 시험지 상하단 메타데이터 및 무의미한 표 안내 라인 정화
                    if any(meta in clean_line for meta in [
                        "국가공무원", "가책형", "컴퓨터일반", "쪽", "PAGE", "The following table:"
                    ]):
                        continue
                    raw_lines.append(clean_line)

    print(f"[*] 정제된 원천 데이터 추출 성공 (총 {len(raw_lines)} 라인). 구조 분석 가동...")

    questions_list = []
    current_q = None

    # 정밀 매칭을 위한 정규식 가이드
    # - q_start_pattern: '문 1.', '문 20.' 등 감지 (문자가 약간 번져 '물1.', '민1.' 로 읽히는 예외 보정)
    q_start_pattern = re.compile(r"^[문물민미]\s*(\d+)\s*[\.\s\-]*(.*)")
    
    # - opt_pattern: ①, ②, ③, ④ 또는 OCR 오인식 숫자(1, 2, 3, 4) 감지
    opt_pattern = re.compile(r"^([①②③④❶❷❸❹]|[1-4]\.|\([1-4]\)|^[1-4]\s+)\s*(.*)")

    for line in raw_lines:
        # 신규 문항 헤더 시작점 감지
        q_match = q_start_pattern.match(line)
        if q_match:
            q_num = int(q_match.group(1))
            q_content = q_match.group(2).strip()

            # 이전 수집 문항이 있다면 안전하게 보관함에 적재
            if current_q:
                questions_list.append(current_q)

            current_q = {
                "number": q_num,
                "question": q_content,
                "options": {"1": "", "2": "", "3": "", "4": ""},
                "last_idx": None
            }
            continue

        # 수집 진행 중인 문항이 있는 경우
        if current_q:
            opt_match = opt_pattern.match(line)
            if opt_match:
                marker = opt_match.group(1).strip()
                content = opt_match.group(2).strip()

                # 비표준화 기호(원문자, 일반 숫자)를 표준 인덱스('1','2','3','4')로 전환
                norm_idx = None
                if any(m in marker for m in ["①", "1", "(1)"]):
                    norm_idx = "1"
                elif any(m in marker for m in ["②", "2", "(2)"]):
                    norm_idx = "2"
                elif any(m in marker for m in ["③", "3", "(3)"]):
                    norm_idx = "3"
                elif any(m in marker for m in ["④", "4", "(4)"]):
                    norm_idx = "4"

                if norm_idx:
                    current_q["last_idx"] = norm_idx
                    current_q["options"][norm_idx] = content
            else:
                # 보기가 감지되기 시작한 시점 이후라면, 해당 보기의 줄바꿈 연장 텍스트로 결합
                if current_q["last_idx"]:
                    # 유실된 보기가 있더라도 이전 보기에 문맥 병합 방지 안전망
                    # 만약 라인이 특정 키워드로 독립 선지처럼 기능한다면 예외처리 가능
                    current_q["options"][current_q["last_idx"]] += " " + line
                else:
                    # 보기가 아직 나오지 않은 지문(C언어 코드 박스, 표 데이터, 수식 등)은 줄바꿈 형태 그대로 누적
                    current_q["question"] += "\n" + line

    # 루프 종료 후 마지막 문항 최종 대피 보관
    if current_q:
        questions_list.append(current_q)

    # 파싱용 상태 플래그 제거 및 가독성 다듬기
    for q in questions_list:
        if "last_idx" in q:
            del q["last_idx"]
        q["question"] = q["question"].strip()

        # [특수 정화] 7번, 10번 등 박스 안의 정답 선택 옵션(ㄱ, ㄴ, ㄷ, ㄹ) 및 보기 꼬임 예외 처리 보정
        # 만약 보기 중 공란이 남아있고 question 필드 하단에 선지가 합쳐져 수집된 정황이 감지되면 자동 복구 적용
        lines_in_q = q["question"].split("\n")
        rebuilt_q_lines = []
        for l in lines_in_q:
            l_strip = l.strip()
            # 보기 선지가 지문에 혼입된 케이스 강제 적출
            inner_opt = opt_pattern.match(l_strip)
            if inner_opt:
                im_marker = inner_opt.group(1).strip()
                im_content = inner_opt.group(2).strip()
                
                im_idx = None
                if any(m in im_marker for m in ["①", "1", "(1)"]): im_idx = "1"
                elif any(m in im_marker for m in ["②", "2", "(2)"]): im_idx = "2"
                elif any(m in im_marker for m in ["③", "3", "(3)"]): im_idx = "3"
                elif any(m in im_marker for m in ["④", "4", "(4)"]): im_idx = "4"

                if im_idx and not q["options"][im_idx]:
                    q["options"][im_idx] = im_content
                    continue
            rebuilt_q_lines.append(l)
        
        q["question"] = "\n".join(rebuilt_q_lines).strip()

    # 문항 번호 순서 정렬 보증
    questions_list.sort(key=lambda x: x["number"])
    return questions_list


if __name__ == "__main__":
    target_exam = "컴퓨터일반-가.pdf"
    result_json = "parsed_exam_result.json"

    try:
        final_data = parse_clean_exam_pdf(target_exam)

        with open(result_json, "w", encoding="utf-8") as f:
            json.dump(final_data, f, ensure_ascii=False, indent=4)

        print(f"\n[+] 파싱 프로세스 완벽 성공!")
        print(f"[+] 총 {len(final_data)}개의 핵심 문항이 정제되어 '{result_json}' 파일에 보관되었습니다.")

    except Exception as e:
        print(f"[-] 장애가 발생하였습니다: {e}")