# backend/app/services/chatbot_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.crud import chatbot as chatbot_crud
from app.models.chatbot import ChatRoom, ChatMessage
from app.models.question import Question  # 💡 과목 판별 조회를 위해 필수 포함
from app.schemas.chatbot import ChatRoomCreate, ChatMessageCreate  # ⚠️ [핵심 교정]: 이 라인이 누락되어 NameError가 났던 것입니다!

# 💡 프로젝트 구조에 준비되어 있는 LLM 및 컨텍스트 빌더 모듈 임포트
from app.services.context_builder import build_question_context
from app.services.llm_service import generate_chat_response


async def create_new_room(db: AsyncSession, user_id: int, room_in: ChatRoomCreate) -> ChatRoom:
    """
    [대화방 신설 및 선제적 가이드 메시지 캐싱]
    """
    # 1. 방 레코드 기본 생성 및 문제 ID 바인딩
    room = await chatbot_crud.create_chat_room(db=db, user_id=user_id, room_in=room_in)
    
    # 2. 과목군을 역추적하여 첫 인사말(웰컴 메시지) 동적 커스텀 적재
    welcome_content = "안녕하세요! 해당 문항에 대해 궁금한 점을 편하게 물어보세요. 보기 분석이나 핵심 개념을 1:1로 가르쳐 드립니다! 😊"
    
    if room_in.question_id:
        q_obj = await db.get(Question, room_in.question_id)
        if q_obj:
            if "컴퓨터" in q_obj.subject:
                welcome_content = f"안녕하세요! 💻 **컴퓨터일반** 전문 AI 튜터입니다. {q_obj.number}번 문제를 해설지와 함께 정밀 분석할 준비가 완료되었습니다. 질문을 입력해 주세요!"
            elif "도로" in q_obj.subject or "운전" in q_obj.subject:
                welcome_content = f"안녕하세요! 🚗 **운전면허** 전문 AI 강사입니다. {q_obj.number}번 문제에 대해서 무엇이든 대답해드릴게요. 무엇이 궁금하신가요?"

    # 3. 챗봇이 열리자마자 띄워줄 인사말을 assistant 역할로 DB에 즉시 캐시 저장
    # ⚠️ 이 내부의 commit 때문에 상단의 'room' 객체 속성들이 만료(Expire)됩니다.
    await chatbot_crud.insert_chat_message(
        db=db,
        room_id=room.id,
        role="assistant",
        content=welcome_content,
        question_id=room_in.question_id
    )
    
    # =================================================================
    # 🌟 [🌟 핵심 버그 수정]: 만료된 room 객체의 속성들을 비동기로 안전하게 새로고침합니다.
    # =================================================================
    await db.refresh(room)
    
    return room


async def get_user_rooms(db: AsyncSession, user_id: int) -> List[ChatRoom]:
    """
    [대화방 목록 조회] 특정 유저가 가지고 있는 모든 대화방 리스트를 반환합니다.
    """
    return await chatbot_crud.get_rooms_by_user(db=db, user_id=user_id)


async def get_room_messages(db: AsyncSession, room_id: int, user_id: int) -> List[ChatMessage]:
    """
    [대화 이력 조회] 대화방에 진입했을 때 과거 대화 타임라인을 안전하게 권한 검증 후 반환합니다.
    """
    # 🛡️ 보안 가드레이르: 타인의 대화방을 훔쳐보지 못하도록 소유권 검증
    room = await chatbot_crud.get_room_by_id(db, room_id)
    if not room or room.user_id != user_id:
        raise ValueError("해당 대화방에 접근할 권한이 없거나 존재하지 않는 방입니다.")
        
    return await chatbot_crud.get_messages_by_room(db=db, room_id=room_id)


