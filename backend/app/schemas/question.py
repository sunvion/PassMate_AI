from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, List
from datetime import datetime

class QuestionBase(BaseModel):
    exam_type: str
    subject: str
    chapter: Optional[str] = None
    year: Optional[int] = None
    number: int
    question: str
    body: Optional[str] = None
    options: Dict[str, str]
    answer: List[int]
    explanation: Optional[str] = None
    points: int = 2
    category: str
    question_type: str
    image_url: Optional[str] = None
    video_url: Optional[str] = None

class QuestionResponse(QuestionBase):
    id: int
    created_at: datetime
    
    # Pydantic v2 ORM 호환 설정
    model_config = ConfigDict(from_attributes=True)

class ExamMetaResponse(BaseModel):
    """메인 화면 대시보드 탭 구성을 위한 고유 시험 정보 응답 포맷"""
    exam_type: str
    subject: str
    year: Optional[int]
    
    model_config = ConfigDict(from_attributes=True)