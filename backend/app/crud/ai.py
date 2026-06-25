# app/crud/ai.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, not_
from typing import List
from app.models.question import Question
from app.models.history import ProblemSolvingHistory 

async def get_fresh_candidates_by_chapter(db: AsyncSession, chapter: str, user_id: int, limit: int) -> List[Question]:
    """유저가 해당 챕터에서 정답(is_correct=True)을 맞춘 적이 없는 신규 문제 목록을 가져옵니다."""
    solved_subquery = select(ProblemSolvingHistory.question_id).filter(
        ProblemSolvingHistory.user_id == user_id,
        ProblemSolvingHistory.is_correct == True
    ).subquery()

    stmt = select(Question).filter(
        Question.chapter == chapter,
        not_(Question.id.in_(solved_subquery))
    ).limit(limit)
    
    result = await db.execute(stmt)
    return list(result.scalars().all())

async def get_fresh_candidates_global(db: AsyncSession, user_id: int, points: int, exclude_ids: List[int], limit: int) -> List[Question]:
    """1단계 Fallback용: 유저가 안 풀었으면서 배점(난이도)이 유사한 문제를 글로벌 탐색합니다."""
    solved_subquery = select(ProblemSolvingHistory.question_id).filter(
        ProblemSolvingHistory.user_id == user_id,
        ProblemSolvingHistory.is_correct == True
    ).subquery()

    stmt = select(Question).filter(
        not_(Question.id.in_(exclude_ids)),
        not_(Question.id.in_(solved_subquery)),
        Question.points.between(max(1, points - 1), min(5, points + 1)) 
    ).limit(limit)

    result = await db.execute(stmt)
    return list(result.scalars().all())

# 💡 [교정 완료]: db: Session 오타를 비동기 호환을 위해 db: AsyncSession 명세로 전면 교정합니다.
async def get_past_wrong_questions_by_chapter(db: AsyncSession, chapter: str, user_id: int, limit: int) -> List[Question]:
    """2단계 Fallback용: 풀 수 있는 신규 문제가 없을 때, 해당 챕터에서 과거에 틀렸던 문제를 복습용으로 가져옵니다."""
    stmt = select(Question).join(ProblemSolvingHistory, Question.id == ProblemSolvingHistory.question_id).filter(
        Question.chapter == chapter,
        ProblemSolvingHistory.user_id == user_id,
        ProblemSolvingHistory.is_correct == False
    ).distinct().limit(limit)

    result = await db.execute(stmt)
    return list(result.scalars().all())