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
    동시에 '이어서 학습하기'를 위한 진도율 자동 갱신(UPSERT) 및 실시간 오답 노출 번호 지정을 처리합니다.
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
        is_correct = set(payload.selected_option) == set(question.answer)
    else:
        is_correct = (
            bool(payload.selected_option) and 
            set(payload.selected_option).issubset(set(question.answer))
        )

    # 🌟 commit이 발생하여 객체가 만료되기 전에 리턴 및 인서트할 데이터를 미리 로컬 변수에 스냅샷 백업
    q_id = question.id
    q_answer = question.answer
    q_explanation = question.explanation
    
    # 🆕 [교정]: 단일 문항의 원본 문제 번호를 소싱해 둡니다. (기본값 1)
    q_num = getattr(question, "number", 1)

    # 1. 히스토리 테이블에 결과 스냅샷 저장
    await crud_history.create_history(
        db=db, user_id=user_id, attempt=payload, question=question, is_correct=is_correct
    )

    # 2. [이어서 학습하기] 진행 상태 자동 누적 적재 (고속 인덱싱 기반 UPSERT 작동)
    progress_query = text("""
        INSERT INTO user_learning_progress (user_id, exam_type, subject, last_question_id, solved_count, updated_at)
        VALUES (:user_id, :exam_type, :subject, :last_question_id, 1, CURRENT_TIMESTAMP)
        ON CONFLICT (user_id, exam_type, subject) 
        DO UPDATE SET 
            last_question_id = EXCLUDED.last_question_id,
            solved_count = user_learning_progress.solved_count + 1,
            updated_at = CURRENT_TIMESTAMP
    """)
    await db.execute(progress_query, {
        "user_id": user_id, 
        "exam_type": question.exam_type,
        "subject": question.subject, 
        "last_question_id": q_id
    })

    # 3. [개별 풀이 모드 전용] 하루 단위 오답노트 실시간 누적 및 워프 ID 추출 파이프라인
    wrong_notebook_id = None
    if not is_correct:
        today_str = datetime.now().strftime("%Y-%m-%d")
        if question.exam_type in ["CS_GENERAL", "CS_NATIONAL"]:
            target_title = f"{today_str} 국가직 {question.subject} 오답노트 (개별풀이)"
        elif question.exam_type == "CS_LOCAL":
            target_title = f"{today_str} 지방직 {question.subject} 오답노트 (개별풀이)"
        else:
            target_title = f"{today_str} {question.subject} 오답노트 (개별풀이)"

        # 오늘 생성된 고유 오답노트 존재 여부 스캔
        exist_check = text("SELECT id FROM wrong_notebooks WHERE user_id = :user_id AND title = :title")
        exist_res = await db.execute(exist_check, {"user_id": user_id, "title": target_title})
        wrong_notebook_id = exist_res.scalar()

        if not wrong_notebook_id:
            # 존재하지 않는다면 오늘 자 마스터 오답노트 카드 선제 발급
            nb_ins = text("""
                INSERT INTO wrong_notebooks (user_id, title, exam_type, year, subject, created_at)
                VALUES (:user_id, :title, :exam_type, :year, :subject, CURRENT_TIMESTAMP) RETURNING id
            """)
            nb_res = await db.execute(nb_ins, {
                "user_id": user_id, "title": target_title, "exam_type": question.exam_type,
                "year": question.year, "subject": question.subject
            })
            wrong_notebook_id = nb_res.scalar()

        # 당일 중복 문항 적재 방지용 유니크 가드 검증
        item_check = text("SELECT id FROM wrong_notebook_items WHERE notebook_id = :nb_id AND question_id = :q_id")
        item_exist = await db.execute(item_check, {"nb_id": wrong_notebook_id, "q_id": q_id})
        
        if not item_exist.scalar():
            # 💡 [SQL 수정]: 저장 인서트 절에 question_number 바인딩 매핑 추가
            item_ins = text("""
                INSERT INTO wrong_notebook_items (notebook_id, question_id, question_number, selected_option, is_correct, status, submitted_at)
                VALUES (:notebook_id, :question_id, :question_number, :selected_option, :is_correct, 'wrong', CURRENT_TIMESTAMP)
            """)
            await db.execute(item_ins, {
                "notebook_id": wrong_notebook_id, 
                "question_id": q_id, 
                "question_number": q_num,  # 🆕 원본 문제 번호 저장
                "selected_option": json.dumps(payload.selected_option), 
                "is_correct": is_correct
            })

    # 트랜잭션 정상 반영 커밋
    await db.commit()

    # 안전하게 백업된 데이터와 워프용 오답노트 ID를 결합하여 반환
    return AttemptResultResponse(
        question_id=q_id,
        is_correct=is_correct,
        correct_answer=q_answer,
        explanation=q_explanation,
        wrong_notebook_id=wrong_notebook_id
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

    # 오답노트 아이템으로 이관할 타겟 문항 홀딩 큐
    wrong_items_queue = []

    # 💡 [교정]: enumerate를 동원하여 사용자가 시험을 본 원본 순서(문제지 상의 1번 ~ 20/40번 위치)를 보존합니다.
    for idx, attempt in enumerate(payload.attempts, start=1):
        question = await crud_question.get_by_id(db, question_id=attempt.question_id)
        if not question:
            continue
        
        # [시험 직렬별 복수 정답 알고리즘 일괄 적용]
        if question.exam_type == "DRIVERS_LICENSE_1":
            is_correct = set(attempt.selected_option) == set(question.answer)
        else:
            is_correct = (
                bool(attempt.selected_option) and 
                set(attempt.selected_option).issubset(set(question.answer))
            )
        
        if is_correct:
            correct_count += 1

        # [프론트엔드 핵심 요청 교정 가드]: 맞은 문제는 철저히 배제하고, 틀린 문항에 원본 기출 번호(q_num) 장착
        if not is_correct:
            is_unsolved = not attempt.selected_option or len(attempt.selected_option) == 0
            status_str = "unsolved" if is_unsolved else "wrong"
            
            # DB questions에 등록된 고유 기출 번호가 있다면 우선 소싱, 없다면 진행 인덱스(idx) 배치
            q_num = getattr(question, "number", idx)
            wrong_items_queue.append((attempt.question_id, q_num, attempt.selected_option, is_correct, status_str))

        # 루프 내부에서도 커밋 전 데이터를 미리 스냅샷 백업
        q_id = question.id
        q_answer = question.answer
        q_explanation = question.explanation

        # 개별 문항 풀이 기록 적재
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

    # [독립형 오답노트 세션 트랜잭션 일괄 처리 엔진]
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

            # 4. 소싱된 오답/미풀이 하위 문항 리스트 벌크 적재 진행 (question_number 포함)
            for q_id, q_num, sel_opt, is_corr, stat in wrong_items_queue:
                # 💡 [SQL 수정]: question_number 컬럼 추가 바인딩 영구 적재
                item_ins = text("""
                    INSERT INTO wrong_notebook_items (notebook_id, question_id, question_number, selected_option, is_correct, status, submitted_at)
                    VALUES (:notebook_id, :question_id, :question_number, :selected_option, :is_correct, :status, :submitted_at)
                """)
                await db.execute(item_ins, {
                    "notebook_id": notebook_id, 
                    "question_id": q_id, 
                    "question_number": q_num,  # 🆕 원본 배치 번호 저장
                    "selected_option": json.dumps(sel_opt),
                    "is_correct": is_corr, 
                    "status": stat, 
                    "submitted_at": shared_submitted_at
                })
            
            # 모든 히스토리 + 오답노트 적재가 완벽히 성공했을 때 최종 단 1회 커밋하여 데이터 무결성 보장
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
    user_res = await db.execute(text("SELECT id FROM users WHERE email = :email"), {"email": current_user})
    user_id = user_res.scalar()
    if not user_id:
        raise HTTPException(status_code=404, detail="구글 인증 정보와 매칭되는 시스템 유저를 찾을 수 없습니다.")

    score_summaries = await crud_history.get_user_scores_summary(db, user_id=user_id)
    return score_summaries