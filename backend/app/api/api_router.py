# backend/app/api/v1/api_router.py
from fastapi import APIRouter
from app.api.v1 import auth, users, exams, attempts, statistics  # 신규 도메인 라우터 패키지 임포트

api_router = APIRouter()

# v1 엔드포인트 라우팅 등록 및 태그 분류
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])

# 기출문제 조회 및 채점 파이프라인 연동
api_router.include_router(exams.router, prefix="/exams", tags=["Exams"])
api_router.include_router(attempts.router, prefix="/attempts", tags=["Attempts"])

# 🆕 통계 및 대시보드 도메인 라우터 등록
api_router.include_router(statistics.router, prefix="/statistics", tags=["Statistics"])