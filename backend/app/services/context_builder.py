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
    🚀 [고도화]: 기출문항의 모든 메타데이터를 통합하여 GPT 대화용 주입 컨텍스트를 조립합니다.
    """
    stmt = select(Question).filter(Question.id == question_id)
    result = await db.execute(stmt)
    q = result.scalars().first()
    
    if not q:
        return ""
        
    # JSONB 데이터 구조인 사지/오지선다 보기를 줄바꿈 텍스트 포맷으로 예쁘게 파싱
    options_parsed = ""
    if isinstance(q.options, dict):
        options_parsed = "\n".join([f"({k}) {v}" for k, v in q.options.items()])
    else:
        options_parsed = str(q.options)

    # 시스템 정답 포맷 가공 (배열 파싱 대응)
    answer_parsed = str(q.answer)

    # 🖼️ 프론트엔드 퍼블릭 경로 스냅샷 확보 (추후 비전 연동용 예비 데이터)
    image_info = f"없음 (순수 텍스트 문항)"
    if q.image_url:
        image_info = f"존재함 (경로: {q.image_url})"

    return f"""[기출문제 원본 컨텍스트 데이터 스냅샷]
- 시험 대분류: {q.exam_type}
- 과목/단원: {q.subject} > {q.chapter or '미분류 상세 단원'}
- 출제 문항 정보: {q.year or '미상'}년도 시행 / {q.number}번
- 문제 발문(질문 본문): {q.question}
- 지문 추가 텍스트(body): {q.body or '없음'}
- 보기 구성 목록:
{options_parsed}
- 시스템 공식 정답: {answer_parsed}
- 출제자 친절 해설: {q.explanation or '등록된 요약 해설이 없습니다.'}
- 문항 이미지 에셋 링크 상태: {image_info}"""