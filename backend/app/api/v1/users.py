# backend/app/api/v1/users.py
from fastapi import APIRouter, Depends, HTTPException, status
# 💡 Session 대신 AsyncSession을 임포트합니다.
from sqlalchemy.ext.asyncio import AsyncSession 

from app.db.session import get_db
from app.core.security import get_current_user
from app.crud import user as user_crud
from app.schemas.user import UserResponse  # 혹은 유저 응답 스케마 명칭

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(                     
    current_user: str = Depends(get_current_user),  
    db: AsyncSession = Depends(get_db)              
):
    """
    현재 로그인한 유저의 프로필 정보 조회 API
    Header에 'Authorization: Bearer <우리_JWT_토큰>' 필요
    """
    db_user = await user_crud.get_user_by_email(db, email=current_user) 
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
        
    return db_user