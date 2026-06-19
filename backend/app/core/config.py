# app/core/config.py
import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # API 서버 설정
    API_V1_STR: str = "/api/v1"
    
    # JWT 보안 설정
    SECRET_KEY: str  # 우리 서비스 자체 JWT 서명용 비밀키
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # 1일 유지
    
    # 데이터베이스 설정
    DATABASE_URL: str
    
    # 구글 OAuth 설정
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/callback/google"
    
    # 프론트엔드 리디렉션 주소
    FRONTEND_SUCCESS_URL: str = "http://localhost:3000/login-success"

    # .env 파일 로드 설정
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

settings = Settings()