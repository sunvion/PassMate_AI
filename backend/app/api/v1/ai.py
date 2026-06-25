# app/api/v1/ai.py
import traceback
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession  # 💡 비동기 세션 타입 임포트
from sqlalchemy import select                      # 💡 2.0 스타일 select 임포트

from app.db.session import get_db
from app.schemas.ai import AIRecommendationListResponse
from app.services import ai_service
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/recommended-questions", response_model=AIRecommendationListResponse)
async def get_recommended_questions(  # 💡 async def 로 전환
    question_id: int = Query(..., description="기준이 되는 틀린 문제 ID"),
    limit: int = Query(3, ge=1, le=10, description="추천 문항 수 (기본 3개)"),
    db: AsyncSession = Depends(get_db), # 💡 AsyncSession 주입
    current_user: any = Depends(get_current_user)
):
    try:
        if isinstance(current_user, str):
            if "@" in current_user:
                # 💡 비동기 방식 유저 조회 처리 (await db.execute)
                result = await db.execute(select(User).filter(User.email == current_user))
                db_user = result.scalars().first()
            else:
                try:
                    result = await db.execute(select(User).filter(User.id == int(current_user)))
                    db_user = result.scalars().first()
                except ValueError:
                    db_user = None
            
            if not db_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, 
                    detail="토큰 인증에 성공했으나, 데이터베이스에서 유저 정보를 찾을 수 없습니다."
                )
            target_user_id = db_user.id
        else:
            target_user_id = current_user.id

        # 🎯 비동기로 서비스 레이어 호출 (await 추가)
        recommendations = await ai_service.get_recommended_questions(
            db=db, 
            user_id=target_user_id, 
            question_id=question_id, 
            limit=limit
        )
        return recommendations

    except HTTPException as e:
        raise e
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        print("\n" + "="*60)
        print("🚨 [AI DOMAIN ERROR] 예외 발생 상세 추적:")
        traceback.print_exc()
        print("="*60 + "\n")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="AI 추천 로직 처리 중 내부 서버 에러가 발생했습니다."
        )