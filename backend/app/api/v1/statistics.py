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
    ChapterWrongCountResponse,
    LearningProgressSaveRequest
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
    🎯 [시험별/과목별 최신 진도 리스트 추출 분기 개정 완료]
    절대적 최신 1개(LIMIT 1)가 아닌, 사용자가 응시한 모든 시험(직렬)/과목별 최신 상태를 
    각각 1개씩 리스트(Array) 포맷으로 일괄 반환하도록 구조를 고도화했습니다.
    """
    user_res = await db.execute(text("SELECT id FROM users WHERE email = :email"), {"email": current_user})
    user_id = user_res.scalar()
    if not user_id:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")
    
    # 하위 호환성 가드: 현재 가동 중인 프론트 컴퓨터 DB에 'year' 컬럼이 실제로 생성되어 있는지 체크
    column_check = await db.execute(text("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'user_learning_progress' AND column_name = 'year'
        )
    """))
    has_year_column = column_check.scalar()

    if has_year_column:
        # 🅰️ [최신 스키마 버전]: DISTINCT ON을 통해 시험 종류 및 과목별 최신 스냅샷 한 행씩 분리 추출
        query = text("""
            WITH latest_progress AS (
                SELECT DISTINCT ON (ulp.exam_type, ulp.subject)
                    ulp.id, ulp.exam_type, ulp.subject, ulp.year, ulp.last_question_id, ulp.solved_count, ulp.updated_at,
                    (SELECT COUNT(*) FROM questions q 
                        WHERE q.exam_type = ulp.exam_type 
                        AND q.subject = ulp.subject 
                        AND COALESCE(q.year, 0) = ulp.year) as total_count
                FROM user_learning_progress ulp
                WHERE ulp.user_id = :user_id 
                     AND ulp.exam_type != 'DRIVERS_LICENSE_1'  -- 운전면허 데이터는 조회 대상에서 생략
                ORDER BY ulp.exam_type, ulp.subject, ulp.updated_at DESC
            )
            SELECT * FROM latest_progress ORDER BY updated_at DESC;
        """)
        res = await db.execute(query, {"user_id": user_id})
        rows = res.all()
        
        return [
            {
                "attempt_id": row.id,
                "exam_type": row.exam_type,
                "subject": row.subject,
                "year": None if row.year == 0 else row.year,
                "exam_id": row.year,
                "last_question_id": row.last_question_id,
                "solved_count": row.solved_count,
                "total_count": row.total_count,
                "updated_at": row.updated_at
            }
            for row in rows
        ]
    else:
        # 🅱️ [옛날 스키마 보존 버전]: year 컬럼 조회를 배제하고 exam_type, subject 별 최신 상태 병렬 추출
        query = text("""
            WITH latest_progress AS (
                SELECT DISTINCT ON (ulp.exam_type, ulp.subject)
                       ulp.id, ulp.exam_type, ulp.subject, ulp.last_question_id, ulp.solved_count, ulp.updated_at,
                       (SELECT COUNT(*) FROM questions q WHERE q.exam_type = ulp.exam_type AND q.subject = ulp.subject) as total_count
                FROM user_learning_progress ulp
                WHERE ulp.user_id = :user_id
                     AND ulp.exam_type != 'DRIVERS_LICENSE_1'
                ORDER BY ulp.exam_type, ulp.subject, ulp.updated_at DESC
            )
            SELECT * FROM latest_progress ORDER BY updated_at DESC;
        """)
        res = await db.execute(query, {"user_id": user_id})
        rows = res.all()
        
        return [
            {
                "attempt_id": row.id,
                "exam_type": row.exam_type,
                "subject": row.subject,
                "year": None,
                "exam_id": 0,
                "last_question_id": row.last_question_id,
                "solved_count": row.solved_count,
                "total_count": row.total_count,
                "updated_at": row.updated_at
            }
            for row in rows
        ]


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


@router.post("/progress", summary="채점 없이 학습 진행 상태만 중간 저장 (나중에 학습 기능 대응)")
async def save_learning_progress(
    payload: LearningProgressSaveRequest,
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    한 문제씩 풀기 화면에서 사용자가 '나중에 학습' 버튼을 눌러 이탈할 때 호출됩니다.
    채점(오답 처리)이나 역사적 풀이 로그 적재를 일체 배제하고, 오직 대시보드 포인터 위치만 안전하게 세이브합니다.
    """
    # 1. 토큰 유효성 검증 및 유저 매핑
    user_res = await db.execute(text("SELECT id FROM users WHERE email = :email"), {"email": current_user})
    user_id = user_res.scalar()
    if not user_id:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")

    # 2. 순수 UPSERT 쿼리 실행 (ON CONFLICT 구문을 통해 기존 행이 있으면 덮어쓰고 없으면 인서트)
    query = text("""
        INSERT INTO user_learning_progress (user_id, exam_type, subject, year, last_question_id, solved_count, updated_at)
        VALUES (:user_id, :exam_type, :subject, COALESCE(:year, 0), :last_question_id, :solved_count, CURRENT_TIMESTAMP)
        ON CONFLICT (user_id, exam_type, subject, year) 
        DO UPDATE SET 
            last_question_id = EXCLUDED.last_question_id,
            solved_count = EXCLUDED.solved_count,
            updated_at = CURRENT_TIMESTAMP
    """)
    
    await db.execute(query, {
        "user_id": user_id,
        "exam_type": payload.exam_type,
        "subject": payload.subject,
        "year": payload.year,
        "last_question_id": payload.last_question_id,
        "solved_count": payload.solved_count  # 프론트엔드가 계산해서 넘겨준 현재까지의 정밀 진도 수 박제
    })
    
    # 영구 저장 커밋
    await db.commit()
    
    return {"status": "success", "message": "학습 진행 상태가 안전하게 중간 저장되었습니다."}


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