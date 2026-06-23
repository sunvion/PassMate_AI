# backend/app/schemas/statistics.py
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class DashboardSummaryResponse(BaseModel):
    """💡 홈 화면 '학습 요약' 3단 카드 대시보드 전송 포맷"""
    total_solved: int                  # 총 풀이 문제 수
    average_correct_rate: float        # 평균 정답률
    recent_attempt_at: Optional[datetime] = None  # 최근 응시 기록

    model_config = ConfigDict(from_attributes=True)


class SolvedQuestionDetail(BaseModel):
    """💡 유저가 푼 개별 문제의 상세 기록 스냅샷"""
    history_id: int
    question_id: int
    question_text: str          # questions 테이블에서 JOIN으로 가져올 문제 발문
    selected_option: List[int]  # 유저가 제출한 보기
    is_correct: bool            # 정답 여부
    correct_answer: List[int]   # 실제 정답

    model_config = ConfigDict(from_attributes=True)


class ExamSessionDetailResponse(BaseModel):
    """💡 시험 세션별 점수 및 그 시험 안에서 푼 문제들의 통합 정보"""
    exam_type: str
    year: Optional[int]
    subject: str
    total_questions: int
    correct_count: int
    score: int
    submitted_at: datetime
    solved_questions: List[SolvedQuestionDetail]  # 해당 시험에서 푼 문제 상세 리스트

    model_config = ConfigDict(from_attributes=True)


# 🆕 추가된 오답노트 도메인용 스키마 클래스군 

class WrongExamSummaryResponse(BaseModel):
    """💡 오답노트 메인 화면용 목록 요약 데이터 포맷"""
    exam_type: str
    year: Optional[int]
    subject: str
    wrong_count: int                   # 유저가 해당 과목에서 틀린 총 문항 수

    model_config = ConfigDict(from_attributes=True)


class WrongQuestionDetailResponse(BaseModel):
    """💡 특정 과목 오답노트 진입 시 노출할 개별 문제 상세 피드백 데이터 포맷"""
    question_id: int
    question: str                      # 원본 문제 본문 질문 내용
    options: dict                      # questions 테이블의 원본 사지/오지 선다 보기 데이터 (JSONB 매칭)
    selected_option: List[int]         # 풀이 기록 테이블에 남아있는 유저의 마킹 데이터
    correct_answer: List[int]          # 원본 문제 테이블에 기록된 실제 정답 데이터
    explanation: Optional[str] = None  # 문제 해설 텍스트 데이터
    is_correct: bool                   # 항상 False 상태(오답노트이기 때문)
    submitted_at: datetime             # 최초 오답 제출 일시

    model_config = ConfigDict(from_attributes=True)