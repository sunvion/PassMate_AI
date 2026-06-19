from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.crud import user as user_crud
from app.schemas.user import UserResponse  # Pydantic 스키마 가정 
from app.core.security import get_current_user  # 공통 인증 의존성 함수가 있다고 가정

router = APIRouter()

@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: str = Depends(get_current_user),  # 토큰 파싱 및 유저 이메일 반환 의존성 
    db: Session = Depends(get_db)
):
    """
    현재 로그인한 유저의 프로필 정보 조회 API
    Header에 'Authorization: Bearer <우리_JWT_토큰>' 필요
    """
    # 의존성(get_current_user)을 통해 토큰에서 추출한 email로 DB 조회
    db_user = user_crud.get_user_by_email(db, email=current_user) 
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
        
    # Pydantic 스키마 규격에 맞춰 자동으로 리턴 (email, name, picture 등) 
    return db_user