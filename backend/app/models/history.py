from sqlalchemy import Column, BigInteger, Integer, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.db.base import Base

class ProblemSolvingHistory(Base):  # 💡 만약 CRUD에서 'History'로 부르고 싶다면 이 이름을 History로 변경!
    __tablename__ = "problem_solving_history"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(BigInteger, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    selected_option = Column(JSONB, nullable=False) 
    is_correct = Column(Boolean, nullable=False)     
    exam_type = Column(String(50), nullable=False)   
    year = Column(Integer, nullable=True)            
    subject_snapshot = Column(String(100), nullable=False)
    category_snapshot = Column(String(50), nullable=False)
    
    # 💡 SQL 스키마의 TIME ZONE 및 NOT NULL 제약조건 싱크 맞춤
    submitted_at = Column(DateTime(timezone=True), default=func.now(), server_default=func.now(), nullable=False)
    time = Column(Integer, nullable=False)  # 💡 SQL이 NOT NULL이면 False로 매칭
    
    # 연관 관계 매핑
    user = relationship("User", back_populates="solving_histories")
    question = relationship("Question")