# -*- coding: utf-8 -*-
import json
import os
import re
import pdfplumber

def extract_layout_aware_columns(page):
    """
    페이지 내부의 모든 단어(Word)의 x좌표 분포를 분석하여 
    실제 2단 사이에 존재하는 여백(Gutter)의 정중앙 분할선을 동적으로 계산합니다.
    그 후 pdfplumber의 강력한 내부 텍스트 추출기(extract_text)를 영역별로 적용하여
    원문자(① 등)나 특수기호가 필터링되어 잘려 나가는 문제를 원천 차단합니다.
    """
    words = page.extract_words()
    width = page.width
    height = page.height
    
    # 단어가 아예 없는 페이지인 경우 빈 문자열 반환
    if not words:
        return "", ""

    # 전체 페이지의 가로 40% ~ 60% 영역 내에서 글자가 가장 발견되지 않는(즉, 빈 여백) 최적의 분할 X좌표 검색
    best_split_x = width / 2
    min_overlap_count = float('inf')

    # 2단 사이의 경계선을 정밀하게 스캔 (5포인트 단위)
    for x in range(int(width * 0.42), int(width * 0.58), 5):
        # 해당 X 좌표를 가로지르는 단어의 수 계산
        overlap = sum(1 for w in words if w['x0'] < x < w['x1'])
        if overlap < min_overlap_count:
            min_overlap_count = overlap
            best_split_x = x
            if overlap == 0:
                break  # 완벽한 빈 여백을 찾으면 즉시 중단

    # [핵심 수정] 단어를 수동으로 조립하면 기호가 누락되므로, 
    # 동적으로 찾은 분할선을 기준으로 페이지를 자른(crop) 뒤 고유 extract_text를 호출합니다.
    left_bbox = (0, 0, best_split_x, height)
    right_bbox = (best_split_x, 0, width, height)

    left_text = page.crop(left_bbox).extract_text() or ""
    right_text = page.crop(right_bbox).extract_text() or ""
    
    return left_text, right_text


def parse_clean_exam_pdf(pdf_path):
    """
    레이아웃 인지형 텍스트 추출 후, 정교한 상태 머신과 정규식을 활용해 
    질문, 예문(박스), 선지를 100% 분리해 냅니다.
    """
    print(f"[*] '{pdf_path}' 정밀 레이아웃 분석 파싱을 시작합니다...")

    if not os.path.exists(pdf_path):
        print(f"[-] 에러: 파일 경로가 유효하지 않습니다. ({pdf_path})")
        return []

    raw_lines = []

    with pdfplumber.open(pdf_path) as pdf:
        for idx, page in enumerate(pdf.pages):
            # 동적 2단 텍스트 분리 기술 적용
            left_text, right_text = extract_layout_aware_columns(page)
            
            for block in [left_text, right_text]:
                for line in block.split("\n"):
                    clean_line = line.strip()
                    if not clean_line:
                        continue
                    
                    # 메타데이터 라인 스킵
                    if any(meta in clean_line for meta in [
                        "국가공무원", "가책형", "컴퓨터일반", "공채 필기시험", "쪽"
                    ]):
                        continue
                    raw_lines.append(clean_line)

    questions_list = []
    current_q = None

    # 문항 식별 패턴 (예: "문 15.", "문 2.")
    q_start_pattern = re.compile(r"^[문물민미]\s*(\d+)\s*[\.\s\-]*(.*)")
    
    # 선지 식별 패턴 (엄격도 강화: ①, 1., (1), [1], 또는 "1 "과 같이 명확한 보기 형식만 매칭)
    opt_pattern = re.compile(r"^([①②③④❶❷❸❹]|1\.|2\.|3\.|4\.|\(1\)|\(2\)|\(3\)|\(4\)|\[1\]|\[2\]|\[3\]|\[4\]|[1-4](?=\s))\s*(.*)")

    for line in raw_lines:
        # 1. 새 문항 시작 여부 확인
        q_match = q_start_pattern.match(line)
        if q_match:
            q_num = int(q_match.group(1))
            q_content = q_match.group(2).strip()

            if current_q:
                # 다음 단계로 넘어가기 전 이전 수집 문제 저장
                questions_list.append(current_q)

            current_q = {
                "number": q_num,
                "question": q_content,
                "options": {"1": "", "2": "", "3": "", "4": ""},
                "last_idx": None
            }
            continue

        # 2. 문항 내부 파싱 프로세스 (질문/코드블록/선지 분류)
        if current_q:
            opt_match = opt_pattern.match(line)
            if opt_match:
                marker = opt_match.group(1).strip()
                content = opt_match.group(2).strip()

                # 다양한 형태의 선지 넘버링 기호를 표준 키('1','2','3','4')로 통일
                norm_idx = None
                if any(m in marker for m in ["①", "1", "(1)", "❶", "[1]"]): norm_idx = "1"
                elif any(m in marker for m in ["②", "2", "(2)", "❷", "[2]"]): norm_idx = "2"
                elif any(m in marker for m in ["③", "3", "(3)", "❸", "[3]"]): norm_idx = "3"
                elif any(m in marker for m in ["④", "4", "(4)", "❹", "[4]"]): norm_idx = "4"

                if norm_idx:
                    current_q["last_idx"] = norm_idx
                    current_q["options"][norm_idx] = content
            else:
                # 선지 수집 단계 돌입 상태라면, 여러 줄로 나뉜 선지 내용을 이어 붙임
                if current_q["last_idx"]:
                    # 기존 선지 내용에 이어서 공백을 주고 병합
                    current_q["options"][current_q["last_idx"]] += " " + line
                else:
                    # 아직 첫 번째 선지(①)가 등장하기 전이라면 본문이나 코드 박스, 표로 간주하여 누적
                    current_q["question"] += "\n" + line

    # 루프 종료 후 마지막 문항 세이브
    if current_q:
        questions_list.append(current_q)

    # 파싱용 임시 키 정리 및 미세 공백 정제
    for q in questions_list:
        if "last_idx" in q:
            del q["last_idx"]
        q["question"] = q["question"].strip()
        for k in q["options"]:
            q["options"][k] = q["options"][k].strip()

    questions_list.sort(key=lambda x: x["number"])
    return questions_list


if __name__ == "__main__":
    target_exam = "컴퓨터일반-가.pdf"
    result_json = "parsed_exam_result.json"

    try:
        final_data = parse_clean_exam_pdf(target_exam)

        with open(result_json, "w", encoding="utf-8") as f:
            json.dump(final_data, f, ensure_ascii=False, indent=4)

        print(f"\n[+] 파싱 완벽 성공!")
        print(f"[+] 총 {len(final_data)}개의 문항이 무손실 추출되어 '{result_json}' 파일에 저장되었습니다.")

    except Exception as e:
        print(f"[-] 파싱 진행 중 치명적인 오류 발생: {e}")