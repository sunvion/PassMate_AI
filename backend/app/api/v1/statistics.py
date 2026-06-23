# backend/app/api/v1/statistics.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Any, List, Optional

from app.db.session import get_db
from app.core.security import get_current_user
from app.crud.statistics import crud_statistics
from app.schemas.statistics import (
    DashboardSummaryResponse, 
    ExamSessionDetailResponse,
    WrongExamSummaryResponse,        # 🆕 추가 임포트
    WrongQuestionDetailResponse      # 🆕 추가 임포트
)

router = APIRouter()

@router.get("/today-summary", response_model=DashboardSummaryResponse, summary="홈 대시보드 학습 요약 정보 반환")
async def read_dashboard_summary(
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """사용자의 전체 풀이 이력을 실시간으로 집계하여 총 풀이 문제 수, 평균 정답률, 최근 응시 일시를 넘겨줍니다."""
    user_res = await db.execute(text("SELECT id FROM users WHERE email = :email"), {"email": current_user})
    user_id = user_res.scalar()
    if not user_id:
        raise HTTPException(status_code=404, detail="구글 인증 정보와 매칭되는 시스템 유저를 찾을 수 없습니다.")

    summary = await crud_statistics.get_user_dashboard_summary(db=db, user_id=user_id)
    return summary


@router.get("/history-details", response_model=List[ExamSessionDetailResponse], summary="유저 전체 풀이 이력 및 문항 상세 조회")
async def read_history_details(
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """유저가 지금까지 풀이한 데이터를 동적으로 그루핑하여 시험지 세션 정보와 문항 상세 정보를 반환합니다."""
    user_res = await db.execute(text("SELECT id FROM users WHERE email = :email"), {"email": current_user})
    user_id = user_res.scalar()
    if not user_id:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")

    details = await crud_statistics.get_user_exam_history_details(db=db, user_id=user_id)
    return details


@router.delete("/history", summary="유저 전체 풀이 이력 초기화")
async def clear_history(
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """사용자의 문제 채점 및 성적 히스토리 데이터를 영구적으로 완전히 삭제하여 초기화합니다."""
    user_res = await db.execute(text("SELECT id FROM users WHERE email = :email"), {"email": current_user})
    user_id = user_res.scalar()
    if not user_id:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")

    await crud_statistics.clear_user_history(db=db, user_id=user_id)
    return {"message": "전체 풀이 이력이 성공적으로 초기화되었습니다."}


# 🆕 오답노트 라우터 1: 전체 오답 목록 요약 통계 그룹 리스트 조회
@router.get("/wrong-notebook", response_model=List[WrongExamSummaryResponse], summary="오답노트 메인 목록 요약 조회")
async def read_wrong_notebook_list(
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """현재 로그인 유저가 틀린(is_correct=False) 문제들을 과목/직렬별로 묶어 카운트 통계를 리턴합니다."""
    user_res = await db.execute(text("SELECT id FROM users WHERE email = :email"), {"email": current_user})
    user_id = user_res.scalar()
    if not user_id:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")

    return await crud_statistics.get_user_wrong_summary(db=db, user_id=user_id)


# 🆕 오답노트 라우터 2: 선택한 특정 시험 카테고리에 해당하는 오답들의 문항 원본 상세 조회
@router.get("/wrong-notebook/details", response_model=List[WrongQuestionDetailResponse], summary="특정 과목 오답노트 상세 조회")
async def read_wrong_notebook_details(
    exam_type: str = Query(..., description="시험 종류 필터 (예: CS_GENERAL)"),
    subject: str = Query(..., description="과목 분류 명칭 필터 (예: 컴퓨터일반)"),
    year: Optional[int] = Query(None, description="선택적 기출 연도 필터"),
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """사용자가 선택한 특정 시험 분류군의 모든 오답들과 해설, 원본 보기 포맷 데이터를 결합하여 반환합니다."""
    user_res = await db.execute(text("SELECT id FROM users WHERE email = :email"), {"email": current_user})
    user_id = user_res.scalar()
    if not user_id:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")

    return await crud_statistics.get_user_wrong_details(
        db=db, user_id=user_id, exam_type=exam_type, subject=subject, year=year
    )