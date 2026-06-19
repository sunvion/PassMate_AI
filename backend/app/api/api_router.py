from fastapi import APIRouter
from app.api.v1 import auth, users

api_router = APIRouter()

# v1 라우터들을 등록 (prefix를 분리하여 깔끔하게 관리)
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])