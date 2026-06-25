from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.db.session import get_db

router = APIRouter()

@router.get("/questions/{question_id}/similar")
async def get_similar_questions(
    question_id: int,
    db: AsyncSession = Depends(get_db)
):

    sql = text("""
    SELECT
        q2.id,
        q2.question,
        q2.subject,
        q2.exam_type,
        1 - (q1.embedding <=> q2.embedding) AS similarity
    FROM questions q1
    JOIN questions q2
        ON q1.id != q2.id
    WHERE q1.id = :question_id
    ORDER BY q1.embedding <=> q2.embedding
    LIMIT 5
    """)

    result = await db.execute(
        sql,
        {"question_id": question_id}
    )

    rows = result.fetchall()

    return [
        {
            "id": row.id,
            "question": row.question,
            "subject": row.subject,
            "exam_type": row.exam_type,
            "similarity": float(row.similarity)
        }
        for row in rows
    ]