import json
import os
from ollama import chat

# 설정: 검증 대상 과목 및 영역
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
    def __init__(self, model="qwen2.5:1.5b"): 
        self.model = model

    def get_llm_response(self, system_prompt, user_prompt):
        """시스템 프롬프트를 분리하여 언어 및 출력 형식을 제어"""
        res = chat(model=self.model, messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ])
        return res['message']['content'].strip()

    def classify(self, question_text):
        """정의된 카테고리 내에서만 분류하도록 강제하는 로직"""
        
        # 1. 과목 분류: 후보군 명시
        subject_candidates = list(SUBJECTS.keys())
        subject_prompt = f"""
        Classify the subject of the following question. 
        You MUST choose ONLY from these subjects: {subject_candidates}.
        Question: {question_text}
        Return ONLY the subject name exactly as listed.
        """
        subject = self.get_llm_response("You are a strict classifier. Follow instructions exactly.", subject_prompt)
        
        # 2. 영역 분류: 선택된 과목의 하위 영역으로 후보군 제한
        area_candidates = SUBJECTS.get(subject, ["기타"])
        area_prompt = f"""
        Subject: {subject}
        You MUST choose ONLY one area from these: {area_candidates}.
        Question: {question_text}
        Return ONLY the area name exactly as listed.
        """
        area = self.get_llm_response("You are a strict classifier. Return only one category name.", area_prompt)
        
        # 3. 자기 검증: 결과가 후보군에 포함되는지 재확인
        verify_prompt = f"""
        Question: {question_text}
        Classified Subject: {subject}
        Classified Area: {area}
        Is this area valid for the given subject? Answer 'YES' or 'NO'.
        """
        verification = self.get_llm_response("Answer only YES or NO.", verify_prompt)
        
        return {"subject": subject, "area": area, "verification": verification}

def process_exam_files(input_dir, output_dir):
    """지정된 디렉토리의 JSON 파일을 처리하여 분류 결과를 저장"""
    classifier = ExamClassifier()
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    for filename in os.listdir(input_dir):
        if filename.endswith(".json"):
            file_path = os.path.join(input_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                items = data if isinstance(data, list) else [data]
                
                for item in items:
                    q_text = item.get("question", "")
                    if q_text:
                        # 이제 classify 메서드가 정상적으로 호출됩니다.
                        result = classifier.classify(q_text)
                        item.update(result)
                
                output_path = os.path.join(output_dir, f"classified_{filename}")
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f"[+] 분류 완료: {output_path}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_directory = os.path.join(base_dir, "data", "input")
    output_directory = os.path.join(base_dir, "data", "output")
    
    if not os.path.exists(input_directory):
        os.makedirs(input_directory)
        print(f"[*] 생성됨: {input_directory}. 이곳에 분석할 JSON 파일을 넣으세요.")
    else:
        process_exam_files(input_directory, output_directory)