# backend/app/crud/question.py
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.question import Question  # 프로젝트의 실제 테이블 ORM 모델 경로
from app.models.history import ProblemSolvingHistory  # 🌟 [필수 추가]: 풀이 이력 모델 임포트
from typing import List, Optional

class CRUDQuestion:
    async def get_by_id(self, db: AsyncSession, question_id: int) -> Optional[Question]:
        """
        문제 고유 고유 ID(PK)를 기반으로 단일 문항 상세 정보를 조회합니다.
        """
        query = select(Question).where(Question.id == question_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_questions_by_criteria(
        self, db: AsyncSession, exam_type: str, subject: str, year: Optional[int] = None
    ) -> List[Question]:
        """
        기존 일반 기출 조회용: 시험 종류, 과목, 출제 연도를 기반으로 정렬된 문항 리스트를 반환합니다.
        """
        query = select(Question).where(
            Question.exam_type == exam_type,
            Question.subject == subject
        )
        
        # 연도 파라미터가 명시적으로 들어온 경우에만 조건절 조건 추가
        if year is not None:
            query = query.where(Question.year == year)
            
        # 문항 번호(1번~20번) 순서대로 오름차순 정렬
        query = query.order_by(Question.number.asc())
        
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_random_questions(
        self, db: AsyncSession, exam_type: str, subject: str, limit: int = 40
    ) -> List[Question]:
        """
        🆕 [추가]: 운전면허 등 문제은행 규격 대응 랜덤 문항 추출 로직
        PostgreSQL의 ORDER BY RANDOM()을 사용하여 무작위로 뒤섞은 뒤 지정된 개수(기본 40개)만큼 끊어옵니다.
        """
        query = (
            select(Question)
            .where(
                Question.exam_type == exam_type,
                Question.subject == subject
            )
            .order_by(func.random())  # 🌟 데이터베이스 레벨에서 무작위 셔플링 수행
            .limit(limit)             # 🌟 지정된 개수(40개)만큼 슬라이싱
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    # 🌟 CRUDQuestion 클래스 스코프 내부로 안전하게 안착
    async def get_wrong_questions_by_chapter(self, db: AsyncSession, user_id: int, chapter: str) -> List[Question]:
        """
        특정 챕터 내부에서 사용자가 단 한 번이라도 틀린 이력이 있는 중복 없는 원본 문제 리스트 반환
        """
        subquery = (
            select(ProblemSolvingHistory.question_id)
            .where(ProblemSolvingHistory.user_id == user_id, ProblemSolvingHistory.is_correct == False)
            .distinct()
            .subquery()
        )
        query = (
            select(Question)
            .join(subquery, Question.id == subquery.c.question_id)
            .where(Question.chapter == chapter)
            .order_by(Question.year.desc(), Question.number.asc())  # 최신개년 문항순 정렬
        )
        result = await db.execute(query)
        return list(result.scalars().all())

crud_question = CRUDQuestion()