async def process_user_message(db: AsyncSession, user_id: int, room_id: int, message_in: ChatMessageCreate) -> ChatMessage:
    """
    [대화 진행 인터셉터]
    마스터 룸에 바인딩된 원래 기출문제 정보를 기반으로 매 질문 턴마다 완벽한 문맥 프롬프트를 재생성합니다.
    """
    room = await chatbot_crud.get_room_by_id(db, room_id)
    if not room or room.user_id != user_id:
        raise ValueError("해당 대화방에 메시지를 보낼 권한이 없습니다.")

    # =================================================================
    # 🌟 [핵심 버그 수정]: 내부 commit에 의해 room 객체가 만료되기 전에
    # 필요한 속성(question_id)을 로컬 변수에 스냅샷으로 안전하게 백업합니다.
    # =================================================================
    room_question_id = room.question_id

    # 1. 유저 질문 적재 (⚠️ 이 내부의 commit 때문에 상단 room 객체가 만료됨)
    await chatbot_crud.insert_chat_message(
        db=db,
        room_id=room_id,
        role="user",
        content=message_in.content,
        question_id=room_question_id  # 백업된 변수 사용
    )

    # 2. 과목분류별 최적화 페르소나 및 이미지 소스 준비 단계
    persona = "너는 친절하고 전문적인 기출문제 오답 클리닉 선생님이야."
    q_info = None
    target_image = None

    if room_question_id:  # 💡 만료된 room.question_id 대신 백업본 변수 사용!
        q_info = await db.get(Question, room_question_id)
        if q_info:
            target_image = q_info.image_url
            if "컴퓨터" in q_info.subject:
                persona = "너는 컴퓨터구조, 데이터베이스, 운영체제론, 자료 구조, 프로그래밍 언어론, 소프트웨어 공학 및 시스템 설계, 데이터 통신과 네트워크, 인터넷 및 최신 기술 용어의 내부 원리를 꿰뚫고 있는 전산직 공무원 1:1 전문 기술 과외 강사야. 전공 도메인 지식에 근거해 매우 논리적이고 단계적으로 가르쳐줘."
            elif "도로" in q_info.subject or "운전" in q_info.subject:
                persona = "너는 국가 도로교통법 조항 및 교통안전 규칙 표준 지침에 정통한 법규 강사야. 벌점 기준, 행정 처분, 도로 수칙 등의 법적 근거를 명확히 선언하며 차분하게 설명해줘."

    # 기본 베이스 가이드라인 라인 조립
    system_prompt = (
        f"{persona}\n"
        f"학생이 문제를 왜 틀렸는지 자가진단할 수 있도록 유도하고, 정답 해설을 보아도 놓쳤던 맹점 개념을 채워주는 것이 임무야.\n"
        f"항상 정중한 존댓말로 친절하게 과외하듯 대답해줘."
    )

    # 3. 과목 데이터 보관 구조(이미지형 vs 텍스트형)에 따른 프롬프트 최종 분기
    if room_question_id and q_info:  # 💡 여기도 백업본 변수 활용
        q_context = await build_question_context(db, room_question_id)
        
        if "컴퓨터" in q_info.subject:
            system_prompt = (
                f"{persona}\n"
                "아래 제공되는 [기출문항 정보]와 함께 입력되는 '이미지 파일'을 완벽히 매칭하여 학생의 질문에 답변해야 해.\n\n"
                f"[🚨 기출문항 정보]\n{q_context}\n\n"
                "💡 [★멀티모달 시각 지침★]\n"
                "1. 현재 문제의 보기(①~④)는 데이터베이스에 텍스트로 저장되어 있지 않고, 함께 입력되는 '이미지 파일'에 포함되어 있어.\n"
                "2. 학생이 '4번 보기 왜 틀림?', '③번 보기 보충 설명해줘'와 같이 특정 보기를 짚어 질문하면, 이미지 속에서 해당 번호의 텍스트와 내용을 직접 눈으로 확인하고 정확하게 매칭하여 해설해줘.\n"
                "3. 이미지에 포함된 글자가 조금 흐릿하더라도 맥락(컴퓨터일반 지식)을 고려하여 가장 정확한 IT 전문 용어로 해석해야 해.\n"
                "4. 만약 이미지 식별이 불가능할 정도로 깨져 있다면 환각(지어내기)을 일으키지 말고, '회원님, 이미지 속 보기 글자가 흐려 정확한 식별이 어렵습니다. 번거로우시겠지만 보기 내용을 적어주시면 더 자세히 설명해 드릴게요!'라고 안내해줘.\n\n"
                "친절하고 명확한 어조로, 전문성이 느껴지게 마크다운 문법을 활용하여 대답해줘."
            )
        else:
            system_prompt = (
                f"{persona}\n"
                "아래 제공되는 완전무결한 [기출문항 정보] 데이터 세트를 기반으로 학생의 질문에 명쾌하게 답변해야 해.\n\n"
                f"[🚨 기출문항 정보]\n{q_context}\n\n"
                "💡 [텍스트 매칭 가이드라인]\n"
                "1. 본 운전면허 문항은 질문 발문과 보기 목록((1)~(4)), 공식 정답 및 출제자 해설이 모두 텍스트로 완벽히 등록되어 있어.\n"
                "2. 따라서 학생이 '3번 보기 설명해줘' 혹은 '왜 2번은 정답이 아니야?'라고 질문하면, 위의 [기출문항 정보] 내 '보기 구성 목록' 텍스트를 즉시 대조하여 관련된 도로교통법 조항 근거와 함께 정확하게 과외 튜팅을 제공해줘.\n"
                "3. 제공된 텍스트 콘텍스트를 최우선으로 신뢰하여 답변하고, 정중하고 친절한 톤을 상시 유지해줘."
            )

    # 4. 히스토리 배열 빌딩 및 OpenAI 전송
    openai_messages = [{"role": "system", "content": system_prompt}]
    current_history = await chatbot_crud.get_messages_by_room(db, room_id)
    
    for msg in current_history:
        openai_messages.append({"role": msg.role, "content": msg.content})

    # 5. llm_service.py에 이미지 경로를 파라미터로 넘겨 Vision 활성화
    ai_generated_content = await generate_chat_response(openai_messages, image_source=target_image)

    # 6. GPT 최종 피드백 답변 저장 후 컨트롤러 반환
    ai_message_record = await chatbot_crud.insert_chat_message(
        db=db,
        room_id=room_id,
        role="assistant",
        content=ai_generated_content,
        question_id=room_question_id  # 💡 여기도 안전하게 백업본 변수 주입
    )
    return ai_message_record