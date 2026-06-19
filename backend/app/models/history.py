from sqlalchemy import Column, BigInteger, Integer, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.db.base import Base

class ProblemSolvingHistory(Base):
    __tablename__ = "problem_solving_history"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(BigInteger, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    selected_option = Column(JSONB, nullable=False) # 유저가 마킹한 정답 배열 스냅샷 (예: [2])
    is_correct = Column(Boolean, nullable=False)     # 채점 성공 여부 (True/False)
    exam_type = Column(String(50), nullable=False)   # 풀이 당시 시험 종류 스냅샷
    year = Column(Integer, nullable=True)            # 풀이 당시 시험 연도 스냅샷
    subject_snapshot = Column(String(100), nullable=False)
    category_snapshot = Column(String(50), nullable=False)
    submitted_at = Column(DateTime, default=func.now(), nullable=False)
    time = Column(Integer, nullable=True)            # 풀이 소요 시간 (초 단위)

    # 연관 관계 매핑 (Lazy Loading 지원)
    user = relationship("User", back_populates="solving_histories")
    question = relationship("Question")