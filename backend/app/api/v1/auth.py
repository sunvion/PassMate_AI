from fastapi import APIRouter, Depends, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
# 💡 [핵심] 비동기 세션 타입을 인지하기 위해 AsyncSession을 추가합니다.
from sqlalchemy.ext.asyncio import AsyncSession 
import urllib.parse

from app.db.session import get_db
from app.services import google_auth
from app.crud import user as user_crud
from app.core import security

router = APIRouter()

@router.get("/callback/google")
async def google_oauth_callback(
    code: str = Query(...), 
    db: AsyncSession = Depends(get_db)
):
    """
    구글 로그인 콜백 엔드포인트
    1. 구글 일회용 코드로 구글 액세스 토큰 교환
    2. 구글 토큰으로 사용자 프로필 정보 획득
    3. DB 조회 후 기존 회원이 아니면 신규 가입 처리 (비동기)
    4. 우리 서비스 전용 JWT 토큰 발급
    5. 프론트엔드 성공 페이지로 JWT와 닉네임을 담아 리디렉션
    """
    # 1. 구글 일회용 코드를 구글 전용 액세스 토큰으로 교환
    google_access_token = await google_auth.exchange_code_for_google_token(code) 
    
    # 2. 구글 액세스 토큰으로 유저 프로필 정보 가져오기
    google_profile = await google_auth.get_google_user_profile(google_access_token) 
    email = google_profile.get("email") 
    provider_id = str(google_profile.get("id")) # 💡 구글의 고유 식별 ID를 가져옵니다.
    
    # 3. DB에서 유저 조회 및 가입 여부 판단 (비동기 await 적용)
    db_user = await user_crud.get_user_by_email(db, email=email) 
    if not db_user:
        # 💡 신규 소셜 가입자인 경우 provider_id를 함께 전달하여 생성합니다!
        db_user = await user_crud.create_google_user(db=db, email=email, provider_id=provider_id) 
        
    # 4. 우리 서비스 전용 자체 JWT 토큰 생성
    access_token = security.create_access_token(subject=db_user.email)
    
    # 5. 고유 닉네임 추출 및 안전하게 URL 인코딩 처리
    encoded_nickname = urllib.parse.quote(db_user.nickname)
    
    # 프론트엔드(localhost:3000)의 로그인 성공 페이지로 토큰과 고유 닉네임을 리디렉션 전달
    frontend_redirect_url = (
        f"http://localhost:3000/login-success?token={access_token}&nickname={encoded_nickname}"
    )
    
    return RedirectResponse(url=frontend_redirect_url)


@router.post("/logout")
def logout():
    """
    사용자 로그아웃 API
    프론트엔드에서 저장된 토큰을 파기하는 것과 별개로, 
    백엔드 세션 종료나 토큰 만료 처리를 안전하게 기록하기 위한 창구입니다.
    """
    # TODO: 필요한 경우 블랙리스트 토큰 DB 저장 등의 로그아웃 비즈니스 로직 구현 
    return {"status": "success", "message": "Successfully logged out"}