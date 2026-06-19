from sqlalchemy import Column, BigInteger, Integer, String, Text, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from app.db.base import Base

class Question(Base):
    __tablename__ = "questions"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    exam_type = Column(String(50), nullable=False)
    subject = Column(String(100), nullable=False)
    chapter = Column(String(100), nullable=True) 
    year = Column(Integer, nullable=True)
    number = Column(Integer, nullable=False)
    question = Column(Text, nullable=False)
    body = Column(Text, nullable=True)
    options = Column(JSONB, nullable=False)       # JSONB로 오지선다 및 사지선다 보관
    answer = Column(JSONB, nullable=False)        # JSONB Array 형태로 정답 보관 (예: [2] 혹은 [1, 3])
    explanation = Column(Text, nullable=True)
    points = Column(Integer, default=2, nullable=True) # 기본 배점 2점 (공무원은 스크립트에서 5점 오버라이드 가능)
    category = Column(String(50), nullable=False)
    question_type = Column(String(50), nullable=False) # NORMAL, BOX_QUESTION 등 UI 레이아웃 타입
    image_url = Column(String(512), nullable=True)
    video_url = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)