# app/services/context_builder.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.question import Question

def build_context(question, similar_questions, law_chunks):
    """기존 법률 RAG용 컨텍스트 빌더 (유지)"""
    similar_text = "\n".join(
        [f"- {q['question']}" for q in similar_questions]
    )
    law_text = "\n".join(
        [f"- {l['content']}" for l in law_chunks]
    )

    return f"""
[문제]
{question}

[유사 문제]
{similar_text}

[관련 법령]
{law_text}

[요청]
이 문제를 왜 틀렸는지 설명하고,
정답 근거를 법령 기반으로 설명해줘.
"""

async def build_question_context(db: AsyncSession, question_id: int) -> str:
    """
    🚀 [신설] AI 챗봇 전용 컨텍스트 빌더
    특정 문제 ID를 기반으로 GPT가 인지할 수 있는 완벽한 문제 요약 문맥을 생성합니다.
    """
    stmt = select(Question).filter(Question.id == question_id)
    result = await db.execute(stmt)
    question_obj = result.scalars().first()
    
    if not question_obj:
        return ""
        
    # 오지/사지선다 보기 딕셔너리를 가독성 좋은 텍스트로 파싱
    options_text = "\n".join([f"({k}) {v}" for k, v in question_obj.options.items()])
    
    return f"""- 과목/단원: {question_obj.subject} > {question_obj.chapter or '미분류 단원'}
- 문제 질문: {question_obj.question}
- 보기 구성:
{options_text}
- 시스템 정답 번호: {question_obj.answer}
- 출제자 해설: {question_obj.explanation or '등록된 공식 해설이 없습니다.'}"""