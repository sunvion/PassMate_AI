# app/services/llm_service.py
import os
import base64
from openai import AsyncOpenAI
from dotenv import load_dotenv
from typing import List, Dict, Optional

load_dotenv()

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 💡 외부 OpenAI 서버가 접근할 수 없는 로컬 이미지 파일을 안전하게 읽어 Base64로 인코딩하는 헬퍼 함수
def _encode_local_image_to_base64(image_path: str) -> Optional[str]:
    """
    로컬 시스템상의 이미지 절대 경로를 입력받아 OpenAI API에 직접 첨부 가능한 Base64 데이터 문자열로 변환합니다.
    """
    if not image_path or not os.path.exists(image_path):
        return None
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
            # 파일 확장자에 맞는 MIME-Type 동적 지정 (png 기준 기본 세팅)
            ext = os.path.splitext(image_path)[-1].lower().replace(".", "")
            mime_type = f"image/{ext}" if ext in ["png", "jpg", "jpeg", "webp"] else "image/png"
            return f"data:{mime_type};base64,{encoded_string}"
    except Exception as e:
        print(f"⚠️ [IMAGE_ENCODE_WARNING] 로컬 이미지 변환 실패 ({image_path}): {str(e)}")
        return None


async def generate_answer(prompt: str) -> str:
    """기존 단일 프롬프트 방식의 RAG용 답변 생성 함수 (유지)"""
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"🚨 [LLM_SERVICE_ERROR] generate_answer 실패: {str(e)}")
        return "답변을 생성하는 중 기술적 오류가 발생했습니다."


async def generate_chat_response(messages: List[Dict[str, str]], image_source: Optional[str] = None) -> str:
    """
    🚀 [고도화된 Vision 지원 버전]
    대화방의 가이드라인과 히스토리를 유지하면서, 문제 이미지 데이터(로컬 경로 또는 웹 URL)가 존재할 경우
    gpt-4o-mini 멀티모달 규격으로 메시지 배열의 최신 턴을 동적 가공하여 전송합니다.
    """
    try:
        # 멀티모달 처리를 위해 원본 메시지 리스트 스냅샷 복사
        processed_messages = []
        for msg in messages:
            processed_messages.append({"role": msg["role"], "content": msg["content"]})

        # 🖼️ 이미지 소스가 전달되었을 때 처리
        if image_source:
            final_image_url = None

            # 상황 1: 전달받은 문자열이 로컬 물리 경로인 경우 (예: backend/docs/parser/... 또는 프론트 정적 주소)
            if os.path.exists(image_source) or image_source.startswith("frontend/") or image_source.startswith("backend/"):
                # 상대 경로가 섞여 들어올 것을 대비해 절대 경로 매핑 전환 및 인코딩 실행
                base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
                absolute_path = os.path.join(base_dir, image_source) if not os.path.isabs(image_source) else image_source
                final_image_url = _encode_local_image_to_base64(absolute_path)
            
            # 상황 2: 이미 http로 시작하는 웹 URL이거나 이미 base64 프로토콜 형태로 들어온 경우
            elif image_source.startswith("http://") or image_source.startswith("https://") or image_source.startswith("data:image"):
                final_image_url = image_source

            # 💡 조립 단계: OpenAI 멀티모달 규격에 맞춰 마지막 유저 메시지의 content를 문자열에서 '배열 형태'로 치환합니다.
            if final_image_url:
                for msg in reversed(processed_messages):
                    if msg["role"] == "user":
                        # 기존 텍스트 알맹이와 이미지 오브젝트를 하나의 리스트로 통합 바인딩
                        msg["content"] = [
                            {"type": "text", "text": msg["content"]},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": final_image_url,
                                    "detail": "high"  # 🔍 문제지의 작은 글자(선택지 등)를 정밀 분석하기 위해 high 옵션 지정
                                }
                            }
                        ]
                        break

        # 🚀 gpt-4o-mini 호출 (텍스트 + 이미지를 한 번에 추론)
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=processed_messages,
            max_tokens=1200  # 비전 분석 및 해설 과정이 길어질 수 있으므로 최대 토큰을 소폭 상향 조정
        )
        return response.choices[0].message.content

    except Exception as e:
        print(f"🚨 [LLM_SERVICE_ERROR] generate_chat_response 비전 처리 실패: {str(e)}")
        return "AI 오답 튜터가 이미지를 시각적으로 분석하고 답변을 준비하는 과정에서 기술적 오류가 발생했습니다."