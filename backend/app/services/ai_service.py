# app/services/ai_service.py
import random
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.crud import ai as ai_crud
from app.models.question import Question
from app.schemas.ai import AIRecommendationListResponse

async def get_recommended_questions(db: AsyncSession, user_id: int, question_id: int, limit: int = 3) -> dict: # 💡 async 함수 선언
    # 💡 비동기 방식 기준 문제 조회 처리
    result = await db.execute(select(Question).filter(Question.id == question_id))
    base_question = result.scalars().first()
    
    if not base_question:
        raise ValueError("기준 문제를 찾을 수 없습니다.")
    
    chapter = base_question.chapter if base_question.chapter else "미분류 단원"
    recommendation_type = "MATCHED"

    # 💡 비동기 CRUD 호출 (await)
    candidates = await ai_crud.get_fresh_candidates_by_chapter(db, chapter, user_id, limit=limit * 3)

    # 🔥 1단계 Fallback: 자원 부족 시 글로벌 탐색으로 확장
    if len(candidates) < limit:
        recommendation_type = "GLOBAL_FALLBACK"
        exclude_ids = [base_question.id] + [c.id for c in candidates]
        needed_count = (limit * 3) - len(candidates)
        
        base_points = base_question.points if base_question.points is not None else 2
        
        # 💡 비동기 글로벌 후보군 조회 (await)
        global_candidates = await ai_crud.get_fresh_candidates_global(
            db, user_id, base_points, exclude_ids, limit=needed_count
        )
        candidates.extend(global_candidates)

    # 🔥 2단계 Fallback: 신규 문제가 아예 없다면 복습 모드
    if len(candidates) == 0:
        recommendation_type = "REVIEW_MODE"
        # 💡 비동기 복습 문제 조회 (await)
        candidates = await ai_crud.get_past_wrong_questions_by_chapter(db, chapter, user_id, limit=limit)

    # 🔥 3단계 Fallback: 완전 고갈 시 가상 문제 동적 생성
    if len(candidates) == 0:
        return _generate_llm_mock_question(base_question, chapter)

    # 🎯 3문항 필터링 및 셔플
    random.shuffle(candidates)
    final_items = candidates[:limit]

    return {
        "recommendation_type": recommendation_type,
        "chapter": chapter,
        "items": final_items
    }

def _generate_llm_mock_question(base_question: Question, chapter: str) -> dict:
    base_points = base_question.points if base_question.points is not None else 2
    return {
        "recommendation_type": "GENERATED",
        "chapter": chapter,
        "items": [
            {
                "id": 9999,
                "question": f"[AI 생성 유사 문항] 다음 중 {chapter}의 성질로 올바른 객관식 문항을 고르시오.",
                "image_url": None,
                "options": {"1": "AI 임시 보기 1", "2": "AI 임시 보기 2", "3": "AI 임시 보기 3", "4": "AI 임시 보기 4"},
                "answer": [1],
                "explanation": "이 문제는 DB 자원 고갈 시 AI가 실시간으로 원리를 복제해 낸 신규 문항입니다.",
                "points": base_points,
                "chapter": chapter
            }
        ]
    }