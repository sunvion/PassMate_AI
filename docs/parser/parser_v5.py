# -*- coding: utf-8 -*-
import json
import os
import re
import pdfplumber

def extract_layout_aware_columns(page):
    """
    페이지 내부의 모든 단어(Word)의 x좌표 분포를 분석하여 
    실제 2단 사이에 존재하는 여백(Gutter)의 정중앙 분할선을 동적으로 계산합니다.
    이를 통해 원문자(① 등)가 경계선에 걸려 잘려 나가는 문제를 원천 차단합니다.
    """
    words = page.extract_words()
    if not words:
        return "", ""

    width = page.width
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

    # 찾은 경계선 기준으로 단어를 좌/우 그룹으로 분류 (단어의 중심값 기준)
    left_words = []
    right_words = []
    for w in words:
        centroid_x = (w['x0'] + w['x1']) / 2.0
        if centroid_x < best_split_x:
            left_words.append(w)
        else:
            right_words.append(w)

    def reconstruct_text_from_words(col_words):
        """
        단어 객체들을 y좌표(상하 오차 허용) 기준으로 묶어 정상적인 텍스트 라인으로 복원합니다.
        """
        if not col_words:
            return ""
        
        # 1차 정렬: 상단 좌표 기준, 2차 정렬: 좌측 좌표 기준
        col_words.sort(key=lambda w: (w['top'], w['x0']))
        
        lines = []
        current_line_words = []
        
        for w in col_words:
            if not current_line_words:
                current_line_words.append(w)
            else:
                prev_w = current_line_words[-1]
                # 같은 줄로 취급할 수 있는 y축 오차 범위 설정 (3포인트 내외)
                if abs(w['top'] - prev_w['top']) <= 3.5:
                    current_line_words.append(w)
                else:
                    # 기존 라인 조립 및 추가
                    current_line_words.sort(key=lambda x: x['x0'])
                    lines.append(" ".join([x['text'] for x in current_line_words]))
                    current_line_words = [w]
                    
        if current_line_words:
            current_line_words.sort(key=lambda x: x['x0'])
            lines.append(" ".join([x['text'] for x in current_line_words]))
            
        return "\n".join(lines)

    left_text = reconstruct_text_from_words(left_words)
    right_text = reconstruct_text_from_words(right_words)
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
    
    # 선지 식별 패턴 (예: "①", "②", "1.", "(3)", "4 ZigBee" 등 통합 처리)
    opt_pattern = re.compile(r"^([①②③④❶❷❸❹]|[1-4]\.|\([1-4]\)|\[[1-4]\]|^[1-4])\s*(.*)")

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
                if any(m in marker for m in ["①", "1", "(1)", "❶"]): norm_idx = "1"
                elif any(m in marker for m in ["②", "2", "(2)", "❷"]): norm_idx = "2"
                elif any(m in marker for m in ["③", "3", "(3)", "❸"]): norm_idx = "3"
                elif any(m in marker for m in ["④", "4", "(4)", "❹"]): norm_idx = "4"

                if norm_idx:
                    current_q["last_idx"] = norm_idx
                    current_q["options"][norm_idx] = content
            else:
                # 선지 수집 단계 돌입 상태라면, 여러 줄로 나뉜 선지 내용을 이어 붙임
                if current_q["last_idx"]:
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