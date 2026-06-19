# backend/app/models/user.py
from sqlalchemy import Column, BigInteger, String, Integer, DateTime
from sqlalchemy.sql import func
from app.db.base import Base  # 기존 base.py에서 상속받는 Base 클래스

class User(Base):
    __tablename__ = "users"

    # id: BIGINT, PK, AUTO_INCREMENT (대규모 트래픽 및 확장성을 위해 BigInteger 유지)
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    
    # email: VARCHAR(255), UNIQUE, NOT NULL
    email = Column(String(255), unique=True, index=True, nullable=False)
    
    # 소셜 로그인 제공자 및 고유 ID (내가 구현한 로그인 로직의 핵심)
    provider = Column(String(50), nullable=False)                  # 예: 'google'
    provider_id = Column(String(255), nullable=False)              # 구글 고유 유저 ID
    
    # 서비스 내에서 활동할 닉네임 (상대방의 중복 방지 제약조건 반영)
    nickname = Column(String(100), unique=True, index=True, nullable=False)
    
    # profile_image: VARCHAR(512), NULL (구글 프로필 이미지 URL이 길 수 있으므로 512자 유지)
    profile_image = Column(String(512), nullable=True)
    
    # 서비스 커스텀 필드 유지
    chat_limit_override = Column(Integer, nullable=True)
    
    # 생성 및 수정 일시 (상대방의 타임존 설정 및 NOT NULL 반영)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)