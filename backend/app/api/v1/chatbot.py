# app/api/v1/chatbot.py
import traceback
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.chatbot import (
    ChatRoomCreate, 
    ChatRoomResponse, 
    ChatMessageCreate, 
    ChatMessageResponse
)
from app.services import chatbot_service

router = APIRouter()

# 💡 안전한 비동기 유저 식별용 헬퍼 함수
async def _get_authenticated_user_id(db: AsyncSession, current_user: any) -> int:
    if isinstance(current_user, str):
        if "@" in current_user:
            result = await db.execute(select(User).filter(User.email == current_user))
            db_user = result.scalars().first()
        else:
            try:
                result = await db.execute(select(User).filter(User.id == int(current_user)))
                db_user = result.scalars().first()
            except ValueError:
                db_user = None
        
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="인증 유저를 데이터베이스에서 조회할 수 없습니다."
            )
        return db_user.id
    return current_user.id


# =================================================================
# 🏢 1. 챗봇 대화방(Room) 도메인 API
# =================================================================

@router.post("/rooms", response_model=ChatRoomResponse, status_code=status.HTTP_201_CREATED)
async def create_chat_room(
    room_in: ChatRoomCreate,
    db: AsyncSession = Depends(get_db),
    current_user: any = Depends(get_current_user)
):
    """
    새로운 오답 전용 대화방을 생성합니다.
    (예: 문항 #161 오답 튜팅방)
    """
    try:
        user_id = await _get_authenticated_user_id(db, current_user)
        room = await chatbot_service.create_new_room(db=db, user_id=user_id, room_in=room_in)
        return room
    except Exception as e:
        print(f"🚨 [CHATROOM_CREATE_ERROR] {str(e)}")
        raise HTTPException(status_code=500, detail="대화방 생성 중 내부 서버 오류가 발생했습니다.")


@router.get("/rooms", response_model=List[ChatRoomResponse])
async def get_user_chat_rooms(
    db: AsyncSession = Depends(get_db),
    current_user: any = Depends(get_current_user)
):
    """
    현재 로그인한 유저의 과거 AI 대화방 목록을 전체 조회합니다.
    """
    try:
        user_id = await _get_authenticated_user_id(db, current_user)
        rooms = await chatbot_service.get_user_rooms(db=db, user_id=user_id)
        return rooms
    except Exception as e:
        print(f"🚨 [CHATROOM_LIST_ERROR] {str(e)}")
        raise HTTPException(status_code=500, detail="대화방 목록 로드 중 오류가 발생했습니다.")


# =================================================================
# 💬 2. 챗봇 메시지(Message) 및 GPT 연동 API
# =================================================================

@router.post("/rooms/{room_id}/messages", response_model=ChatMessageResponse)
async def send_chat_message(
    room_id: int,
    message_in: ChatMessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: any = Depends(get_current_user)
):
    """
    대화방에 질문 메시지를 전송하고, OpenAI(GPT)로부터 컨텍스트 기반 답변을 받아 반환합니다.
    Request Body에 'question_id'가 포함되면 해당 기출문제의 정보가 프롬프트에 자동 주입됩니다.
    """
    try:
        user_id = await _get_authenticated_user_id(db, current_user)
        
        # 🎯 서비스 레이어 호출: 유저 질문 저장 -> 프롬프트 조립 -> GPT 호출 -> AI 답변 저장 완료형 패턴
        ai_response = await chatbot_service.process_user_message(
            db=db,
            user_id=user_id,
            room_id=room_id,
            message_in=message_in
        )
        return ai_response

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        print("\n" + "="*60)
        print("🚨 [GPT_CHATBOT_PROCESSING_ERROR] 상세 에러 추적:")
        traceback.print_exc()
        print("="*60 + "\n")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI 튜터가 답변을 생성하는 과정에서 기술적 장애가 발생했습니다."
        )


@router.get("/rooms/{room_id}/messages", response_model=List[ChatMessageResponse])
async def get_room_message_history(
    room_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: any = Depends(get_current_user)
):
    """
    특정 대화방 내부의 과거 대화 히스토리(유저 질문 및 AI 답변)를 순서대로 가져옵니다.
    """
    try:
        user_id = await _get_authenticated_user_id(db, current_user)
        messages = await chatbot_service.get_room_messages(db=db, room_id=room_id, user_id=user_id)
        return messages
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        print(f"🚨 [CHAT_HISTORY_ERROR] {str(e)}")
        raise HTTPException(status_code=500, detail="대화 내역을 불러오지 못했습니다.")