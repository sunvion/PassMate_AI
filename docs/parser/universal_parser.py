# -*- coding: utf-8 -*-
import json
import os
import re
import argparse
import pdfplumber

def extract_clean_lines_by_columns(page, is_double_column=True):
    """
    페이지 내부의 단어(Word) 정보를 추출하여, 
    2단 레이아웃인 경우 동적으로 분할선을 계산하여 좌우 단으로 정교하게 분리합니다.
    Y좌표 오차가 적은 단어들을 라인으로 복원하여 문자 유실을 원천 방지합니다.
    """
    words = page.extract_words()
    if not words:
        return []
    
    width = page.width
    height = page.height
    
    # 2단 여부 동적 감지
    best_split_x = width / 2
    if is_double_column:
        min_overlap_count = float('inf')
        # 페이지 가로의 42% ~ 58% 영역을 스캔하여 글자가 가로지르지 않는 최적의 빈 여백(Gutter) 축색
        for x in range(int(width * 0.42), int(width * 0.58), 4):
            overlap = sum(1 for w in words if w['x0'] < x < w['x1'])
            if overlap < min_overlap_count:
                min_overlap_count = overlap
                best_split_x = x
                if overlap == 0:
                    break
        # 만약 여백 경계에 걸쳐진 글자가 너무 많다면(단일 단 시험지인 경우), 단 분할을 해제함
        if min_overlap_count > len(words) * 0.1:
            is_double_column = False

    left_words = []
    right_words = []
    
    if is_double_column:
        for w in words:
            centroid_x = (w['x0'] + w['x1']) / 2.0
            if centroid_x < best_split_x:
                left_words.append(w)
            else:
                right_words.append(w)
    else:
        left_words = words

    def reconstruct_lines(col_words):
        if not col_words:
            return []
        
        # Y좌표(top) 순으로 정렬 후 X좌표 정렬
        col_words.sort(key=lambda w: (w['top'], w['x0']))
        
        lines_words = []
        current_line_words = []
        for w in col_words:
            if not current_line_words:
                current_line_words.append(w)
            else:
                prev_w = current_line_words[-1]
                # Y축 오차가 4.5포인트 이하인 경우 같은 물리적 라인으로 간주
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
            text = " ".join([x['text'] for x in line_w]).strip()
            if text:
                formatted_lines.append({
                    "text": text,
                    "x0": line_w[0]['x0'],
                    "top": line_w[0]['top']
                })
        return formatted_lines

    left_lines = reconstruct_lines(left_words)
    right_lines = reconstruct_lines(right_words)
    return left_lines + right_lines


def segment_options_spatially(question_lines):
    """
    공간/좌표 분석 Fallback:
    가장 하단에 있으면서 가로 위치(x0)가 세로로 유사하게 정렬된 4개 줄을 찾아 선지(보기)로 분리합니다.
    """
    if len(question_lines) < 4:
        return None
    
    candidate_lines = question_lines[-10:]
    x_coords = [round(line['x0'], 1) for line in candidate_lines]
    
    best_align_x = None
    max_aligned_count = 0
    for ref_x in set(x_coords):
        aligned = [line for line in candidate_lines if abs(line['x0'] - ref_x) <= 4.0]
        if len(aligned) == 4:
            best_align_x = ref_x
            break
        elif len(aligned) > max_aligned_count:
            max_aligned_count = len(aligned)
            best_align_x = ref_x
            
    if best_align_x is not None:
        opt_start_indices = []
        for idx, line in enumerate(question_lines):
            if abs(line['x0'] - best_align_x) <= 4.0:
                opt_start_indices.append(idx)
                
        if len(opt_start_indices) >= 4:
            opt_starts = opt_start_indices[-4:]
            
            options = {"1": "", "2": "", "3": "", "4": ""}
            options["1"] = " ".join([l['text'] for l in question_lines[opt_starts[0]:opt_starts[1]]]).strip()
            options["2"] = " ".join([l['text'] for l in question_lines[opt_starts[1]:opt_starts[2]]]).strip()
            options["3"] = " ".join([l['text'] for l in question_lines[opt_starts[2]:opt_starts[3]]]).strip()
            options["4"] = " ".join([l['text'] for l in question_lines[opt_starts[3]:]]).strip()
            
            question_text = "\n".join([l['text'] for l in question_lines[:opt_starts[0]]]).strip()
            return question_text, options
            
    return None


