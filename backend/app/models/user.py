from sqlalchemy import Column, Integer, String, DateTime, func
from app.db.base import Base  # 기존 base.py에서 상속받는 Base 클래스

class User(Base):
    __tablename__ = "users"

    # id: INT, PK, AUTO_INCREMENT
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # email: VARCHAR, UNIQUE, NOT NULL
    email = Column(String, unique=True, index=True, nullable=False)
    
    # name: VARCHAR, NOT NULL
    # name = Column(String, nullable=False)

    # 서비스 내에서 활동할 닉네임 (선택 사항, 초기값은 name과 동일하게 설정 가능)
    nickname = Column(String, unique=True, index=True, nullable=False) # 👈 중복 방지 설정
    
    # profile_image: VARCHAR, NULL (Optional)
    profile_image = Column(String, nullable=True)
    
    # created_at: TIMESTAMP, DEFAULT CURRENT_TIMESTAMP, NOT NULL
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # updated_at: TIMESTAMP, DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, NOT NULL
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)