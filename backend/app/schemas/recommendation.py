from pydantic import BaseModel
from typing import List


class RecommendationAnalyzeRequest(BaseModel):
    question_id: int


class RecommendationAnalyzeResponse(BaseModel):
    question_id: int
    exam_type: str
    subject: str
    weak_topic: str
    analysis: str
    recommended_study_topics: List[str]