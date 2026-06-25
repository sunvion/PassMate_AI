# app/schemas/ai.py
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Dict, Optional

class QuestionRecommendation(BaseModel):
    # 💡 Pydantic v2의 validation_alias를 지정하여 ORM 객체의 실제 컬럼명과 프론트엔드 노출용 필드명을 완벽히 동기화
    question_id: int = Field(..., validation_alias="id") 
    question: str
    image_url: Optional[str] = None
    options: Dict[str, str]  
    correct_answer: List[int] = Field(..., validation_alias="answer") 
    explanation: Optional[str] = None
    difficulty: int = Field(2, validation_alias="points") 
    chapter: Optional[str] = None  # 💡 SQL 모델의 nullable=True 스펙 반영

    # 💡 프로젝트의 다른 파일들과 동일한 Pydantic v2 ConfigDict 선언 체계로 통일
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class AIRecommendationListResponse(BaseModel):
    recommendation_type: str
    chapter: str
    items: List[QuestionRecommendation]

    model_config = ConfigDict(from_attributes=True)