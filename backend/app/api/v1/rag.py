from fastapi import APIRouter
from app.services.rag.law_rag import search_law

router = APIRouter()

@router.get("/ping")
def ping():
    return {"status": "ok"}

@router.get("")
def get_law(query: str):
    return search_law(query)