def extract_options_hybrid(question_lines):
    """
    정규식(가로/세로 매칭) + 종결성 기반 라인 병합 + 공간 분석 + 강제 분할을 결합한 하이브리드 보기 추출 알고리즘입니다.
    """
    # 보기 넘버링 마커 정의
    opt_pattern = re.compile(
        r"([①②③④❶❷❸❹]|1\.|2\.|3\.|4\.|\(1\)|\(2\)|\(3\)|\(4\)|\[1\]|\[2\]|\[3\]|\[4\])"
    )
    
    def get_norm_idx(marker):
        if marker in ["①", "1.", "(1)", "[1]", "❶", "1"]: return "1"
        if marker in ["②", "2.", "(2)", "[2]", "❷", "2"]: return "2"
        if marker in ["③", "3.", "(3)", "[3]", "❸", "3"]: return "3"
        if marker in ["④", "4.", "(4)", "[4]", "❹", "4"]: return "4"
        return None

    # ----------------------------------------------------
    # Step 1: 기호 기반 텍스트 스캔 & 매핑
    # ----------------------------------------------------
    options = {"1": "", "2": "", "3": "", "4": ""}
    question_text_parts = []
    current_opt_idx = None
    
    for line_obj in question_lines:
        line_text = line_obj['text']
        matches = list(opt_pattern.finditer(line_text))
        
        if matches:
            prev_end = 0
            for idx, match in enumerate(matches):
                marker = match.group(1)
                norm_idx = get_norm_idx(marker)
                
                fragment = line_text[prev_end:match.start()].strip()
                if fragment:
                    if current_opt_idx:
                        options[current_opt_idx] += " " + fragment
                    else:
                        question_text_parts.append(fragment)
                
                if norm_idx:
                    current_opt_idx = norm_idx
                prev_end = match.end()
            
            last_fragment = line_text[prev_end:].strip()
            if last_fragment:
                if current_opt_idx:
                    options[current_opt_idx] += " " + last_fragment
                else:
                    question_text_parts.append(last_fragment)
        else:
            if current_opt_idx:
                options[current_opt_idx] += "\n" + line_text
            else:
                question_text_parts.append(line_text)

    is_success = all(options[k].strip() != "" for k in ["1", "2", "3", "4"])
    
    if is_success:
        question_text = "\n".join(question_text_parts).strip()
        clean_marker_pattern = re.compile(r"^([①②③④❶❷❸❹]|1\.|2\.|3\.|4\.|\(1\)|\(2\)|\(3\)|\(4\)|\[1\]|\[2\]|\[3\]|\[4\]|[.,·•\-\s])\s*")
        for k in options:
            options[k] = clean_marker_pattern.sub("", options[k].strip()).strip()
        return question_text, options

    # ----------------------------------------------------
    # Step 2: 종결성 기반 라인 병합 및 보기 분할 (Heuristic)
    # ----------------------------------------------------
    # 보기로 예상되는 정렬된 영역(align_x)을 탐색
    candidate_lines = question_lines[-10:]
    x_coords = [round(line['x0'], 1) for line in candidate_lines]
    
    best_align_x = None
    max_aligned_count = 0
    for ref_x in set(x_coords):
        aligned = [line for line in candidate_lines if abs(line['x0'] - ref_x) <= 4.0]
        if len(aligned) > max_aligned_count:
            max_aligned_count = len(aligned)
            best_align_x = ref_x
            
    if best_align_x is not None:
        first_opt_idx = None
        for idx, line in enumerate(question_lines):
            if abs(line['x0'] - best_align_x) <= 4.0:
                first_opt_idx = idx
                break
                
        if first_opt_idx is not None and len(question_lines) - first_opt_idx >= 4:
            # 원본 손상을 막기 위해 깊은 복사 개념 적용
            opt_area_lines = [{"text": l['text'], "x0": l['x0'], "top": l['top']} for l in question_lines[first_opt_idx:]]
            
            # 한국어 미완결 어미/조사 패턴
            incomplete_pattern = re.compile(
                r".*(?:[을를은는이가의에와과로고며]|에서|하고|하여|해서|으로|대한|사용한|공용|속도가|있어서|않아서|이어서|되어서|되므로|이므로|않은|옳은|없는|있고|없고|전원이|않는|등이|같을|동일한|사용하는)$"
            )
            
            merged_opt_lines = []
            i = 0
            while i < len(opt_area_lines):
                line = opt_area_lines[i]
                # 현재 줄이 미완결 패턴으로 끝나면 다음 줄과 강제 결합
                while i < len(opt_area_lines) - 1 and incomplete_pattern.match(opt_area_lines[i]['text']):
                    opt_area_lines[i+1]['text'] = opt_area_lines[i]['text'] + " " + opt_area_lines[i+1]['text']
                    i += 1
                    line = opt_area_lines[i]
                merged_opt_lines.append(line)
                i += 1
                
            # 병합 결과가 정확히 4개라면 보기 1~4 매핑 기용
            if len(merged_opt_lines) == 4:
                options = {
                    "1": merged_opt_lines[0]['text'],
                    "2": merged_opt_lines[1]['text'],
                    "3": merged_opt_lines[2]['text'],
                    "4": merged_opt_lines[3]['text']
                }
                question_text = "\n".join([l['text'] for l in question_lines[:first_opt_idx]]).strip()
                clean_marker_pattern = re.compile(r"^([①②③④❶❷❸❹]|1\.|2\.|3\.|4\.|\(1\)|\(2\)|\(3\)|\(4\)|\[1\]|\[2\]|\[3\]|\[4\]|[.,·•\-\s])\s*")
                for k in options:
                    options[k] = clean_marker_pattern.sub("", options[k].strip()).strip()
                return question_text, options

    # ----------------------------------------------------
    # Step 3: 공간/좌표 기반 분석 Fallback
    # ----------------------------------------------------
    spatial_res = segment_options_spatially(question_lines)
    if spatial_res:
        q_text, opts = spatial_res
        clean_marker_pattern = re.compile(r"^([step1①②③④❶❷❸❹]|1\.|2\.|3\.|4\.|\(1\)|\(2\)|\(3\)|\(4\)|\[1\]|\[2\]|\[3\]|\[4\]|[.,·•\-\s])\s*")
        for k in opts:
            opts[k] = clean_marker_pattern.sub("", opts[k].strip()).strip()
        return q_text, opts

    # ----------------------------------------------------
    # Step 4: 강제 4분할 Fallback
    # ----------------------------------------------------
    if len(question_lines) >= 4:
        options = {
            "1": question_lines[-4]['text'],
            "2": question_lines[-3]['text'],
            "3": question_lines[-2]['text'],
            "4": question_lines[-1]['text']
        }
        question_text = "\n".join([l['text'] for l in question_lines[:-4]]).strip()
        clean_marker_pattern = re.compile(r"^([①②③④❶❷❸❹]|1\.|2\.|3\.|4\.|\(1\)|\(2\)|\(3\)|\(4\)|\[1\]|\[2\]|\[3\]|\[4\]|[.,·•\-\s])\s*")
        for k in options:
            options[k] = clean_marker_pattern.sub("", options[k].strip()).strip()
        return question_text, options

    return "\n".join([l['text'] for l in question_lines]).strip(), {"1": "", "2": "", "3": "", "4": ""}


