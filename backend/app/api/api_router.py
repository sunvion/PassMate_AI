# app/api/api_router.py
from fastapi import APIRouter

# 💡 모든 v1 도메인 라우터 모듈을 깔끔하게 한 줄로 임포트합니다.
from app.api.v1 import (
    auth,
    users,
    exams,
    attempts,
    statistics,
    ai,
    recommendations,
    rag,
    wrong_note
)

api_router = APIRouter()

# ---------------------------------------------------------------------------
# 🚀 v1 하위 도메인 라우터 통합 등록
# ---------------------------------------------------------------------------

# 기본 엔드포인트 세트
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(exams.router, prefix="/exams", tags=["Exams"])
api_router.include_router(attempts.router, prefix="/attempts", tags=["Attempts"])
api_router.include_router(statistics.router, prefix="/statistics", tags=["Statistics"])

# AI 및 특화 도메인 엔드포인트 세트 (중복 제거 완료)
api_router.include_router(ai.router, prefix="/ai", tags=["AI Integration"])
api_router.include_router(rag.router, prefix="/law", tags=["RAG"])
api_router.include_router(wrong_note.router, prefix="/wrong-note", tags=["WrongNote"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["Recommendations"])