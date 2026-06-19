import json
import os
import re
from ollama import chat

# 분류 대상 과목과 그에 속한 세부 영역(후보군)을 정의합니다.
SUBJECTS = {
    "컴퓨터일반": [
        "컴퓨터구조", "운영체제", "데이터베이스", "자료 구조", 
        "프로그래밍 언어론", "소프트웨어 공학 및 시스템 설계", 
        "데이터 통신과 네트워크", "인터넷 및 최신 기술 용어"
    ],
    "운전면허": [
        "교통법규", "안전운전", "도로표지", "응급처치", "차량관리"
    ]
}

class ExamClassifier:
    """Ollama 로컬 모델을 사용하여 기출문제를 단계적으로 분류하고 검증하는 클래스입니다."""
    
    def __init__(self, model="exaone3.5:2.4b"): 
        self.model = model

    def clean_response(self, text):
        """모델이 생성한 코드 블록이나 불필요한 마크다운을 제거하여 순수 텍스트만 추출합니다."""
        cleaned = re.sub(r'```[\s\S]*?```', '', text)
        return cleaned.strip()

    def get_llm_response(self, system_prompt, user_prompt):
        """Ollama 모델로부터 응답을 받는 함수로, 제약사항을 강제합니다."""
        strict_system_prompt = (
            f"{system_prompt} DO NOT generate code, explanations, or markdown. Return ONLY the requested value."
        )
        res = chat(model=self.model, messages=[
            {"role": "system", "content": strict_system_prompt},
            {"role": "user", "content": user_prompt}
        ])
        return self.clean_response(res['message']['content'])

    def classify(self, question_text):
        """문제 텍스트를 입력받아 과목/영역을 분류하고 검증하는 파이프라인입니다."""
        
        # 1단계: 과목 분류 (후보군 제한)
        subject_candidates = list(SUBJECTS.keys())
        subject_prompt = f"Question: {question_text}\nChoose subject from: {subject_candidates}. Return ONLY subject name."
        subject = self.get_llm_response("You are a strict classifier.", subject_prompt)
        
        # [방어 코드] 모델이 정의되지 않은 과목으로 분류 시 기본값 설정
        if subject not in SUBJECTS:
            subject = "컴퓨터일반"
            
        # 2단계: 영역 분류 (선택된 과목의 하위 영역으로 후보군 제한)
        area_candidates = SUBJECTS.get(subject, ["기타"])
        area_prompt = f"Subject: {subject}\nQuestion: {question_text}\nChoose area from: {area_candidates}. Return ONLY area name."
        area = self.get_llm_response("You are a strict classifier.", area_prompt)
        
        # 3단계: 자기 검증
        verify_prompt = f"Question: {question_text}\nSubject: {subject}\nArea: {area}\nIs this classification logically correct? Answer YES or NO."
        verification = self.get_llm_response("Answer only YES or NO.", verify_prompt)
        
        return {"subject": subject, "area": area, "verification": verification}

def process_exam_files(input_dir, output_dir):
    """지정된 디렉토리의 JSON 파일을 순회하며 분류 작업을 수행합니다."""
    classifier = ExamClassifier()
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    files = [f for f in os.listdir(input_dir) if f.endswith(".json")]
    
    for filename in files:
        print(f"[*] 처리 중: {filename}")
        file_path = os.path.join(input_dir, filename)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            items = data if isinstance(data, list) else [data]
            
            for item in items:
                q_text = item.get("question", "")
                if q_text:
                    # 원본 데이터를 수정하지 않고 새로운 분류 결과만 업데이트합니다.
                    result = classifier.classify(q_text)
                    item.update(result)
            
            output_path = os.path.join(output_dir, f"classified_{filename}")
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
    print("\n[*] 모든 작업이 완료되었습니다.")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_directory = os.path.join(base_dir, "data", "input")
    output_directory = os.path.join(base_dir, "data", "output")
    
    if not os.path.exists(input_directory):
        os.makedirs(input_directory)
    else:
        process_exam_files(input_directory, output_directory)