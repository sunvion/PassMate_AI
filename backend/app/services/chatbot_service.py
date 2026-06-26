# app/services/chatbot_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.crud import chatbot as chatbot_crud
from app.models.chatbot import ChatRoom, ChatMessage
from app.schemas.chatbot import ChatRoomCreate, ChatMessageCreate

# 💡 이미 프로젝트 구조에 준비되어 있는 LLM 및 컨텍스트 빌더 모듈 임포트
from app.services.context_builder import build_question_context
from app.services.llm_service import generate_chat_response


async def create_new_room(db: AsyncSession, user_id: int, room_in: ChatRoomCreate) -> ChatRoom:
    """
    [대화방 생성] 유저 전용 오답 클리닉 대화방 레코드를 신설합니다.
    """
    return await chatbot_crud.create_chat_room(db=db, user_id=user_id, room_in=room_in)


async def get_user_rooms(db: AsyncSession, user_id: int) -> List[ChatRoom]:
    """
    [대화방 목록 조회] 특정 유저가 가지고 있는 모든 대화방 리스트를 반환합니다.
    """
    return await chatbot_crud.get_rooms_by_user(db=db, user_id=user_id)


async def get_room_messages(db: AsyncSession, room_id: int, user_id: int) -> List[ChatMessage]:
    """
    [대화 이력 조회] 대화방에 진입했을 때 과거 대화 타임라인을 안전하게 권한 검증 후 반환합니다.
    """
    # 🛡️ 보안 가드레이르: 타인의 대화방을 훔쳐보지 못하도록 소유권 검증
    room = await chatbot_crud.get_room_by_id(db, room_id)
    if not room or room.user_id != user_id:
        raise ValueError("해당 대화방에 접근할 권한이 없거나 존재하지 않는 방입니다.")
        
    return await chatbot_crud.get_messages_by_room(db=db, room_id=room_id)


async def process_user_message(
    db: AsyncSession, 
    user_id: int, 
    room_id: int, 
    message_in: ChatMessageCreate
) -> ChatMessage:
    """
    [핵심 엔진] 유저의 질문 수신 -> 오답 컨텍스트 조립 -> GPT 호출 -> 대화 내역 쌍방 저장을 총괄합니다.
    """
    # 1. 대화방 소유권 검증
    room = await chatbot_crud.get_room_by_id(db, room_id)
    if not room or room.user_id != user_id:
        raise ValueError("해당 대화방에 메시지를 보낼 권한이 없습니다.")

    # 2. 유저가 입력한 새 질문을 데이터베이스(DB)에 먼저 선반영 저장
    await chatbot_crud.insert_chat_message(
        db=db,
        room_id=room_id,
        role="user",
        content=message_in.content,
        question_id=message_in.question_id
    )

    # 3. GPT에게 대화의 맥락(Context)을 학습시키기 위한 프롬프트 가이드라인(System Prompt) 초기 조립
    system_prompt = (
        "너는 친절하고 전문적인 IT 컴퓨터일반 및 도로교통법규 기출문제 핵심 오답 과외 선생님인 'AI 오답 튜터'야.\n"
        "학생이 질문한 내용에 대해 정답 해설을 보아도 이해하지 못한 구멍 난 개념이 무엇인지 파악하고,\n"
        "이해하기 쉽도록 구체적인 예시나 비교 분석을 곁들여서 1:1 과외하듯 존댓말로 설명해줘."
    )

    # 4. 🎯 [오답 컨텍스트 주입 🌟] question_id가 실려왔다면 context_builder를 가동
    if message_in.question_id:
        try:
            # context_builder.py 내 비동기 함수를 호출하여 해당 문항의 발문/보기/정답/해설 텍스트 덩어리를 획득
            q_context = await build_question_context(db, message_in.question_id)
            if q_context:
                system_prompt += (
                    f"\n\n[🚨 현재 학생이 틀려서 질문 중인 기출문항 정보]\n{q_context}\n"
                    f"위 문제의 발문, 보기 구조, 공식 정답 해설을 완벽히 숙지한 채로 학생의 다음 질문에 정교하게 답변해줘."
                )
        except Exception as ce:
            # 툴이 아직 미완성이거나 에러가 나더라도 대화 자체가 깨지지 않도록 가볍게 로그만 남기고 백업 처리
            print(f"⚠️ [CONTEXT_BUILDER_WARNING] 퀴즈 문맥 확보 실패: {str(ce)}")

    # 5. OpenAI 대화 스택 규격에 맞게 [System Prompt + 누적 대화 히스토리] 어레이 빌드
    openai_messages = [
        {"role": "system", "content": system_prompt}
    ]

    # DB에서 지금까지 주고받은 전체 대화(방금 저장한 유저 질문 포함)를 순서대로 가져옴
    current_history = await chatbot_crud.get_messages_by_room(db, room_id)
    for msg in current_history:
        openai_messages.append({
            "role": msg.role, 
            "content": msg.content
        })

    # 6. 🚀 llm_service.py를 깨워 OpenAI Async API 최종 연동 및 답변 생성 완료 수신 (await)
    ai_generated_content = await generate_chat_response(openai_messages)

    # 7. GPT가 가공해낸 최종 답변을 assistant 역할로 DB에 영구 기록
    ai_message_record = await chatbot_crud.insert_chat_message(
        db=db,
        room_id=room_id,
        role="assistant",
        content=ai_generated_content,
        question_id=message_in.question_id
    )

    # 8. 라우터로 완성된 AI 메시지 레코드 반환
    return ai_message_record