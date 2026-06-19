import json
import os
import re
from ollama import chat

# ==============================================================================
# 1. 설정 영역 (Configuration)
# ==============================================================================
# 분류할 과목과 그에 따른 하위 영역을 정의합니다.
# LLM 프롬프트에 이 리스트를 주입하여, 모델이 정의된 범주 내에서만 답변하도록 강제합니다.
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
    Ollama 로컬 모델을 활용하여 기출문제를 분류하고 검증하는 클래스입니다.
    이 클래스는 3단계 파이프라인(과목 분류 -> 영역 분류 -> 자기 검증)을 수행합니다.
    """
    
    def __init__(self, model="qwen2.5:1.5b"): 
        self.model = model

    def clean_response(self, text):
        """
        LLM이 가끔 생성하는 마크다운 코드 블록(```)이나 불필요한 공백을 제거합니다.
        포트폴리오 포인트: 로컬 LLM의 환각(Hallucination) 현상을 후처리를 통해 제어함.
        """
        # 마크다운 코드 블록 패턴 제거 (예: ```c ... ```)
        cleaned = re.sub(r'```[\s\S]*?```', '', text)
        return cleaned.strip()

    def get_llm_response(self, system_prompt, user_prompt):
        """
        Ollama 모델에게 메시지를 전달하고 응답을 받는 함수입니다.
        시스템 프롬프트를 통해 모델의 행동(Persona)을 고정합니다.
        """
        # 시스템 프롬프트에 코드 생성 금지 지시를 포함하여 환각을 억제합니다.
        strict_system_prompt = (
            f"{system_prompt} DO NOT generate code, markdown blocks, or extra explanations. "
            "Return ONLY the requested label or value."
        )
        
        res = chat(model=self.model, messages=[
            {"role": "system", "content": strict_system_prompt},
            {"role": "user", "content": user_prompt}
        ])
        
        # 모델의 원본 응답을 후처리하여 깔끔하게 만듭니다.
        return self.clean_response(res['message']['content'])

    def classify(self, question_text):
        """
        [핵심 로직] 기출문제 분류 파이프라인
        1. Subject 분류 -> 2. Area 분류 -> 3. Self-Reflection (검증)
        """
        
        # 1단계: 과목 분류
        subject_candidates = list(SUBJECTS.keys())
        subject = self.get_llm_response(
            "You are a strict classifier.",
            f"Classify the subject. Choose ONLY from: {subject_candidates}. Question: {question_text}"
        )
        
        # 2단계: 영역 분류
        area_candidates = SUBJECTS.get(subject, ["기타"])
        area = self.get_llm_response(
            "You are a strict classifier.",
            f"Subject: {subject}. Choose ONLY one area from: {area_candidates}. Question: {question_text}"
        )
        
        # 3단계: 자기 검증 (Self-Reflection)
        # 모델이 스스로 분류 결과를 평가하게 하여 신뢰성을 확보합니다.
        verification = self.get_llm_response(
            "Answer only YES or NO.",
            f"Question: {question_text}\nSubject: {subject}\nArea: {area}\nIs this correct? YES or NO."
        )
        
        return {"subject": subject, "area": area, "verification": verification}

def process_exam_files(input_dir, output_dir):
    """
    지정된 디렉토리의 JSON 파일을 처리합니다.
    팀원들에게 진행 상황을 공유할 수 있도록 상세한 콘솔 로그를 남깁니다.
    """
    classifier = ExamClassifier()
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    files = [f for f in os.listdir(input_dir) if f.endswith(".json")]
    
    for idx, filename in enumerate(files):
        print(f"[{idx + 1}/{len(files)}] 분석 중: {filename}")
        
        with open(os.path.join(input_dir, filename), 'r', encoding='utf-8') as f:
            data = json.load(f)
            items = data if isinstance(data, list) else [data]
            
            for item in items:
                q_text = item.get("question", "")
                if q_text:
                    # 분류 수행
                    result = classifier.classify(q_text)
                    item.update(result)
            
            # 결과 저장
            with open(os.path.join(output_dir, f"classified_{filename}"), 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
    print("\n[*] 모든 작업이 완료되었습니다.")

if __name__ == "__main__":
    # 프로젝트 루트 경로 기반으로 자동 설정
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_directory = os.path.join(base_dir, "data", "input")
    output_directory = os.path.join(base_dir, "data", "output")
    
    if not os.path.exists(input_directory):
        os.makedirs(input_directory)
        print(f"[*] '{input_directory}' 폴더를 생성했습니다. 파일을 넣고 다시 실행하세요.")
    else:
        process_exam_files(input_directory, output_directory)