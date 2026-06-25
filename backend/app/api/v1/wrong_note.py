from fastapi import APIRouter
from app.services.wrong_note_service import get_wrong_note

router = APIRouter()

@router.get("/wrong-note/{question_id}")
def wrong_note(question_id: int):
    return get_wrong_note(question_id)