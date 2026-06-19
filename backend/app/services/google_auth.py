import httpx
from fastapi import HTTPException, status
from app.core.config import settings  # app/core/config.py의 세팅 객체 가정

# 구글 OAuth 관련 엔드포인트 URL
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

async def exchange_code_for_google_token(code: str) -> str:
    """
    기능: 구글이 던져준 일회용 코드를 구글 전용 액세스 토큰으로 교환합니다.
    매개변수: code (구글이 넘겨준 일회용 인증 코드 문자열)
    반환값: 구글 액세스 토큰 문자열
    """
    # .env 혹은 config에서 로드한 구글 자격증명 정보 사용
    data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(GOOGLE_TOKEN_URL, data=data)
            response_json = response.json()
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Google token exchange failed: {response_json.get('error_description', 'Unknown error')}"
                )
                
            # 구글 액세스 토큰 추출 및 반환
            google_access_token = response_json.get("access_token")
            if not google_access_token:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Google access_token not found in response"
                )
            return google_access_token
            
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Google server communication error: {exc}"
            )


async def get_google_user_profile(google_access_token: str) -> dict:
    """
    기능: 구글 액세스 토큰을 들고 구글 사용자 정보 엔드포인트를 호출하여 프로필을 가져옵니다.
    매개변수: google_access_token (위에서 발급받은 구글 토큰)
    반환값: {"id": "...", "email": "...", "name": "...", "picture": "..."} 형태의 딕셔너리
    """
    headers = {
        "Authorization": f"Bearer {google_access_token}"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(GOOGLE_USERINFO_URL, headers=headers)
            response_json = response.json()
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Failed to fetch user profile from Google"
                )
                
            # 명세에 명시된 형태 정보 구성 및 반환 (id, email, name, picture)
            return {
                "id": response_json.get("id"),
                "email": response_json.get("email"),
            }
            
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Google server communication error: {exc}"
            )