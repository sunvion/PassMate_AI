# backend/app/api/v1/users.py
from fastapi import APIRouter, Depends, HTTPException, status
# 💡 Session 대신 AsyncSession을 임포트합니다.
from sqlalchemy.ext.asyncio import AsyncSession 

from app.db.session import get_db
from app.core.security import get_current_user
from app.crud import user as user_crud
from app.schemas.user import UserResponse  # 혹은 유저 응답 스케마 명칭

from app.schemas.user import UserResponse, UserUpdateRequest, UserMe

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(                     # 1️⃣ 일반 def를 'async def'로 변경
    current_user: str = Depends(get_current_user),  
    db: AsyncSession = Depends(get_db)               # 2️⃣ 타입을 Session에서 'AsyncSession'으로 변경
):
    """
    현재 로그인한 유저의 프로필 정보 조회 API
    Header에 'Authorization: Bearer <우리_JWT_토큰>' 필요
    """
    # 3️⃣ 🌟 [핵심] 함수 호출 앞에 반드시 'await'을 추가합니다!
    db_user = await user_crud.get_user_by_email(db, email=current_user) 
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
        
    return db_user

@router.put("/me", response_model=UserResponse, summary="내 프로필(닉네임/이미지) 수정 API")
async def update_my_profile(
    payload: UserUpdateRequest,
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    [PUT] /api/v1/users/me
    JWT 토큰 인증 후, 요청 본문에 담긴 새로운 닉네임이나 프로필 이미지로 정보를 수정합니다.
    """
    db_user = await user_crud.get_user_by_email(db, email=current_user)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Pydantic 스키마를 딕셔너리로 변환하여 CRUD에 전달 (전송된 값만 추출)
    update_dict = payload.model_dump(exclude_unset=True)
    
    # 🌟 비동기 함수이므로 반드시 'await' 기입
    updated_user = await user_crud.update_user_profile(db, db_user=db_user, update_data=update_dict)
    return updated_user


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT, summary="회원 탈퇴 API")
async def withdraw_my_account(
    current_user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    [DELETE] /api/v1/users/me
    JWT 토큰 인증 후, 해당 유저의 계정과 연관된 모든 데이터를 DB에서 즉시 영구 삭제합니다.
    """
    db_user = await user_crud.get_user_by_email(db, email=current_user)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # 🌟 비동기 계정 삭제 처리
    await user_crud.delete_user_account(db, db_user=db_user)
    return None  # HTTP 204 No Content 응답은 본문을 반환하지 않습니다.