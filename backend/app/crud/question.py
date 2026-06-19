from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.question import Question
from typing import List, Optional

class CRUDQuestion:
    async def get_distinct_exams(self, db: AsyncSession) -> List[Question]:
        """
        설명: 고유한 시험지 세트(exam_type, subject, year 조합)를 전체 대시보드용으로 반환
        """
        query = select(Question.exam_type, Question.year, Question.subject).distinct()
        result = await db.execute(query)
        return result.all()

    async def get_questions_by_exam(
        self, db: AsyncSession, exam_type: str, year: int, subject: str
    ) -> List[Question]:
        """
        설명: 선택한 시험지의 20문항 전체를 문항 순서대로 정렬하여 반환
        """
        query = (
            select(Question)
            .where(
                Question.exam_type == exam_type,
                Question.year == year,
                Question.subject == subject
            )
            .order_by(Question.number.asc())
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_id(self, db: AsyncSession, question_id: int) -> Optional[Question]:
        """
        설명: 고유 ID를 기반으로 단일 문항의 원본 정보를 상세 조회
        """
        query = select(Question).where(Question.id == question_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

crud_question = CRUDQuestion()