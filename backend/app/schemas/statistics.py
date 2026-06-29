# backend/app/schemas/statistics.py
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

# =================================================================
# 📊 1. 홈 대시보드 & 회차별 성적표 도메인 스키마 (기존 유지)
# =================================================================

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


# =================================================================
# 🆕 2. 제출 회차별 독립 오답노트 도메인 스키마 (보완 및 수정)
# =================================================================

class WrongNotebookListElement(BaseModel):
    """💡 오답노트 메인 목록 조회용 개별 원소 포맷 (GET /wrong-notebooks)"""
    id: int                            # 오답노트 고유 ID (wrong_notebook_id)
    title: str                         # 오답노트 네이밍 (중복 방지 접미사 포함)
    exam_type: str                     # 시험 직렬 종류 (CS_GENERAL, CS_LOCAL 등)
    year: Optional[int]                # 기출 연도
    subject: str                       # 과목 명칭 (컴퓨터일반 등)
    wrong_count: int                   # 해당 회차에서 틀린 문제 수 (status = 'wrong')
    unsolved_count: int                # 해당 회차에서 안 푼 문제 수 (status = 'unsolved')
    total_count: int                   # 오답노트에 귀속된 총 문항 수 (wrong + unsolved)
    created_at: str                    # 생성일자 포맷 스냅샷 (예: "2026-06-24")

    model_config = ConfigDict(from_attributes=True)


class WrongNotebookItemDetail(BaseModel):
    """💡 특정 오답노트 상세 내부의 문항별 원본 데이터 및 채점 정보 스냅샷"""
    question_id: int
    number: int                        # 원본 시험지 기준 실제 문제 번호 필드
    question: str                      # 원본 문제 질문 본문
    options: dict                      # 사지/오지 선다 보기 딕셔너리 (JSONB 맵핑)
    selected_option: List[int]         # 사용자가 마킹했던 보기 배열 (안 풀었으면 [])
    correct_answer: List[int]          # 실제 시스템 정답 번호 배열
    is_correct: bool                   # 정답 여부 (오답노트 아이템이므로 기본 False)
    status: str                        # 'wrong' (틀린 문제) 또는 'unsolved' (안 푼 문제) 구분자
    explanation: Optional[str] = None  # 문항 전용 상세 해설 데이터
    image_url: Optional[str] = None    # 기출 지문 이미지 주소 필드
    submitted_at: datetime             # 답안 제출 및 발급 타임스탬프
    
    # 🎯 [핵심 추가]: 이 문항과 이미 연결된 AI 챗봇방이 있다면 방 ID(int), 없으면 null(None)로 응답
    chat_room_id: Optional[int] = None 

    model_config = ConfigDict(from_attributes=True)


class WrongNotebookDetailResponse(BaseModel):
    """💡 오답노트 단일 상세 내역 응답 포맷 (GET /wrong-notebooks/{wrong_notebook_id})"""
    id: int                            # wrong_notebook_id
    title: str                         # 오답노트 명칭
    exam_type: str                     # 시험 종류
    year: Optional[int]                # 기출 연도
    subject: str                       # 과목 명칭
    items: List[WrongNotebookItemDetail]  # 귀속된 오답 및 미풀이 문항 통합 리스트 (여기에 자동으로 chat_room_id가 바인딩됩니다.)

    model_config = ConfigDict(from_attributes=True)


class WrongNotebookUpdateTitleRequest(BaseModel):
    """💡 오답노트 고유 제목 수정을 위한 인바운드 요청 바디 규격 (PATCH)"""
    title: str                         # 변경하려는 새로운 오답노트 이름


class ChapterWrongCountResponse(BaseModel):
    """💡 오답노트 메인 대시보드 챕터별 오답 개수 요약 포맷"""
    chapter: str
    wrong_count: int

    model_config = ConfigDict(from_attributes=True)


class LearningProgressSaveRequest(BaseModel):
    """💡 채점 없이 한 문제씩 풀기 도중 '나중에 학습' 클릭 시 상태 보존을 위한 요청 포맷"""
    exam_type: str
    subject: str
    year: Optional[int] = 0            # 운전면허 등 연도 없는 과목은 기본값 0
    last_question_id: int              # 이탈 시점에 화면에 머물러 있던 문제의 ID (PK)
    solved_count: int                  # 프론트엔드 세션에서 현재까지 실제 풀이 완료한 누적 문항 수


class UserLearnedDomainElement(BaseModel):
    """💡 유저가 실제 학습한 이력이 존재하는 고유 시험/과목 원소 포맷"""
    exam_type: str                     # 예: 'CS_GENERAL', 'CS_LOCAL'
    subject: str                       # 예: '컴퓨터일반'

    model_config = ConfigDict(from_attributes=True)