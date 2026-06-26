# app/crud/chatbot.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.models.chatbot import ChatRoom, ChatMessage
from app.schemas.chatbot import ChatRoomCreate, ChatMessageCreate

# =================================================================
# 🏢 1. ChatRoom 관련 비동기 SQL 처리부
# =================================================================

async def create_chat_room(db: AsyncSession, user_id: int, room_in: ChatRoomCreate) -> ChatRoom:
    """새로운 AI 대화 전용 방을 생성합니다."""
    db_room = ChatRoom(
        user_id=user_id,
        title=room_in.title
    )
    db.add(db_room)
    await db.commit()
    await db.refresh(db_room)
    return db_room

async def get_rooms_by_user(db: AsyncSession, user_id: int) -> List[ChatRoom]:
    """해당 유저가 소유한 대화방 목록을 최신 생성 순서로 긁어옵니다."""
    stmt = select(ChatRoom).filter(ChatRoom.user_id == user_id).order_by(ChatRoom.id.desc())
    result = await db.execute(stmt)
    return list(result.scalars().all())

async def get_room_by_id(db: AsyncSession, room_id: int) -> Optional[ChatRoom]:
    """단일 대화방 객체를 조회합니다."""
    stmt = select(ChatRoom).filter(ChatRoom.id == room_id)
    result = await db.execute(stmt)
    return result.scalars().first()


# =================================================================
# 💬 2. ChatMessage 관련 비동기 SQL 처리부
# =================================================================

async def insert_chat_message(
    db: AsyncSession, 
    room_id: int, 
    role: str, 
    content: str, 
    question_id: Optional[int] = None
) -> ChatMessage:
    """유저의 질문 문장 또는 OpenAI GPT가 가공해낸 답변 문장을 메시지 테이블에 레코드로 삽입합니다."""
    db_message = ChatMessage(
        room_id=room_id,
        role=role,
        content=content,
        question_id=question_id
    )
    db.add(db_message)
    await db.commit()
    await db.refresh(db_message)
    return db_message

async def get_messages_by_room(db: AsyncSession, room_id: int) -> List[ChatMessage]:
    """특정 대화방 내부에서 오고 간 누적 대화 타임라인을 순서대로 정렬하여 로드합니다."""
    stmt = select(ChatMessage).filter(ChatMessage.room_id == room_id).order_by(ChatMessage.id.asc())
    result = await db.execute(stmt)
    return list(result.scalars().all())