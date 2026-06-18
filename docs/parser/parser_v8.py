# -*- coding: utf-8 -*-
import json
import os
import re
import pdfplumber

def extract_clean_lines_by_columns(page):
    """문자 유실 없이 페이지를 좌/우로 분할하여 라인 단위로 추출합니다."""
    words = page.extract_words()
    if not words:
        return [], []
    
    width = page.width
    best_split_x = width / 2
    min_overlap_count = float('inf')
    
    # 동적 분할선 계산
    for x in range(int(width * 0.42), int(width * 0.58), 5):
        overlap = sum(1 for w in words if w['x0'] < x < w['x1'])
        if overlap < min_overlap_count:
            min_overlap_count = overlap
            best_split_x = x
            if overlap == 0: break

    left_words, right_words = [], []
    for w in words:
        if (w['x0'] + w['x1']) / 2.0 < best_split_x:
            left_words.append(w)
        else:
            right_words.append(w)

    def reconstruct_lines(col_words):
        if not col_words: return []
        col_words.sort(key=lambda w: (w['top'], w['x0']))
        lines_words = []
        current_line_words = []
        for w in col_words:
            if not current_line_words:
                current_line_words.append(w)
            elif abs(w['top'] - current_line_words[-1]['top']) <= 4.5:
                current_line_words.append(w)
            else:
                current_line_words.sort(key=lambda x: x['x0'])
                lines_words.append(current_line_words)
                current_line_words = [w]
        if current_line_words:
            current_line_words.sort(key=lambda x: x['x0'])
            lines_words.append(current_line_words)
        
        return [{"text": " ".join([x['text'] for x in lw]).strip(), "x0": lw[0]['x0'], "top": lw[0]['top']} for lw in lines_words]

    return reconstruct_lines(left_words), reconstruct_lines(right_words)

def segment_options_hybrid(question_lines):
    # [수정] 점(.)이나 기호로 시작하는 모든 경우를 포함하도록 정규식 확장
    # ^(\.|[①-④]|[1-4]\.|\([1-4]\))\s+ 패턴 추가
    pattern = re.compile(r'^(?:\.|[①②③④]|[1-4]\.|\([1-4]\)|\[[1-4]\])\s*')
    
    # ... (중략: 패턴 매칭 로직 유지) ...
    # 만약 위 패턴으로 4개가 찾아진다면 사용하고, 안되면 공간 분석으로 진입
    
    return segment_options_spatially(question_lines)

def segment_options_spatially(question_lines):
    """
    공간 분석 강화를 위해 허용 오차를 늘리고, 
    4개 미만으로 감지되더라도 강제로 4등분을 시도하는 로직을 추가합니다.
    """
    # 1. 기존의 좌표 기반 정렬 시도 (유지)
    # ... (기존 로직) ...
    
    # 2. [추가] 좌표로 실패했을 경우, 단순히 '줄 개수'를 이용한 강제 분할 전략 (Fallback)
    # 문항 전체가 4개 이상의 줄로 구성되어 있다면, 적어도 보기 4개는 있다고 가정
    if len(question_lines) >= 4:
        # 마지막 4줄을 보기로 강제 매핑
        idx = [-4, -3, -2, -1] 
        options = {
            "1": question_lines[-4]['text'],
            "2": question_lines[-3]['text'],
            "3": question_lines[-2]['text'],
            "4": " ".join([l['text'] for l in question_lines[-1:]]) # 마지막 줄은 길 수 있음
        }
        question_text = "\n".join([l['text'] for l in question_lines[:-4]]).strip()
        return question_text, options
        
    return None

def segment_options_spatially(question_lines):
    """공간 좌표 기반의 전통적인 선지 분할 (백업)"""
    if len(question_lines) < 4: return None
    
    x_coords = [round(line['x0'], 1) for line in question_lines[-10:]]
    best_align_x = None
    max_aligned = 0
    
    for ref_x in set(x_coords):
        aligned = [line for line in question_lines[-10:] if abs(line['x0'] - ref_x) <= 3.5]
        if len(aligned) >= 3: # 최소 3개 이상 정렬되면 기준으로 삼음
            best_align_x = ref_x
            break
            
    if best_align_x is not None:
        opt_starts = [i for i, line in enumerate(question_lines) if abs(line['x0'] - best_align_x) <= 3.5]
        if len(opt_starts) >= 4:
            idx = opt_starts[-4:]
            options = {
                "1": " ".join([l['text'] for l in question_lines[idx[0]:idx[1]]]),
                "2": " ".join([l['text'] for l in question_lines[idx[1]:idx[2]]]),
                "3": " ".join([l['text'] for l in question_lines[idx[2]:idx[3]]]),
                "4": " ".join([l['text'] for l in question_lines[idx[3]:]])
            }
            question_text = "\n".join([l['text'] for l in question_lines[:idx[0]]]).strip()
            return question_text, options
    return None

def parse_clean_exam_pdf(pdf_path):
    print(f"[*] '{pdf_path}' 분석 시작...")
    raw_lines = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            left, right = extract_clean_lines_by_columns(page)
            for col in [left, right]:
                for line in col:
                    if any(m in line['text'] for m in ["국가공무원", "가책형", "쪽"]): continue
                    raw_lines.append(line)

    questions_list = []
    current_q_lines = []
    q_num = None
    q_pattern = re.compile(r"^[문물]\s*(\d+)")

    for line in raw_lines:
        match = q_pattern.match(line['text'])
        if match:
            if current_q_lines:
                res = segment_options_hybrid(current_q_lines)
                if res:
                    q_text, opts = res
                    questions_list.append({"number": q_num, "question": q_text, "options": opts})
            
            q_num = int(match.group(1))
            line['text'] = q_pattern.sub("", line['text']).strip()
            current_q_lines = [line]
        elif q_num:
            current_q_lines.append(line)

    # 마지막 문항 처리
    if current_q_lines:
        res = segment_options_hybrid(current_q_lines)
        if res:
            q_text, opts = res
            questions_list.append({"number": q_num, "question": q_text, "options": opts})
            # ... (함수 끝부분 리턴 직전) ...
    
            # 누락된 번호 확인 (디버깅)
            parsed_nums = [q['number'] for q in questions_list]
            all_nums = list(range(1, 21)) # 1~20번 문제라고 가정
            missing = [n for n in all_nums if n not in parsed_nums]
            if missing:
                print(f"[-] 경고: 다음 문항 파싱 실패: {missing}")
    
            return sorted(questions_list, key=lambda x: x["number"])

    return sorted(questions_list, key=lambda x: x["number"])

if __name__ == "__main__":
    # 파일명 변경 필요시 여기 수정
    target_exam = "컴퓨터일반-가.pdf"
    try:
        final_data = parse_clean_exam_pdf(target_exam)
        with open("parsed_result.json", "w", encoding="utf-8") as f:
            json.dump(final_data, f, ensure_ascii=False, indent=4)
        print(f"[+] 성공: {len(final_data)} 문항 저장 완료.")
    except Exception as e:
        print(f"[-] 에러: {e}")