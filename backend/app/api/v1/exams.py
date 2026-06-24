# backend/app/api/v1/exams.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from typing import List, Optional, Any

from app.db.session import get_db
from app.crud.question import crud_question
from app.models.question import Question
from app.schemas.question import QuestionResponse

router = APIRouter()

@router.get("", summary="등록된 전체 기출지 메타 리스트 유니크 조회")
async def read_exam_meta_list(db: AsyncSession = Depends(get_db)):
    """
    프론트엔드 메인 설정 대시보드 진입 시 과목/연도 셀렉트 박스를 빌드하기 위해
    현재 시스템에 존재하는 고유한 시험 메타 데이터 조합 리스트를 반환합니다.
    """
    # 중복 없는 과목 조합을 뽑아내기 위한 DISTINCT 대량 쿼리 실행
    query = select(Question.exam_type, Question.year, Question.subject).distinct()
    result = await db.execute(query)
    
    # 프론트엔드가 요구하는 JSON 리스트 객체로 포맷 가공 변환
    meta_list = []
    for row in result.all():
        meta_list.append({
            "exam_type": row.exam_type,
            "year": row.year,
            "subject": row.subject
        })
    return meta_list


@router.get("/questions", summary="조건별 기출문제 문항 전체 조회 (정방향 기본 모드)")
async def read_exam_questions(
    exam_type: str,
    subject: str,
    year: Optional[int] = None,  # 422 에러 방지 및 유연성을 위해 Optional 가드 처리
    db: AsyncSession = Depends(get_db)
):
    """
    컴퓨터일반 등 지정된 연도의 기출문제 시험 세트 전체를 1번부터 차례대로 정렬하여 반환합니다.
    """
    questions = await crud_question.get_questions_by_criteria(
        db=db, exam_type=exam_type, subject=subject, year=year
    )
    if not questions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="요청하신 조건과 매칭되는 기출문제가 시스템에 존재하지 않습니다."
        )
    return questions


@router.get("/questions/random", summary="🆕 문제은행 기반 랜덤 문항 추출 (운전면허 전용)")
async def read_random_exam_questions(
    exam_type: str,
    subject: str,
    limit: int = 40,  # 운전면허 학과 규격인 40개를 기본값으로 설정
    db: AsyncSession = Depends(get_db)
):
    """
    전체 문제 풀에서 무작위로 셔플된 지정된 개수(40개)만큼의 문항 시험지를 실시간으로 동적 생성하여 내려줍니다.
    """
    questions = await crud_question.get_random_questions(
        db=db, exam_type=exam_type, subject=subject, limit=limit
    )
    if not questions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 시험 분류에 저장된 데이터 풀이 없어 랜덤 추출에 실패했습니다."
        )
    return questions

@router.get("/questions/wrong", response_model=List[QuestionResponse], summary="특정 챕터의 오답 문항 전체 리스트 조회")
async def read_wrong_questions_by_chapter(
    chapter: str, # 🌟 쿼리 파라미터로 수신 (?chapter=컴퓨터구조)
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user_res = await db.execute(text("SELECT id FROM users WHERE email = :email"), {"email": current_user})
    user_id = user_res.scalar()
    if not user_id:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")
        
    questions = await crud_question.get_wrong_questions_by_chapter(db=db, user_id=user_id, chapter=chapter)
    return questions
