# app/services/llm_service.py
import os
from openai import AsyncOpenAI  # 💡 비동기 처리를 위한 AsyncOpenAI 임포트
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()

# 💡 비동기 클라이언트로 초기화 진행
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def generate_answer(prompt: str) -> str:
    """기존 단일 프롬프트 방식의 RAG용 답변 생성 함수 (비동기 교정)"""
    try:
        # 💡 정석 문법인 client.chat.completions.create로 교정
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"🚨 [LLM_SERVICE_ERROR] generate_answer 실패: {str(e)}")
        return "답변을 생성하는 중 기술적 오류가 발생했습니다."

async def generate_chat_response(messages: List[Dict[str, str]]) -> str:
    """
    🚀 [신설] AI 오답 튜터 챗봇 전용 비동기 함수
    대화방의 System 가이드라인 및 누적 대화 내역 전체를 그대로 GPT에게 주입하여 흐름이 이어지는 답변을 받아옵니다.
    """
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages  # 💡 역할별(system, user, assistant) 대화 배열 스택 투입
        )
        # OpenAI v1.0+ 표준 리턴 데이터 파싱 구조 적용
        return response.choices[0].message.content
    except Exception as e:
        print(f"🚨 [LLM_SERVICE_ERROR] generate_chat_response 실패: {str(e)}")
        return "AI 오답 튜터가 답변을 준비하는 과정에서 에러가 발생했습니다. 잠시 후 다시 시도해 주세요."