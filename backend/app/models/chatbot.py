# backend/app/models/chatbot.py
from sqlalchemy import Column, BigInteger, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.base import Base

class ChatRoom(Base):
    __tablename__ = "chat_rooms"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # 💡 [핵심 고도화]: 대화방 마스터 레벨에 문제 ID를 바인딩하여 선제적 컨텍스트 준비를 가능하게 합니다.
    question_id = Column(BigInteger, ForeignKey("questions.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), server_default=func.now(), nullable=False)

    # 🔗 연관 관계 매핑
    user = relationship("User", back_populates="chat_rooms")
    messages = relationship("ChatMessage", back_populates="room", cascade="all, delete-orphan", passive_deletes=True)
    question = relationship("Question")  # 문항 정보 직접 접근용


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    room_id = Column(BigInteger, ForeignKey("chat_rooms.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(BigInteger, ForeignKey("questions.id", ondelete="SET NULL"), nullable=True)
    
    role = Column(String(20), nullable=False)     # 'user' 또는 'assistant'
    content = Column(Text, nullable=False)         # 대화 내용
    created_at = Column(DateTime(timezone=True), default=func.now(), server_default=func.now(), nullable=False)

    # 🔗 연관 관계 매핑
    room = relationship("ChatRoom", back_populates="messages")
    question = relationship("Question")