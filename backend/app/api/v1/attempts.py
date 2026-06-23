# backend/app/api/v1/attempts.py
import re
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Any
from datetime import datetime

from app.db.session import get_db
from app.core.security import get_current_user  # JWT 토큰 유효성 검증 및 유저 주입 의존성
from app.crud.question import crud_question
from app.crud.history import crud_history
from app.schemas.history import (
    SingleAttemptCreate,
    BulkAttemptCreate,
    AttemptResultResponse,
    BulkAttemptResultResponse,
    ScoreSummaryResponse
)

router = APIRouter()


def check_answers_match(user_ans: Any, correct_ans: Any, is_civil_service: bool = False) -> bool:
    """
    시험 유형에 맞춰 정답을 검증합니다.
    - 운전면허 (Default): 요구하는 복수 정답과 완벽히 일치해야 함 (user_set == correct_set)
    - 공무원 (is_civil_service=True): 복수 정답 중 하나만 맞혀도 인정 (user_set이 correct_set의 부분집합)
    """
    def normalize_to_set(ans: Any) -> set:
        if ans is None:
            return set()
        if isinstance(ans, list):
            ans = "".join(map(str, ans))
        return set(re.findall(r'[1-5]', str(ans)))

    user_set = normalize_to_set(user_ans)
    correct_set = normalize_to_set(correct_ans)

    # 아무것도 마킹하지 않은 경우 무조건 오답 처리
    if not user_set or not correct_set:
        return False

    if is_civil_service:
        # 🌟 공무원 시험 규격: 유저가 제출한 번호들이 정답 집합 내에 존재하면 정답 인정
        # 예: 정답이 {1, 2}일 때 유저가 {1}만 고르거나, {2}만 고르거나, {1, 2}를 고르면 정답 처리
        # (단, {1, 3}처럼 틀린 번호가 섞여 있으면 False)
        return user_set.issubset(correct_set)
    else:
        # 🌟 운전면허 시험 규격: 복수 정답을 모두 완벽하게 맞혀야만 인정
        return user_set == correct_set


