from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class SingleAttemptCreate(BaseModel):
    """단일 문제 채점 요청 바디 (옵션 A용)"""
    question_id: int
    selected_option: List[int]
    time: Optional[int] = None

class BulkAttemptCreate(BaseModel):
    """시험지 전체 일괄 채점 요청 바디 (옵션 B용)"""
    attempts: List[SingleAttemptCreate]

class AttemptResultResponse(BaseModel):
    """채점 결과 개별 문항 피드백 포맷"""
    question_id: int
    is_correct: bool
    correct_answer: List[int]
    explanation: Optional[str] = None

class BulkAttemptResultResponse(BaseModel):
    """일괄 채점 완료 후 프론트엔드 최종 스코어 보드 반환 포맷"""
    total_questions: int
    correct_count: int
    score: int
    results: List[AttemptResultResponse]

class ScoreSummaryResponse(BaseModel):
    """마이페이지 내 시험 점수 목록 리스트 조회 응답 포맷"""
    exam_type: str
    year: Optional[int]
    subject: str
    total_questions: int
    correct_count: int
    score: int
    submitted_at: datetime

    model_config = ConfigDict(from_attributes=True)