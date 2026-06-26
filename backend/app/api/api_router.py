# app/api/api_router.py
from fastapi import APIRouter

# 💡 모든 v1 도메인 라우터 모듈을 깔끔하게 한 줄로 임포트합니다. (chatbot 추가)
from app.api.v1 import (
    auth,
    users,
    exams,
    attempts,
    statistics,
    ai,
    recommendations,
    rag,
    wrong_note,
    chatbot  # 🚀 🆕 챗봇 라우터 패키지 임포트 추가
)

api_router = APIRouter()

# ---------------------------------------------------------------------------
# 🚀 v1 하위 도메인 라우터 통합 등록
# ---------------------------------------------------------------------------

# 기본 엔드포인트 세트 (중복 등록 라인 제거 완료)
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(exams.router, prefix="/exams", tags=["Exams"])
api_router.include_router(attempts.router, prefix="/attempts", tags=["Attempts"])
api_router.include_router(statistics.router, prefix="/statistics", tags=["Statistics"])

# 제출 회차별 독립 오답노트 관리 라우터
api_router.include_router(
    statistics.wrong_notebook_router,
    prefix="/wrong-notebooks",
    tags=["WrongNotebooks"],
)

# AI 및 특화 도메인 엔드포인트 세트
api_router.include_router(ai.router, prefix="/ai", tags=["AI Integration"])
api_router.include_router(rag.router, prefix="/law", tags=["RAG"])
api_router.include_router(wrong_note.router, prefix="/wrong-note", tags=["WrongNote"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["Recommendations"])

# 🤖 🆕 1:1 오답 과외용 AI 챗봇 전용 도메인 라우터 등록
api_router.include_router(chatbot.router, prefix="/chatbot", tags=["AI Chatbot"])