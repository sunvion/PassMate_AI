# backend/app/crud/statistics.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete, func, text
from app.models.history import ProblemSolvingHistory
from app.models.question import Question
from app.schemas.statistics import (
    DashboardSummaryResponse, 
    ExamSessionDetailResponse, 
    SolvedQuestionDetail
)
from typing import List, Optional, Any, Dict

class CRUDStatistics:
    async def get_user_dashboard_summary(self, db: AsyncSession, user_id: int) -> DashboardSummaryResponse:
        """
        [개정] 홈 화면 '학습 요약' 3단 카드 대시보드 실시간 집계
        과거 전체 누적 데이터가 아닌, 과목(직렬)별 '가장 최근에 제출된 세션 회차'만 필터링하여 통계를 도출합니다.
        """
        # 유저의 전체 풀이 기록을 시간순(오름차순)으로 조회
        query = (
            select(ProblemSolvingHistory)
            .where(ProblemSolvingHistory.user_id == user_id)
            .order_by(ProblemSolvingHistory.submitted_at.asc())
        )
        result = await db.execute(query)
        rows = result.scalars().all()

        # 풀이 이력이 아예 없는 경우 방어 처리
        if not rows:
            return DashboardSummaryResponse(
                total_solved=0,
                average_correct_rate=0.0,
                recent_attempt_at=None
            )

        # 1. 과목별로 이력 그루핑 (exam_type, year, subject_snapshot)
        exam_groups = {}
        for r in rows:
            key = (r.exam_type, r.year, r.subject_snapshot)
            if key not in exam_groups:
                exam_groups[key] = []
            exam_groups[key].append(r)

        latest_session_rows = []

        # 2. 각 과목 그룹 내에서 '가장 최근에 제출한 청크 세션(20 또는 40문항)' 분리
        for key, items in exam_groups.items():
            exam_type, _, _ = key
            chunk_size = 40 if exam_type == "DRIVERS_LICENSE_1" else 20
            
            total_len = len(items)
            remainder = total_len % chunk_size
            
            # 딱 나누어 떨어지면 마지막 chunk_size(20/40)만큼이 최신 제출 회차
            if remainder == 0:
                last_chunk = items[-chunk_size:]
            else:
                # 진행 중이거나 규격이 어긋난 경우 남은 잔여 데이터가 최신 제출 회차
                last_chunk = items[-remainder:]
                
            latest_session_rows.extend(last_chunk)

        # 3. 필터링된 과목별 최신 회차 데이터만으로 최종 대시보드 요약 지표 연산
        total_solved = len(latest_session_rows)
        correct_count = sum(1 for r in latest_session_rows if r.is_correct)
        average_correct_rate = round((correct_count / total_solved) * 100, 1) if total_solved > 0 else 0.0
        
        # 최근 응시 기록은 전체 풀이 이력 중 가장 마지막 타임스탬프 반환
        recent_attempt_at = max(r.submitted_at for r in rows)

        return DashboardSummaryResponse(
            total_solved=total_solved,
            average_correct_rate=average_correct_rate,
            recent_attempt_at=recent_attempt_at
        )

    async def get_user_exam_history_details(self, db: AsyncSession, user_id: int) -> List[ExamSessionDetailResponse]:
        """전체 풀이 이력 기반 동적 규격 슬라이싱 성적표 세션 빌드 (기존 성적표 아코디언 로직 유지)"""
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


    # 🆕 ================= 독립형 오답노트 관리 비즈니스 로직 연동 (CRUD) =================

    async def get_wrong_notebooks_list(self, db: AsyncSession, user_id: int) -> List[Dict[str, Any]]:
        """
        1. 오답노트 목록 조회 (GET /api/v1/wrong-notebooks)
        유저가 소유한 오답노트 메인 목록을 카운트 통계 데이터와 결합하여 고속 집계 조회합니다.
        """
        query = text("""
            SELECT 
                wn.id, wn.title, wn.exam_type, wn.year, wn.subject,
                COALESCE(SUM(CASE WHEN wni.status = 'wrong' THEN 1 ELSE 0 END), 0) as wrong_count,
                COALESCE(SUM(CASE WHEN wni.status = 'unsolved' THEN 1 ELSE 0 END), 0) as unsolved_count,
                COUNT(wni.id) as total_count,
                wn.created_at
            FROM wrong_notebooks wn
            LEFT JOIN wrong_notebook_items wni ON wn.id = wni.notebook_id
            WHERE wn.user_id = :user_id
            GROUP BY wn.id, wn.title, wn.exam_type, wn.year, wn.subject, wn.created_at
            ORDER BY wn.created_at DESC
        """)
        result = await db.execute(query, {"user_id": user_id})
        rows = result.all()
        return [
            {
                "id": r.id,
                "title": r.title,
                "exam_type": r.exam_type,
                "year": r.year,
                "subject": r.subject,
                "wrong_count": int(r.wrong_count),
                "unsolved_count": int(r.unsolved_count),
                "total_count": int(r.total_count),
                "created_at": r.created_at.strftime("%Y-%m-%d") if r.created_at else ""
            }
            for r in rows
        ]

    async def get_wrong_notebook_detail(self, db: AsyncSession, user_id: int, notebook_id: int) -> Optional[Dict[str, Any]]:
        """
        2. 특정 오답노트 상세 조회 (GET /api/v1/wrong-notebooks/{wrong_notebook_id})
        오답노트 마스터 유효성 검증 후, 귀속된 모든 문항(틀린 문제 + 안 푼 문제)의 원본과 오답 마킹 스냅샷을 반환합니다.
        """
        # 소유권 검증용 마스터 테이블 조회
        nb_query = text("SELECT id, title, exam_type, year, subject FROM wrong_notebooks WHERE id = :id AND user_id = :user_id")
        nb_res = await db.execute(nb_query, {"id": notebook_id, "user_id": user_id})
        nb_row = nb_res.first()
        if not nb_row:
            return None

        # 연결된 문제 원본 및 오답 스냅샷 데이터 JOIN 조회
        items_query = text("""
            SELECT wni.question_id, q.question, q.options, wni.selected_option, q.answer as correct_answer,
                   wni.is_correct, wni.status, q.explanation, wni.submitted_at
            FROM wrong_notebook_items wni
            JOIN questions q ON wni.question_id = q.id
            WHERE wni.notebook_id = :notebook_id 
            ORDER BY wni.id ASC
        """)
        items_res = await db.execute(items_query, {"notebook_id": notebook_id})
        items_rows = items_res.all()

        import json
        items_list = []
        for r in items_rows:
            # 데이터베이스 적재 데이터 타입 호환성을 고려한 JSON 파싱 방어 코드
            opts = r.options if isinstance(r.options, dict) else json.loads(r.options) if r.options else {}
            sel_opt = r.selected_option if isinstance(r.selected_option, list) else json.loads(r.selected_option) if r.selected_option else []
            corr_ans = r.correct_answer if isinstance(r.correct_answer, list) else json.loads(r.correct_answer) if r.correct_answer else []
            
            items_list.append({
                "question_id": r.question_id,
                "question": r.question,
                "options": opts,
                "selected_option": sel_opt,
                "correct_answer": corr_ans,
                "is_correct": r.is_correct,
                "status": r.status,
                "explanation": r.explanation,
                "submitted_at": r.submitted_at
            })

        return {
            "id": nb_row.id,
            "title": nb_row.title,
            "exam_type": nb_row.exam_type,
            "year": nb_row.year,
            "subject": nb_row.subject,
            "items": items_list
        }

    async def update_wrong_notebook_title(self, db: AsyncSession, user_id: int, notebook_id: int, title: str) -> bool:
        """
        3. 오답노트 이름 수정 (PATCH /api/v1/wrong-notebooks/{wrong_notebook_id})
        사용자가 지정한 제목 식별자로 오답노트의 고유 명칭을 안전하게 업데이트합니다.
        """
        query = text("UPDATE wrong_notebooks SET title = :title WHERE id = :id AND user_id = :user_id")
        res = await db.execute(query, {"title": title, "id": notebook_id, "user_id": user_id})
        await db.commit()
        return res.rowcount > 0

    async def delete_wrong_notebook(self, db: AsyncSession, user_id: int, notebook_id: int) -> bool:
        """
        4. 오답노트 개별 삭제 (DELETE /api/v1/wrong-notebooks/{wrong_notebook_id})
        전체 풀이 이력(History)의 손상 없이, 사용자가 원하는 오답노트 카드 세션만 깔끔하게 제거합니다.
        (ON DELETE CASCADE로 인해 내부 연결 아이템들은 DB 레이어에서 일괄 동시 제거됩니다.)
        """
        query = text("DELETE FROM wrong_notebooks WHERE id = :id AND user_id = :user_id")
        res = await db.execute(query, {"id": notebook_id, "user_id": user_id})
        await db.commit()
        return res.rowcount > 0

crud_statistics = CRUDStatistics()