@router.post("/single", response_model=AttemptResultResponse, summary="단일 문제 즉시 채점 및 기록 (옵션 A)")
async def submit_single_question(
    payload: SingleAttemptCreate,
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    한 문항을 풀 때마다 실시간으로 보기를 제출하여 즉시 채점 결과를 반환받고 유저 풀이 이력에 적재합니다.
    """
    # OAuth 이메일 대응 가드: 구글 이메일 문자열을 기반으로 실제 DB상의 정수형 user_id(PK) 조회
    user_res = await db.execute(text("SELECT id FROM users WHERE email = :email"), {"email": current_user})
    user_id = user_res.scalar()
    if not user_id:
        raise HTTPException(status_code=404, detail="구글 인증 정보와 매칭되는 시스템 유저를 찾을 수 없습니다.")

    question = await crud_question.get_by_id(db, question_id=payload.question_id)
    if not question:
        raise HTTPException(status_code=404, detail="존재하지 않는 문제입니다.")

    # 🌟 [시험 유형 판별]: 문제의 exam_type이나 subject를 기반으로 공무원 시험 여부 확인
    is_civil_service = (
        getattr(question, 'exam_type', '') == "CS_GENERAL" or 
        "컴퓨터일반" in getattr(question, 'subject', '')
    )

    # 분기된 채점 로직 적용
    is_correct = check_answers_match(payload.selected_option, question.answer, is_civil_service=is_civil_service)

    # 🌟 [핵심 교정]: commit이 발생하여 객체가 만료되기 전에 리턴할 데이터를 미리 로컬 변수에 스냅샷 백업
    q_id = question.id
    q_answer = question.answer
    q_explanation = question.explanation

    # 히스토리 테이블에 결과 스냅샷 저장 (이 안에서 db.commit이 일어나며 question 객체가 만료됨)
    await crud_history.create_history(
        db=db, user_id=user_id, attempt=payload, question=question, is_correct=is_correct
    )

    # 안전하게 백업된 순수 파이썬 변수 데이터를 사용하여 안전하게 리턴
    return AttemptResultResponse(
        question_id=q_id,
        is_correct=is_correct,
        correct_answer=q_answer,
        explanation=q_explanation
    )


@router.post("/bulk", response_model=BulkAttemptResultResponse, summary="시험지 전체 일괄 채점 및 기록 (옵션 B)")
async def submit_bulk_exam(
    payload: BulkAttemptCreate,
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    모의고사 스트리밍/스크롤 모드에서 사용자가 '전체 채점하기'를 눌렀을 때,
    20개 문항의 정답 여부를 일괄 계산하여 전체 스코어보드 결과 리스트를 생성 및 영구 적재합니다.
    """
    if not payload.attempts:
        raise HTTPException(status_code=400, detail="제출된 답안 데이터가 비어 있습니다.")

    # OAuth 이메일 대응 가드: 구글 이메일 문자열을 기반으로 실제 DB상의 정수형 user_id(PK) 조회
    user_res = await db.execute(text("SELECT id FROM users WHERE email = :email"), {"email": current_user})
    user_id = user_res.scalar()
    if not user_id:
        raise HTTPException(status_code=404, detail="구글 인증 정보와 매칭되는 시스템 유저를 찾을 수 없습니다.")

    results = []
    correct_count = 0
    total_questions = len(payload.attempts)
    
    # 동일 세션의 제출 시간 동기화를 위해 현재 타임스탬프 고정 적용
    shared_submitted_at = datetime.now()

    for attempt in payload.attempts:
        question = await crud_question.get_by_id(db, question_id=attempt.question_id)
        if not question:
            continue
        
        # 🌟 [시험 유형 판별]: 문제의 exam_type이나 subject를 기반으로 공무원 시험 여부 확인
        is_civil_service = (
            getattr(question, 'exam_type', '') == "CS_GENERAL" or 
            "컴퓨터일반" in getattr(question, 'subject', '')
        )

        # 분기된 채점 로직 적용
        is_correct = check_answers_match(attempt.selected_option, question.answer, is_civil_service=is_civil_service)
        if is_correct:
            correct_count += 1

        # 🌟 [핵심 교정]: 루프 내부에서도 커밋 전 데이터를 미리 스냅샷 백업
        q_id = question.id
        q_answer = question.answer
        q_explanation = question.explanation

        # 개별 문항 풀이 기록 적재 (이 내부에서 커밋이 일어나도 안전하게 방어됨)
        await crud_history.create_history(
            db=db, user_id=user_id, attempt=attempt, question=question, is_correct=is_correct
        )
        
        results.append(
            AttemptResultResponse(
                question_id=q_id,
                is_correct=is_correct,
                correct_answer=q_answer,
                explanation=q_explanation
            )
        )

    # 20문항 공무원 시험지 규격 대응 과목 점수 환산 알고리즘 (개당 5점)
    calculated_score = correct_count * 5 if total_questions == 20 else int((correct_count / total_questions) * 100)

    return BulkAttemptResultResponse(
        total_questions=total_questions,
        correct_count=correct_count,
        score=calculated_score,
        results=results
    )


@router.get("/scores", response_model=List[ScoreSummaryResponse], summary="유저 모의고사 성적 목록 리스트 조회")
async def read_my_scores(
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    사용자가 마이페이지 대시보드에 접근할 때 지금까지 통과한 기출 모의고사 세션 정보와
    환산 점수, 제출 일시 리스트 통계를 가공하여 리턴합니다.
    """
    # OAuth 이메일 대응 가드: 구글 이메일 문자열을 기반으로 실제 DB상의 정수형 user_id(PK) 조회
    user_res = await db.execute(text("SELECT id FROM users WHERE email = :email"), {"email": current_user})
    user_id = user_res.scalar()
    if not user_id:
        raise HTTPException(status_code=404, detail="구글 인증 정보와 매칭되는 시스템 유저를 찾을 수 없습니다.")

    score_summaries = await crud_history.get_user_scores_summary(db, user_id=user_id)
    return score_summaries