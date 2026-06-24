# backend/app/api/v1/attempts.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Any
from datetime import datetime
import json  # 💡 JSONB 규격 가공 대응

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

    # 💡 [시험 직렬별 복수 정답 알고리즘 분기 적용]
    if question.exam_type == "DRIVERS_LICENSE_1":
        # 🚗 운전면허 학과: 복수 정답일 때 정답 요소가 완전히 일치해야 정답 인정
        is_correct = set(payload.selected_option) == set(question.answer)
    else:
        # 🏛️ 공무원 기출(CS_GENERAL, CS_LOCAL): 복수 정답 중 하나만 골라도 정답으로 유연하게 인정 (부분집합 판별)
        is_correct = (
            bool(payload.selected_option) and 
            set(payload.selected_option).issubset(set(question.answer))
        )

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
    동시에 틀린 문제와 안 푼 문제를 모아 독립된 고유 오답노트 세션을 자동 생성합니다.
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

    # 오답노트 아이템으로 이관할 타겟 문항 홀딩 큐
    wrong_items_queue = []

    for attempt in payload.attempts:
        question = await crud_question.get_by_id(db, question_id=attempt.question_id)
        if not question:
            continue
        
        # 💡 [시험 직렬별 복수 정답 알고리즘 일괄 적용]
        if question.exam_type == "DRIVERS_LICENSE_1":
            is_correct = set(attempt.selected_option) == set(question.answer)
        else:
            is_correct = (
                bool(attempt.selected_option) and 
                set(attempt.selected_option).issubset(set(question.answer))
            )
        
        if is_correct:
            correct_count += 1

        # 💡 [오답노트 조건 소싱 분기]: 안 푼 문제(unsolved)와 틀린 문제(wrong) 분류 가드
        is_unsolved = not attempt.selected_option or len(attempt.selected_option) == 0
        if is_unsolved:
            wrong_items_queue.append((attempt.question_id, attempt.selected_option, is_correct, "unsolved"))
        elif not is_correct:
            wrong_items_queue.append((attempt.question_id, attempt.selected_option, is_correct, "wrong"))

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

    # 🆕 🎯 [독립형 오답노트 세션 트랜잭션 일괄 처리 엔진]
    if wrong_items_queue and total_questions > 0:
        first_q = await crud_question.get_by_id(db, question_id=payload.attempts[0].question_id)
        if first_q:
            # 1. 도메인별 기본 타이틀 정의 명세 바인딩
            if first_q.exam_type in ["CS_GENERAL", "CS_NATIONAL"]:
                base_title = f"{first_q.year} 국가직 {first_q.subject} 오답노트"
            elif first_q.exam_type == "CS_LOCAL":
                base_title = f"{first_q.year} 지방직 {first_q.subject} 오답노트"
            elif first_q.exam_type == "DRIVERS_LICENSE_1":
                base_title = "운전면허 필기 오답노트"
            else:
                base_title = f"{first_q.subject} 오답노트"

            # 2. 동일한 기본 제목 존재 시 (2), (3) 접미사를 붙여주는 중복 회피 알고리즘
            title_check = text("SELECT title FROM wrong_notebooks WHERE user_id = :user_id AND title LIKE :pat")
            t_res = await db.execute(title_check, {"user_id": user_id, "pat": f"{base_title}%"})
            existing_titles = [r[0] for r in t_res.all()]
            
            final_title = base_title
            if base_title in existing_titles:
                suffix = 2
                while f"{base_title} ({suffix})" in existing_titles:
                    suffix += 1
                final_title = f"{base_title} ({suffix})"

            # 3. 마스터 wrong_notebooks 인서트 후 고유 ID 생성 받아오기
            nb_ins = text("""
                INSERT INTO wrong_notebooks (user_id, title, exam_type, year, subject, created_at)
                VALUES (:user_id, :title, :exam_type, :year, :subject, :created_at) RETURNING id
            """)
            nb_res = await db.execute(nb_ins, {
                "user_id": user_id, "title": final_title, "exam_type": first_q.exam_type,
                "year": first_q.year, "subject": first_q.subject, "created_at": shared_submitted_at
            })
            notebook_id = nb_res.scalar()

            # 4. 소싱된 오답/미풀이 하위 문항 리스트 벌크 적재 진행
            for q_id, sel_opt, is_corr, stat in wrong_items_queue:
                item_ins = text("""
                    INSERT INTO wrong_notebook_items (notebook_id, question_id, selected_option, is_correct, status, submitted_at)
                    VALUES (:notebook_id, :question_id, :selected_option, :is_correct, :status, :submitted_at)
                """)
                await db.execute(item_ins, {
                    "notebook_id": notebook_id, "question_id": q_id, "selected_option": json.dumps(sel_opt),
                    "is_correct": is_corr, "status": stat, "submitted_at": shared_submitted_at
                })
            
            # 모든 히스토리 + 오답노트 적재가 완벽히 성공했을 때 최종 단 1회 커밋(Commit)하여 정합성 보장
            await db.commit()

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