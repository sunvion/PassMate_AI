# backend/app/api/api_router.py
from fastapi import APIRouter
from app.api.v1 import auth, users, exams, attempts, statistics, recommendations, rag, wrong_note  # 라우터 패키지 임포트

api_router = APIRouter()

# 🔐 v1 엔드포인트 라우팅 등록 및 태그 분류
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])

# 📝 기출문제 조회 및 채점 파이프라인 연동
api_router.include_router(exams.router, prefix="/exams", tags=["Exams"])
api_router.include_router(attempts.router, prefix="/attempts", tags=["Attempts"])

# 📊 1. 최신 세션 반영형 통계 및 대시보드 도메인 라우터 등록
api_router.include_router(statistics.router, prefix="/statistics", tags=["Statistics"])

# 🆕 📄 2. 회차별 독립형 오답노트 관리 도메인 라우터 등록 (프론트엔드 요구사항 주소 바인딩)
api_router.include_router(
    statistics.wrong_notebook_router, 
    prefix="/wrong-notebooks", 
    tags=["WrongNotebooks"]
)

# 🔥 핵심 수정
api_router.include_router(rag.router, prefix="/law", tags=["RAG"])

api_router.include_router(wrong_note.router, prefix="/wrong-note", tags=["WrongNote"])

api_router.include_router(
    recommendations.router,
    prefix="/recommendations",
    tags=["Recommendations"]
)
