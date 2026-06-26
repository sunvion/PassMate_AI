# backend/app/api/v1/statistics.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Any, List, Optional

from app.db.session import get_db
from app.core.security import get_current_user
from app.crud.statistics import crud_statistics
from app.schemas.statistics import (
    DashboardSummaryResponse, 
    ExamSessionDetailResponse,
    WrongNotebookListElement,       # 🆕 신규 목록 엘리먼트 DTO
    WrongNotebookDetailResponse,     # 🆕 신규 상세 응답 DTO
    WrongNotebookUpdateTitleRequest, # 🆕 신규 제목 변경 바디 DTO
    ChapterWrongCountResponse
)

router = APIRouter()
wrong_notebook_router = APIRouter()  # 🆕 독립형 오답노트 전용 라우터 독립 분리 개설

# =================================================================
# 📊 1. 홈 대시보드 & 성적표 & 진도율 도메인 API (router)
# =================================================================

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


@router.get("/latest-progress", summary="대시보드용 최근 학습 진행 상태 조회 (이어서 학습하기)")
async def read_latest_progress(
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    🆕 [신규 추가]
    유저가 한 문제씩 풀기 도중 페이지를 이탈했을 때, 가장 최근에 업데이트된 과목 진도 명세를 1건 추출합니다.
    이 데이터는 대시보드의 '이어서 학습하기' 링크 및 컨텍스트 매핑에 활용됩니다.
    """
    user_res = await db.execute(text("SELECT id FROM users WHERE email = :email"), {"email": current_user})
    user_id = user_res.scalar()
    if not user_id: 
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")
    
    query = text("""
        SELECT exam_type, subject, last_question_id, solved_count, updated_at
        FROM user_learning_progress
        WHERE user_id = :user_id
        ORDER BY updated_at DESC
        LIMIT 1
    """)
    res = await db.execute(query, {"user_id": user_id})
    row = res.first()
    
    if not row:
        return None  # 학습 기록이 전혀 없는 신규 유저인 경우 프론트엔드가 버튼을 비활성화할 수 있도록 null 처리
        
    return {
        "exam_type": row.exam_type,
        "subject": row.subject,
        "last_question_id": row.last_question_id,
        "solved_count": row.solved_count,
        "updated_at": row.updated_at
    }


@router.get("/chapters", response_model=List[ChapterWrongCountResponse], summary="챕터별 오답 개수 집계 조회")
async def read_wrong_chapters(
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """사용자가 과목별/챕터별로 얼마나 많은 문제를 틀렸는지 집계하여 약점 분석 컴포넌트에 바인딩합니다."""
    user_res = await db.execute(text("SELECT id FROM users WHERE email = :email"), {"email": current_user})
    user_id = user_res.scalar()
    if not user_id:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")

    return await crud_statistics.get_wrong_count_by_chapter(db=db, user_id=user_id)


# =================================================================
# 🆕 2. 회차별 독립형 오답노트 관리 API (wrong_notebook_router)
# =================================================================

@wrong_notebook_router.get("", response_model=List[WrongNotebookListElement], summary="오답노트 목록 조회")
async def read_wrong_notebooks(
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """현재 로그인한 사용자가 발급받은 전체 오답노트의 요약 목록(틀린 문제 수, 안 푼 문제 수 포함)을 조회합니다."""
    user_res = await db.execute(text("SELECT id FROM users WHERE email = :email"), {"email": current_user})
    user_id = user_res.scalar()
    if not user_id:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")

    return await crud_statistics.get_wrong_notebooks_list(db=db, user_id=user_id)


@wrong_notebook_router.get("/{wrong_notebook_id}", response_model=WrongNotebookDetailResponse, summary="오답노트 상세 조회")
async def read_wrong_notebook_detail(
    wrong_notebook_id: int,
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """특정 오답노트 내부의 원본 문제 문항 리스트 및 내가 마킹한 오답, 정답 분석 리포트를 일괄 상세 조회합니다."""
    user_res = await db.execute(text("SELECT id FROM users WHERE email = :email"), {"email": current_user})
    user_id = user_res.scalar()
    if not user_id:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")

    detail = await crud_statistics.get_wrong_notebook_detail(db=db, user_id=user_id, notebook_id=wrong_notebook_id)
    if not detail:
        raise HTTPException(status_code=404, detail="해당 오답노트가 존재하지 않거나 접근 권한이 없습니다.")
    return detail


@wrong_notebook_router.patch("/{wrong_notebook_id}", summary="오답노트 이름 수정")
async def update_wrong_notebook_title(
    wrong_notebook_id: int,
    payload: WrongNotebookUpdateTitleRequest,
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """사용자가 직접 오답노트의 고유 타이틀 명칭을 커스텀하게 수정합니다."""
    user_res = await db.execute(text("SELECT id FROM users WHERE email = :email"), {"email": current_user})
    user_id = user_res.scalar()
    if not user_id:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")

    success = await crud_statistics.update_wrong_notebook_title(
        db=db, user_id=user_id, notebook_id=wrong_notebook_id, title=payload.title
    )
    if not success:
        raise HTTPException(status_code=404, detail="오답노트를 찾을 수 없거나 타이틀 수정 권한이 없습니다.")
    return {"message": "오답노트 제목이 수정되었습니다."}


@wrong_notebook_router.delete("/{wrong_notebook_id}", summary="오답노트 개별 삭제")
async def delete_wrong_notebook(
    wrong_notebook_id: int,
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """특정 회차의 오답노트 세션을 개별 삭제합니다. (전체 풀이 이력 로그의 유실 없이 오답노트만 격리 삭제)"""
    user_res = await db.execute(text("SELECT id FROM users WHERE email = :email"), {"email": current_user})
    user_id = user_res.scalar()
    if not user_id:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")

    success = await crud_statistics.delete_wrong_notebook(db=db, user_id=user_id, notebook_id=wrong_notebook_id)
    if not success:
        raise HTTPException(status_code=404, detail="오답노트를 찾을 수 없거나 삭제 권한이 없습니다.")
    return {"message": "오답노트가 삭제되었습니다."}