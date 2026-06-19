# app/core/security.py
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from jwt.exceptions import InvalidTokenError
from app.core.config import settings

# 💡 아래 3가지 import 문을 파일 상단에 추가해 주세요!
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# HTTP 요청 헤더에서 'Authorization: Bearer <토큰>'을 자동으로 추출해주는 FastAPI의 보안 도구입니다.
security_scheme = HTTPBearer()

def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "iat": datetime.now(timezone.utc)
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        token_user_email: str = payload.get("sub")
        if token_user_email is None:
            return None
        return token_user_email
    except InvalidTokenError:
        return None


# =================🔥 새로 추가할 의존성 함수 🔥 =================

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)) -> str:
    """
    FastAPI 라우터에서 유저 인증이 필요할 때 Depends()로 주입할 의존성 함수입니다.
    1. 요청 헤더(Header)에서 'Authorization: Bearer <토큰>' 형태의 토큰을 가로챕니다.
    2. 토큰을 복호화(Verify)하여 변조되거나 만료되었는지 검사합니다.
    3. 올바른 토큰이라면 이메일(sub)을 반환하고, 문제가 있다면 즉시 401 Unauthorized 에러를 발생시킵니다.
    """
    # credentials.credentials를 통해 헤더에서 'Bearer '를 뺀 순수 JWT 문자열만 쏙 빼옵니다.
    token = credentials.credentials
    
    # 우리가 위에 만들어 둔 검증 함수를 활용하여 이메일을 파싱합니다.
    email = verify_access_token(token)
    
    # 토큰에 문제가 있어 이메일이 파싱되지 않는 경우 즉시 예외를 발생시켜 API 진입을 차단합니다.
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증 토큰이 유효하지 않거나 만료되었습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    return email