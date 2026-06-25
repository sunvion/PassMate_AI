import requests

from app.services.rag.law_rag import search_law
from app.services.llm_service import generate_answer
from app.services.context_builder import build_context


def get_question(question_id: int):
    return {
        "id": question_id,
        "question": "신호 위반 시 처벌 기준은?"
    }


def get_similar_questions(question_id: int):

    url = f"http://localhost:8000/api/v1/recommendations/questions/{question_id}/similar"

    try:
        res = requests.get(url)
        return res.json() if res.status_code == 200 else []
    except:
        return []


def get_wrong_note(question_id: int):

    question = get_question(question_id)
    similar = get_similar_questions(question_id)
    law = search_law(question["question"])

    prompt = build_context(
        question["question"],
        similar,
        law
    )

    answer = generate_answer(prompt)

    return {
        "question": question,
        "similar_questions": similar,
        "law_chunks": law,
        "answer": answer
    }