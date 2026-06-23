# backend/app/crud/statistics.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete, func
from app.models.history import ProblemSolvingHistory
from app.models.question import Question
from app.schemas.statistics import DashboardSummaryResponse, ExamSessionDetailResponse, SolvedQuestionDetail
from typing import List, Optional, Any, Dict

class CRUDStatistics:
    async def get_user_dashboard_summary(self, db: AsyncSession, user_id: int) -> DashboardSummaryResponse:
        """홈 화면 '학습 요약' 3단 카드 대시보드 실시간 집계"""
        from sqlalchemy import case
        stats_query = select(
            func.count(ProblemSolvingHistory.id).label("total_solved"),
            func.avg(case((ProblemSolvingHistory.is_correct == True, 100.0), else_=0.0)).label("avg_rate")
        ).where(ProblemSolvingHistory.user_id == user_id)
        stats_result = await db.execute(stats_query)
        stats_row = stats_result.first()

        total_solved = stats_row.total_solved if stats_row and stats_row.total_solved else 0
        average_correct_rate = round(stats_row.avg_rate, 1) if stats_row and stats_row.avg_rate is not None else 0.0

        recent_query = select(ProblemSolvingHistory.submitted_at).where(ProblemSolvingHistory.user_id == user_id).order_by(ProblemSolvingHistory.submitted_at.desc()).limit(1)
        recent_result = await db.execute(recent_query)
        recent_row = recent_result.scalar_one_or_none()

        return DashboardSummaryResponse(
            total_solved=total_solved,
            average_correct_rate=average_correct_rate,
            recent_attempt_at=recent_row
        )

    async def get_user_exam_history_details(self, db: AsyncSession, user_id: int) -> List[ExamSessionDetailResponse]:
        """전체 풀이 이력 기반 동적 규격 슬라이싱 성적표 세션 빌드"""
        query = (
            select(
                ProblemSolvingHistory,
                Question.question.label("question_text"),
                Question.answer.label("correct_answer")
            )
            .join(Question, ProblemSolvingHistory.question_id == Question.id)
            .where(ProblemSolvingHistory.user_id == user_id)
            .order_by(ProblemSolvingHistory.submitted_at.asc())
        )
        
        result = await db.execute(query)
        rows = result.all()

        exam_groups = {}
        for p_history, q_text, q_ans in rows:
            group_key = (p_history.exam_type, p_history.year, p_history.subject_snapshot)
            if group_key not in exam_groups:
                exam_groups[group_key] = []
            exam_groups[group_key].append((p_history, q_text, q_ans))

        final_response = []

        for group_key, items in exam_groups.items():
            exam_type, year, subject = group_key
            chunk_size = 40 if exam_type == "DRIVERS_LICENSE_1" else 20
            
            for i in range(0, len(items), chunk_size):
                chunk = items[i:i + chunk_size]
                total_questions = len(chunk)
                correct_count = sum(1 for p_hist, _, _ in chunk if p_hist.is_correct)
                
                if exam_type == "DRIVERS_LICENSE_1":
                    score = int((correct_count / total_questions) * 100) if total_questions > 0 else 0
                else:
                    score = correct_count * 5 if total_questions == 20 else int((correct_count / total_questions) * 100) if total_questions > 0 else 0

                latest_submitted_at = chunk[-1][0].submitted_at

                solved_questions = [
                    SolvedQuestionDetail(
                        history_id=p_hist.id,
                        question_id=p_hist.question_id,
                        question_text=q_txt,
                        selected_option=p_hist.selected_option,
                        is_correct=p_hist.is_correct,
                        correct_answer=q_an
                    )
                    for p_hist, q_txt, q_an in chunk
                ]

                final_response.append(
                    ExamSessionDetailResponse(
                        exam_type=exam_type,
                        year=year,
                        subject=subject,
                        total_questions=total_questions,
                        correct_count=correct_count,
                        score=score,
                        submitted_at=latest_submitted_at,
                        solved_questions=solved_questions
                    )
                )

        final_response.sort(key=lambda x: x.submitted_at, reverse=True)
        return final_response

    async def clear_user_history(self, db: AsyncSession, user_id: int) -> bool:
        """유저의 모든 문제 풀이 히스토리 일괄 삭제"""
        query = delete(ProblemSolvingHistory).where(ProblemSolvingHistory.user_id == user_id)
        await db.execute(query)
        await db.commit()
        return True

    # 🆕 오답노트 기능 1: 유저가 틀린 문제들을 직렬/과목별로 그룹화하여 카운트 리스트 추출
    async def get_user_wrong_summary(self, db: AsyncSession, user_id: int) -> List[Dict[str, Any]]:
        query = (
            select(
                ProblemSolvingHistory.exam_type,
                ProblemSolvingHistory.year,
                ProblemSolvingHistory.subject_snapshot.label("subject"),
                func.count(ProblemSolvingHistory.id).label("wrong_count")
            )
            .where(
                ProblemSolvingHistory.user_id == user_id, 
                ProblemSolvingHistory.is_correct == False  # 💡 오답 필터링 원칙 적용
            )
            .group_by(
                ProblemSolvingHistory.exam_type, 
                ProblemSolvingHistory.year, 
                ProblemSolvingHistory.subject_snapshot
            )
            .order_by(func.max(ProblemSolvingHistory.submitted_at).desc())
        )
        result = await db.execute(query)
        rows = result.all()
        return [
            {
                "exam_type": r.exam_type,
                "year": r.year,
                "subject": r.subject,
                "wrong_count": r.wrong_count
            }
            for r in rows
        ]

    # 🆕 오답노트 기능 2: 선택한 특정 조건에 부합하는 오답 문항 원본 및 내 선택지 풀 데이터 JOIN 추출
    async def get_user_wrong_details(
        self, db: AsyncSession, user_id: int, exam_type: str, subject: str, year: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        query = (
            select(
                ProblemSolvingHistory.question_id,
                Question.question,
                Question.options,
                ProblemSolvingHistory.selected_option,
                Question.answer.label("correct_answer"),
                Question.explanation,
                ProblemSolvingHistory.is_correct,
                ProblemSolvingHistory.submitted_at
            )
            .join(Question, ProblemSolvingHistory.question_id == Question.id)
            .where(
                ProblemSolvingHistory.user_id == user_id,
                ProblemSolvingHistory.is_correct == False,  # 💡 오답 필터링
                ProblemSolvingHistory.exam_type == exam_type,
                ProblemSolvingHistory.subject_snapshot == subject
            )
        )
        
        # 기출 연도 조건이 전달된 경우 가드 스케일 확장
        if year is not None:
            query = query.where(ProblemSolvingHistory.year == year)
            
        query = query.order_by(ProblemSolvingHistory.submitted_at.desc())
        result = await db.execute(query)
        rows = result.all()
        
        return [
            {
                "question_id": r.question_id,
                "question": r.question,
                "options": r.options,
                "selected_option": r.selected_option,
                "correct_answer": r.correct_answer,
                "explanation": r.explanation,
                "is_correct": r.is_correct,
                "submitted_at": r.submitted_at
            }
            for r in rows
        ]

crud_statistics = CRUDStatistics()