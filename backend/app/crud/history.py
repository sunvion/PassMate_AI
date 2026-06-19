from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, case, Integer
from app.models.history import ProblemSolvingHistory
from app.models.question import Question
from app.schemas.history import SingleAttemptCreate
from typing import List, Dict, Any

class CRUDHistory:
    async def create_history(
        self, db: AsyncSession, user_id: int, attempt: SingleAttemptCreate, question: Question, is_correct: bool
    ) -> ProblemSolvingHistory:
        """
        설명: 유저의 풀이 로그를 적재하고, 마스터 데이터 변동에 대응하기 위해 당시 문항 메타데이터를 스냅샷 처리
        """
        db_history = ProblemSolvingHistory(
            user_id=user_id,
            question_id=attempt.question_id,
            selected_option=attempt.selected_option,
            is_correct=is_correct,
            exam_type=question.exam_type,
            year=question.year,
            subject_snapshot=question.subject,
            category_snapshot=question.category,
            time=attempt.time
        )
        db.add(db_history)
        await db.commit()
        await db.refresh(db_history)
        return db_history

    async def get_user_scores_summary(self, db: AsyncSession, user_id: int) -> List[Dict[str, Any]]:
        """
        설명: 사용자가 제출했던 모의고사 세션들을 제출 시간(submitted_at) 기준으로 그룹화하여 성적표 요약본 리스트 추출
        """
        query = (
            select(
                ProblemSolvingHistory.exam_type,
                ProblemSolvingHistory.year,
                ProblemSolvingHistory.subject_snapshot.label("subject"),
                func.count(ProblemSolvingHistory.id).label("total_questions"),
                # Boolean 필드를 안전하게 카운트하기 위해 case 처리
                func.sum(case((ProblemSolvingHistory.is_correct == True, 1), else_=0)).label("correct_count"),
                ProblemSolvingHistory.submitted_at
            )
            .where(ProblemSolvingHistory.user_id == user_id)
            .group_by(
                ProblemSolvingHistory.exam_type,
                ProblemSolvingHistory.year,
                ProblemSolvingHistory.subject_snapshot,
                ProblemSolvingHistory.submitted_at
            )
            .order_by(ProblemSolvingHistory.submitted_at.desc())
        )
        result = await db.execute(query)
        rows = result.all()
        
        summaries = []
        for r in rows:
            correct_cnt = r.correct_count or 0
            # 공무원 20문항의 경우 개당 5점으로 스코어 환산 로직 바인딩
            calculated_score = correct_cnt * 5 if r.total_questions == 20 else (correct_cnt * 2)
            
            summaries.append({
                "exam_type": r.exam_type,
                "year": r.year,
                "subject": r.subject,
                "total_questions": r.total_questions,
                "correct_count": correct_cnt,
                "score": calculated_score,
                "submitted_at": r.submitted_at
            })
        return summaries

    async def get_wrong_notebook(self, db: AsyncSession, user_id: int, exam_type: str = None) -> List[Question]:
        """
        설명: [제안 API용] 오답노트 구성을 위해 사용자가 단 한 번이라도 틀린 이력이 있는 중복 없는 원본 문제 리스트 반환
        """
        subquery = (
            select(ProblemSolvingHistory.question_id)
            .where(ProblemSolvingHistory.user_id == user_id, ProblemSolvingHistory.is_correct == False)
            .distinct()
            .subquery()
        )
        
        query = select(Question).join(subquery, Question.id == subquery.c.question_id)
        if exam_type:
            query = query.where(Question.exam_type == exam_type)
            
        result = await db.execute(query)
        return result.scalars().all()

crud_history = CRUDHistory()