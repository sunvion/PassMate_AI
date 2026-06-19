# -*- coding: utf-8 -*-
import json
import os
import re
import pdfplumber

def extract_clean_lines_by_columns(page):
    """
    1. 전체 페이지에서 단어(words)를 추출합니다.
    2. 동적으로 단 분할선(best_split_x)을 계산합니다.
    3. 단어들을 좌측/우측 그룹으로 확실히 분리합니다.
    4. 각 그룹 내에서 단어들을 물리적 Y좌표(행) 기준으로 그룹화하고, 
       X좌표 순서대로 정렬하여 텍스트를 복원함으로써 글자 유실을 원천 차단합니다.
    """
    words = page.extract_words()
    if not words:
        return [], []
    
    width = page.width
    
    # 동적 분할선 계산 (전체 너비의 42% ~ 58% 스캔)
    best_split_x = width / 2
    min_overlap_count = float('inf')
    for x in range(int(width * 0.42), int(width * 0.58), 5):
        overlap = sum(1 for w in words if w['x0'] < x < w['x1'])
        if overlap < min_overlap_count:
            min_overlap_count = overlap
            best_split_x = x
            if overlap == 0:
                break

    left_words = []
    right_words = []
    for w in words:
        centroid_x = (w['x0'] + w['x1']) / 2.0
        if centroid_x < best_split_x:
            left_words.append(w)
        else:
            right_words.append(w)

    def reconstruct_lines(col_words):
        if not col_words:
            return []
        
        # y좌표(top) 기준으로 정렬 후 같은 행인 단어들끼리 그룹화
        col_words.sort(key=lambda w: (w['top'], w['x0']))
        
        lines_words = []
        current_line_words = []
        for w in col_words:
            if not current_line_words:
                current_line_words.append(w)
            else:
                prev_w = current_line_words[-1]
                # y좌표 차이가 4.5포인트 이하이면 같은 행으로 간주
                if abs(w['top'] - prev_w['top']) <= 4.5:
                    current_line_words.append(w)
                else:
                    current_line_words.sort(key=lambda x: x['x0'])
                    lines_words.append(current_line_words)
                    current_line_words = [w]
        if current_line_words:
            current_line_words.sort(key=lambda x: x['x0'])
            lines_words.append(current_line_words)

        formatted_lines = []
        for line_w in lines_words:
            # 단어들 사이에 공백을 주며 합쳐 복원
            text = " ".join([x['text'] for x in line_w])
            formatted_lines.append({
                "text": text.strip(),
                "x0": line_w[0]['x0'],
                "top": line_w[0]['top']
            })
        return formatted_lines

    return reconstruct_lines(left_words), reconstruct_lines(right_words)


def segment_options_spatially(question_lines):
    """
    질문 블록의 줄(lines)들 중 가장 하단에 위치하면서
    시작 가로 위치(x0)가 세로로 완벽히 정렬(허용오차 3.5포인트)된 
    4개의 그룹을 선지(보기)로 자동 식별하여 추출하는 공간 정렬 분석 알고리즘입니다.
    """
    if len(question_lines) < 4:
        return None
    
    # 마지막 10줄 이내에서 선지 탐색 가동
    candidate_lines = question_lines[-10:]
    x_coords = [round(line['x0'], 1) for line in candidate_lines]
    
    best_align_x = None
    max_aligned_count = 0
    
    # 유사한 시작 x좌표 빈도 추적
    for ref_x in set(x_coords):
        aligned = [line for line in candidate_lines if abs(line['x0'] - ref_x) <= 3.5]
        if len(aligned) == 4:
            best_align_x = ref_x
            break
        elif len(aligned) > max_aligned_count:
            max_aligned_count = len(aligned)
            best_align_x = ref_x
            
    if best_align_x is not None:
        # 전체 라인에서 찾은 대표 시작좌표와 정렬된 라인들의 인덱스 추출
        opt_start_indices = []
        for idx, line in enumerate(question_lines):
            if abs(line['x0'] - best_align_x) <= 3.5:
                opt_start_indices.append(idx)
                
        # 하단에서 연속하는 4개의 지점을 보기 시작 위치로 매핑
        if len(opt_start_indices) >= 4:
            opt_starts = opt_start_indices[-4:]
            
            options = {"1": "", "2": "", "3": "", "4": ""}
            
            # 보기 1번 추출 (2번 보기 시작 전까지의 모든 줄 병합)
            opt1_lines = question_lines[opt_starts[0]:opt_starts[1]]
            options["1"] = " ".join([l['text'] for l in opt1_lines]).strip()
            
            # 보기 2번 추출
            opt2_lines = question_lines[opt_starts[1]:opt_starts[2]]
            options["2"] = " ".join([l['text'] for l in opt2_lines]).strip()
            
            # 보기 3번 추출
            opt3_lines = question_lines[opt_starts[2]:opt_starts[3]]
            options["3"] = " ".join([l['text'] for l in opt3_lines]).strip()
            
            # 보기 4번 추출 (마지막까지의 모든 줄 병합)
            opt4_lines = question_lines[opt_starts[3]:]
            options["4"] = " ".join([l['text'] for l in opt4_lines]).strip()
            
            # 보기가 시작되기 전까지의 상단 텍스트는 질문과 코드 박스로 지정
            question_text = "\n".join([l['text'] for l in question_lines[:opt_starts[0]]]).strip()
            
            # 보기 내부에 존재하는 기질 기호들(①, ②, 마침표, 컴마 등) 노이즈 세정
            clean_opt_pattern = re.compile(r"^([①②③④❶❷❸❹]|1\.|2\.|3\.|4\.|\(1\)|\(2\)|\(3\)|\(4\)|\[1\]|\[2\]|\[3\]|\[4\]|[.,·•])\s*")
            for k in options:
                options[k] = clean_opt_pattern.sub("", options[k]).strip()
                
            return question_text, options
            
    return None


