# app/models/chatbot.py
from sqlalchemy import Column, BigInteger, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.base import Base

class ChatRoom(Base):
    __tablename__ = "chat_rooms"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)  # 예: "문항 #161 오답 과외방"
    created_at = Column(DateTime(timezone=True), default=func.now(), server_default=func.now(), nullable=False)

    # 🔗 연관 관계 매핑
    user = relationship("User", back_populates="chat_rooms")
    messages = relationship("ChatMessage", back_populates="room", cascade="all, delete-orphan", passive_deletes=True)


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    room_id = Column(BigInteger, ForeignKey("chat_rooms.id", ondelete="CASCADE"), nullable=False)
    
    # 💡 질문 컨텍스트 추적용: 어떤 문제를 보고 대화했는지 기록 (Null 허용)
    question_id = Column(BigInteger, ForeignKey("questions.id", ondelete="SET NULL"), nullable=True)
    
    role = Column(String(20), nullable=False)     # 'user' 또는 'assistant'
    content = Column(Text, nullable=False)         # 대화 알맹이 텍스트
    created_at = Column(DateTime(timezone=True), default=func.now(), server_default=func.now(), nullable=False)

    # 🔗 연관 관계 매핑
    room = relationship("ChatRoom", back_populates="messages")
    question = relationship("Question")