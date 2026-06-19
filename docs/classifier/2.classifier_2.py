import json
import os
import re
from ollama import chat

# AI가 선택할 수 있는 범위를 명확히 고정하여 엉뚱한 과목으로 분류되는 것을 방지합니다.
SUBJECTS = {
    "국가직 9급 컴퓨터일반": [
        "컴퓨터구조", "운영체제", "데이터베이스", "자료 구조", 
        "프로그래밍 언어론", "소프트웨어 공학 및 시스템 설계", 
        "데이터 통신과 네트워크", "인터넷 및 최신 기술 용어"
    ],
    "운전면허": [
        "교통법규", "안전운전", "도로표지", "응급처치", "차량관리"
    ]
}

class ExamClassifier:
    """
    Ollama 로컬 모델을 사용하여 기출문제를 분류하고 검증하는 클래스입니다.
    """
    
    def __init__(self, model="qwen2.5:1.5b"): 
        self.model = model

    def clean_response(self, text):
        # LLM이 생성하는 마크다운 코드 블록(```)이나 불필요한 공백을 정규식으로 제거합니다.
        cleaned = re.sub(r'```[\s\S]*?```', '', text)
        return cleaned.strip()

    def get_llm_response(self, system_prompt, user_prompt):
        # 'DO NOT generate code' 지시사항을 시스템 프롬프트에 강력하게 주입합니다.
        strict_system_prompt = (
            f"{system_prompt} DO NOT generate code, markdown blocks, or extra explanations. "
            "Return ONLY the requested label or value. No conversation."
        )
        
        res = chat(model=self.model, messages=[
            {"role": "system", "content": strict_system_prompt},
            {"role": "user", "content": user_prompt}
        ])
        
        return self.clean_response(res['message']['content'])

    def classify(self, question_text):
        
        # 1단계: 과목 분류 (Strict Selection)
        # 단순히 분류하라고 하지 않고, 후보군(subject_candidates)을 명시하여 강제합니다.
        subject_candidates = list(SUBJECTS.keys())
        subject_prompt = f"Choose the correct subject from: {subject_candidates}. Question: {question_text}"
        subject = self.get_llm_response("You are a strict classifier.", subject_prompt)
        
        # 2단계: 영역 분류 (Scoped Selection)
        # 앞 단계에서 선택된 subject에 대해서만 영역을 고르도록 범위를 제한합니다.
        area_candidates = SUBJECTS.get(subject, ["기타"])
        area_prompt = f"Subject is {subject}. Choose one area from: {area_candidates}. Question: {question_text}"
        area = self.get_llm_response("You are a strict classifier.", area_prompt)
        
        # 3단계: 자기 검증 (Self-Reflection)
        # 분류가 올바른지 논리적으로 다시 한 번 확인합니다.
        verify_prompt = f"Question: {question_text}\nSubject: {subject}\nArea: {area}\nIs this classification correct? Answer YES or NO."
        verification = self.get_llm_response("Answer only YES or NO.", verify_prompt)
        
        return {"subject": subject, "area": area, "verification": verification}

def process_exam_files(input_dir, output_dir):
    classifier = ExamClassifier()
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    files = [f for f in os.listdir(input_dir) if f.endswith(".json")]
    
    for filename in files:
        print(f"[*] 처리 중: {filename}")
        
        with open(os.path.join(input_dir, filename), 'r', encoding='utf-8') as f:
            data = json.load(f)
            # 원본 데이터(list or dict) 구조를 그대로 유지합니다.
            items = data if isinstance(data, list) else [data]
            
            for item in items:
                q_text = item.get("question", "")
                if q_text:
                    # 원본 데이터를 수정하지 않고, 새 키값만 update합니다.
                    result = classifier.classify(q_text)
                    item.update(result)
            
            # 결과 저장
            with open(os.path.join(output_dir, f"classified_{filename}"), 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
    print("\n[*] 모든 작업이 완료되었습니다.")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_directory = os.path.join(base_dir, "data", "input")
    output_directory = os.path.join(base_dir, "data", "output")
    
    if not os.path.exists(input_directory):
        os.makedirs(input_directory)
        print(f"[*] '{input_directory}' 폴더를 생성했습니다. 파일을 넣고 다시 실행하세요.")
    else:
        process_exam_files(input_directory, output_directory)