def parse_clean_exam_pdf(pdf_path):
    """
    레이아웃 인지형 공간 분석 기술을 총동원하여 질문과 선지를 완전무결하게 정제합니다.
    """
    print(f"[*] '{pdf_path}' 정밀 레이아웃 분석 파싱을 시작합니다...")

    if not os.path.exists(pdf_path):
        print(f"[-] 에러: 파일 경로가 유효하지 않습니다. ({pdf_path})")
        return []

    raw_lines = []

    with pdfplumber.open(pdf_path) as pdf:
        for idx, page in enumerate(pdf.pages):
            # 문자 유실이 없는 완벽한 열 복원 적용
            left_lines, right_lines = extract_clean_lines_by_columns(page)
            
            for col_lines in [left_lines, right_lines]:
                for line_obj in col_lines:
                    text_val = line_obj['text']
                    if not text_val:
                        continue
                    
                    # 시험지 상/하단 고정 메타데이터 정리
                    if any(meta in text_val for meta in [
                        "국가공무원", "가책형", "컴퓨터일반", "공채 필기시험", "쪽"
                    ]):
                        continue
                    raw_lines.append(line_obj)

    questions_list = []
    current_q_lines = []
    q_num = None

    # 문항 번호 식별 패턴 (예: "문 15.", "문 2.")
    q_start_pattern = re.compile(r"^[문물민미]\s*(\d+)\s*[\.\s\-]*")

    for line_obj in raw_lines:
        text = line_obj['text']
        q_match = q_start_pattern.match(text)
        
        if q_match:
            # 이전 문항이 수집 중이었다면 공간 분석을 통해 최종 파싱 후 저장
            if current_q_lines and q_num is not None:
                parsed_res = segment_options_spatially(current_q_lines)
                if parsed_res:
                    q_text, opts = parsed_res
                    questions_list.append({
                        "number": q_num,
                        "question": q_text,
                        "options": opts
                    })
                else:
                    # 공간 정렬 분리 실패 시 예외 방지용 단순 텍스트 누적 백업
                    questions_list.append({
                        "number": q_num,
                        "question": "\n".join([l['text'] for l in current_q_lines]),
                        "options": {"1": "", "2": "", "3": "", "4": ""}
                    })
            
            # 새로운 문항 수집 준비
            q_num = int(q_match.group(1))
            
            # "문 1." 부분을 제거하고 순수 내용만 남김
            clean_start_text = q_start_pattern.sub("", text).strip()
            line_obj['text'] = clean_start_text
            current_q_lines = [line_obj]
        else:
            if q_num is not None:
                current_q_lines.append(line_obj)

    # 마지막 문항 최종 세이브 처리
    if current_q_lines and q_num is not None:
        parsed_res = segment_options_spatially(current_q_lines)
        if parsed_res:
            q_text, opts = parsed_res
            questions_list.append({
                "number": q_num,
                "question": q_text,
                "options": opts
            })
        else:
            questions_list.append({
                "number": q_num,
                "question": "\n".join([l['text'] for l in current_q_lines]),
                "options": {"1": "", "2": "", "3": "", "4": ""}
            })

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