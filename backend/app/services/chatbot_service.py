# backend/app/services/chatbot_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.crud import chatbot as chatbot_crud
from app.models.chatbot import ChatRoom, ChatMessage
from app.models.question import Question
from app.schemas.chatbot import ChatMessageCreate

from app.services.context_builder import build_question_context
from app.services.llm_service import generate_chat_response


# =========================================================
# ROLE / POLICY (고정 레벨 - 절대 바뀌지 않음)
# =========================================================

ROLE = "너는 기출문제 기반 학습을 돕는 AI 튜터다."

POLICY = """
- 반드시 제공된 문제 기반으로만 답변한다
- 과목 외 질문 금지
- 추측 금지
- 문제 근거 없이 답변하지 않는다
- 설명 + 이유 + 개념 중심으로 답변한다
"""


# =========================================================
# DOMAIN (과목별 제한 로직)
# =========================================================

def build_domain(subject: str) -> str:
    if not subject:
        return "과목 정보 없음"

    if "컴퓨터" in subject:
        return """
[과목: 컴퓨터일반]
허용 범위:
- 컴퓨터구조, 운영체제, DB, 네트워크, 자료구조, 보안, 프로그래밍 개념

금지:
- 시사, 연예, 상담, 과목 외 IT 일반지식
"""

    if "도로" in subject or "운전" in subject:
        return """
[과목: 운전면허]
허용 범위:
- 도로교통법, 신호, 표지판, 벌점, 행정처분, 안전운전

금지:
- 정치, 연예, 투자, 일반 상식, 프로그래밍
"""

    return """
[과목: 일반]
- 제공된 문제 범위 내에서만 답변
"""

async def process_user_message(
    db: AsyncSession,
    user_id: int,
    room_id: int,
    message_in: ChatMessageCreate
) -> ChatMessage:

    # =========================================================
    # 1. 방 검증
    # =========================================================
    room = await chatbot_crud.get_room_by_id(db, room_id)

    if not room or room.user_id != user_id:
        raise ValueError("접근 권한 없음")

    room_question_id = room.question_id

    # =========================================================
    # 2. 기본 변수 초기화
    # =========================================================
    q_info = None
    subject = None
    q_context = None
    target_image = None
    persona = "기출문제 기반 학습 튜터"

    # =========================================================
    # 3. 문제 데이터 로딩 (핵심)
    # =========================================================
    if room_question_id:

        q_info = await db.get(Question, room_question_id)

        if q_info:
            subject = q_info.subject
            target_image = q_info.image_url

            # 🔥 context는 여기서 "먼저" 생성해야 함
            q_context = await build_question_context(db, room_question_id)

            # persona는 최소화 (중요)
            if "컴퓨터" in subject:
                persona = "컴퓨터 기초 개념을 설명하는 튜터"
            elif "도로" in subject or "운전" in subject:
                persona = "도로교통법 기반 설명 튜터"

    # =========================================================
    # 4. system prompt 생성 (여기서 ONLY 1번 생성)
    # =========================================================
    domain = build_domain(subject)

    system_prompt = f"""
{ROLE}

[역할 설명]
{persona}

[과목]
{subject}

{domain}

[문제]
{q_context}

[규칙]
{POLICY}
"""
    
    # =========================================================
    # 5. 유저 메시지 저장
    # =========================================================
    await chatbot_crud.insert_chat_message(
        db=db,
        room_id=room_id,
        role="user",
        content=message_in.content,
        question_id=room_question_id
    )

    # =========================================================
    # 6. OpenAI 메시지 구성
    # =========================================================
    messages = [
        {"role": "system", "content": system_prompt}
    ]

    history = await chatbot_crud.get_messages_by_room(db, room_id)

    for msg in history:
        # 🔥 가드: 이상한 fallback 제거
        if msg.content and "죄송합니다" in msg.content:
            continue

        messages.append({
            "role": msg.role,
            "content": msg.content
        })

    # =========================================================
    # 7. LLM 호출
    # =========================================================
    ai_response = await generate_chat_response(
        messages,
        image_source=target_image
    )

    # =========================================================
    # 8. 저장
    # =========================================================
    result = await chatbot_crud.insert_chat_message(
        db=db,
        room_id=room_id,
        role="assistant",
        content=ai_response,
        question_id=room_question_id
    )

    return result