def parse_exam_pdf(pdf_path, is_double_column=True, use_korean_marker=True):
    """
    PDF 시험지를 구조화된 JSON 데이터로 파싱하여 리턴합니다.
    """
    print(f"[*] '{pdf_path}' 레이아웃 정교 분석 파싱을 기동합니다...")
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF 파일을 찾을 수 없습니다: {pdf_path}")

    raw_lines = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_lines = extract_clean_lines_by_columns(page, is_double_column)
            for line_obj in page_lines:
                text_val = line_obj['text']
                # 시험지 상/하단 고정 메타데이터 필터링
                if any(meta in text_val for meta in [
                    "국가공무원", "가책형", "컴퓨터일반", "공채 필기시험", "쪽", "PAGE"
                ]):
                    continue
                raw_lines.append(line_obj)

    questions_list = []
    current_q_lines = []
    q_num = None
    
    # 문항 식별 패턴 설정
    # use_korean_marker=True 이면 접두사 [문물민미]가 필수로 붙은 행만 문항 시작으로 판단
    if use_korean_marker:
        q_start_pattern = re.compile(r"^([문물민미]\s*)(\d+)\s*[\.\s\-]+")
    else:
        # 접두사 없이 숫자만 있는 경우 (3자리 이상 큰 수 거르고, 소수점은 거름)
        q_start_pattern = re.compile(r"^(?!\d{3,})(?!\d+\.\d+)(\d+)\s*[\.\s\-]+")

    for line_obj in raw_lines:
        text = line_obj['text']
        q_match = q_start_pattern.match(text)
        
        if q_match:
            # 이전 수집 문항이 있다면 파싱 처리 후 목록에 추가
            if current_q_lines and q_num is not None:
                q_text, opts = extract_options_hybrid(current_q_lines)
                questions_list.append({
                    "number": q_num,
                    "question": q_text,
                    "options": opts
                })
            
            # 신규 문항 설정
            # use_korean_marker 여부에 따라 매치 그룹 인덱스 조정
            match_group_idx = 2 if use_korean_marker else 1
            q_num = int(q_match.group(match_group_idx))
            clean_start_text = q_start_pattern.sub("", text).strip()
            line_obj['text'] = clean_start_text
            current_q_lines = [line_obj]
        else:
            if q_num is not None:
                current_q_lines.append(line_obj)

    # 마지막 문항 마무리 처리
    if current_q_lines and q_num is not None:
        q_text, opts = extract_options_hybrid(current_q_lines)
        questions_list.append({
            "number": q_num,
            "question": q_text,
            "options": opts
        })

    # 중복 제거 및 문항 정렬 보증
    # 동일 문항 번호가 여러 개 감지될 경우 첫 번째 것을 기용하거나 정돈
    unique_questions = {}
    for q in questions_list:
        n = q["number"]
        if n not in unique_questions:
            unique_questions[n] = q
        else:
            # 지문 내용이 더 긴 것을 병합 또는 채택
            if len(q["question"]) > len(unique_questions[n]["question"]):
                unique_questions[n] = q
                
    final_sorted_list = sorted(unique_questions.values(), key=lambda x: x["number"])
    return final_sorted_list


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Universal Layout-Aware Exam PDF Parser")
    parser.add_argument("--input", required=True, help="Path to target exam PDF file")
    parser.add_argument("--output", required=True, help="Path to output JSON file")
    parser.add_argument("--single-column", action="store_true", help="Set to parse single-column layouts (like driver's license)")
    parser.add_argument("--korean-marker", action="store_true", default=False, help="Require Korean prefix (문, 물 등) for questions (recommended for civil service exams)")
    
    args = parser.parse_args()
    
    try:
        results = parse_exam_pdf(args.input, is_double_column=not args.single_column, use_korean_marker=args.korean_marker)
        
        # 저장 디렉토리 자동 생성
        output_dir = os.path.dirname(args.output)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
            
        print(f"\n[+] 파싱 프로세스 완벽 성공!")
        print(f"[+] 총 {len(results)}개 문항이 구조화되어 '{args.output}'에 보존되었습니다.")
        
        # 간단 품질 검수 로그 출력
        empty_opts_count = 0
        for r in results:
            opts_valid = all(v.strip() != "" for v in r["options"].values())
            if not opts_valid:
                empty_opts_count += 1
                print(f"[-] 경고: 문항 {r['number']}번의 보기가 온전하지 않습니다.")
                
        if empty_opts_count == 0:
            print("[+] 품질 검사 결과: 100% 무손실 보기 분리 완성!")
        else:
            print(f"[-] 품질 검사 결과: 전체 {len(results)}개 중 {empty_opts_count}개 문항 보기 분리 불완전.")
            
    except Exception as e:
        print(f"[-] 치명적 파싱 장해 발생: {e}")
