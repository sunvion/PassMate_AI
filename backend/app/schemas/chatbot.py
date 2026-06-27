# app/schemas/chatbot.py
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import datetime

# =================================================================
# 🏢 1. 대화방(Room) 도메인 스키마
# =================================================================

class ChatRoomCreate(BaseModel):
    title: str = Field(..., description="대화방 제목")
    # 💡 프론트엔드 진입 시점에 저격을 위해 넘겨받을 문제 고유 번호
    question_id: Optional[int] = Field(None, description="선제적 컨텍스트 바인딩을 위한 문제 ID")

class ChatRoomResponse(BaseModel):
    id: int
    user_id: int
    title: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =================================================================
# 💬 2. 대화 메시지(Message) 도메인 스키마
# =================================================================

class ChatMessageCreate(BaseModel):
    content: str = Field(..., description="유저의 질문 내용 문자열")
    question_id: Optional[int] = Field(None, description="질문 중인 기준 오답 ID (선택)")

class ChatMessageResponse(BaseModel):
    id: int
    room_id: int
    question_id: Optional[int] = None
    role: str  # 'user' 또는 'assistant'
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)