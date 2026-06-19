# backend/app/models/user.py
from sqlalchemy import Column, BigInteger, String, Integer, DateTime
from sqlalchemy.sql import func
from app.db.base import Base  # 프로젝트 구조에 따른 Base 선언부 임포트

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    provider = Column(String(50), nullable=False)                  # 💡 추가: 소셜 로그인 제공자 ('google')
    provider_id = Column(String(255), nullable=False)              # 💡 추가: 소셜 로그인 유저 고유 ID
    nickname = Column(String(100), nullable=False)
    profile_image = Column(String(512), nullable=True)             # 💡 추가: 프로필 이미지 경로
    chat_limit_override = Column(Integer, nullable=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now()) # 💡 추가: 수정 일시