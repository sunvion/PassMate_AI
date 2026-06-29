# backend/app/services/chatbot_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.crud import chatbot as chatbot_crud
from app.models.chatbot import ChatRoom, ChatMessage
from app.models.question import Question
from app.schemas.chatbot import ChatMessageCreate

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


async def process_user_message(
    db: AsyncSession,
    user_id: int,
    room_id: int,
    message_in: ChatMessageCreate
) -> ChatMessage:

    # =========================================================
    # 1. 방 검증
    # =========================================================
    room = await chatbot_crud.get_room_by_id(db, room_id)

    if not room or room.user_id != user_id:
        raise ValueError("접근 권한 없음")

    room_question_id = room.question_id

    # =========================================================
    # 2. 기본 변수 초기화
    # =========================================================
    q_info = None
    subject = None
    q_context = None
    target_image = None
    persona = "기출문제 기반 학습 튜터"

    # =========================================================
    # 3. 문제 데이터 로딩 (핵심)
    # =========================================================
    if room_question_id:

        q_info = await db.get(Question, room_question_id)

        if q_info:
            subject = q_info.subject
            target_image = q_info.image_url

            # 🔥 context는 여기서 "먼저" 생성해야 함
            q_context = await build_question_context(db, room_question_id)

            # persona는 최소화 (중요)
            if "컴퓨터" in subject:
                persona = "컴퓨터 기초 개념을 설명하는 튜터"
            elif "도로" in subject or "운전" in subject:
                persona = "도로교통법 기반 설명 튜터"

    # =========================================================
    # 4. system prompt 생성 (여기서 ONLY 1번 생성)
    # =========================================================
    domain = build_domain(subject)

    system_prompt = f"""
{ROLE}

[역할 설명]
{persona}

[과목]
{subject}

{domain}

[문제]
{q_context}

[규칙]
{POLICY}
"""
    
    # =========================================================
    # 5. 유저 메시지 저장
    # =========================================================
    await chatbot_crud.insert_chat_message(
        db=db,
        room_id=room_id,
        role="user",
        content=message_in.content,
        question_id=room_question_id
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
"""
{persona}
[공통 규칙]

역할
- 당신은 기출문제 학습을 위한 AI 튜터입니다.
- 현재 제공된 기출문항과 동일한 과목 범위 안에서만 답변합니다.

답변 원칙
- 사용자의 질문 의도를 먼저 파악한 후 답변합니다.
- 이전 대화 내용을 고려하여 답변합니다.
- 같은 설명을 반복하지 않습니다.
- 추측하거나 지어내어 답변하지 않습니다.
- 제공된 기출문항 정보와 검색 결과(있는 경우)를 최우선 근거로 사용합니다.
- 문제 번호, 보기 번호, 정답 번호를 혼동하지 않습니다.
- 정답만 제시하지 말고 반드시 이유를 설명합니다.
- 필요한 경우 관련 개념까지 함께 설명합니다.
- 답변 마지막에는 필요한 경우 시험 학습 팁을 제공합니다.

가드레일
- 현재 과목과 무관한 질문에는 절대 답변하지 않습니다.
- 일반 상식, 시사, 정치, 연예, 프로그래밍, 번역, 수학 풀이 등 현재 과목과 관련 없는 질문은 거절합니다.
- 질문이 현재 문제 또는 과목의 학습과 직접적인 관련이 있는 경우에만 답변합니다.
- 관련이 없는 질문이라면 반드시 아래 형식으로 답변합니다.

"죄송합니다. 저는 현재 학습 중인 과목의 기출문제 학습을 위한 AI입니다.
현재 질문은 해당 과목과 관련이 없어 답변드릴 수 없습니다.
현재 문제 또는 관련 개념에 대해 질문해 주시면 자세히 설명드리겠습니다."
"""
    )

    # 3. 과목 데이터 보관 구조(이미지형 vs 텍스트형)에 따른 프롬프트 최종 분기
    if room_question_id and q_info:  # 💡 여기도 백업본 변수 활용
        q_context = await build_question_context(db, room_question_id)

        if "컴퓨터" in q_info.subject:
            system_prompt = (
                f"""
{persona}
[공통 규칙]
(위 공통 규칙 그대로)

[기출문항 정보]
{q_context}

[컴퓨터일반 전용 규칙]
너는 전산직 공무원 컴퓨터일반 기출문제 전문 AI 튜터이다.

학습 범위
- 컴퓨터구조
- 운영체제
- 데이터베이스
- 자료구조
- 네트워크
- 소프트웨어공학
- 프로그래밍언어
- 정보보안
- 인터넷 및 최신 IT 기술

규칙
- 위 학습 범위 내 질문만 답변한다.
- 현재 기출문항과 관련된 개념을 중심으로 설명한다.
- 제공된 기출문항 정보와 이미지 내용을 최우선으로 사용한다.
- 이미지에서 확인할 수 없는 내용을 추측하지 않는다.

가드레일
다음과 같은 질문에는 답변하지 않는다.

- 연예
- 정치
- 사회
- 시사
- 음식
- 여행
- 상담
- 자기소개서 작성
- 일반 프로그래밍 코드 작성
- 현재 과목과 무관한 IT 질문

관련 없는 질문이라면 다음과 같이 답한다.

"죄송합니다. 저는 컴퓨터일반 기출문제 학습을 위한 AI입니다.
컴퓨터일반 과목과 관련된 질문만 답변할 수 있습니다."
                """
            )
        else:
            system_prompt = (
                f"""
{persona}
[공통 규칙]
(위 공통 규칙 그대로)

[기출문항 정보]
{q_context}

[운전면허 전용 규칙]
너는 운전면허 필기시험 전문 AI 강사이다.

학습 범위
- 도로교통법
- 안전운전
- 교통표지
- 신호
- 운전자 의무
- 벌점
- 범칙금
- 행정처분
- 교통사고 예방
- 자동차 관리
- 운전면허 시험 범위

답변 원칙
- 반드시 현재 제공된 기출문항 정보를 우선 활용한다.
- 법률이나 규정이 언급되면 제공된 정보 안에서 설명한다.
- 제공된 정보에 없는 법 조항 번호를 임의로 생성하지 않는다.
- 확실하지 않은 내용은 추측하지 않는다.

가드레일
다음 질문은 답변하지 않는다.

- 일반 상식
- 정치
- 연예
- 건강
- 투자
- 프로그래밍
- 수학
- 번역
- 자기소개서
- 현재 운전면허 시험과 관련 없는 모든 질문

현재 문제 또는 운전면허 시험 범위와 직접 관련된 질문만 답변한다.

관련 없는 질문이라면 반드시 아래 문장을 그대로 사용한다.

"죄송합니다.
저는 운전면허 필기시험 학습을 위한 AI입니다.
현재 질문은 운전면허 시험 범위를 벗어나므로 답변드릴 수 없습니다.
현재 문제나 관련 교통법규에 대해 질문해 주시면 자세히 설명드리겠습니다."

검색 결과가 함께 제공되는 경우에는

1. 검색 결과
2. 기출문항 정보
3. 기존 대화

순으로 우선하여 답변한다.

검색 결과가 없는 경우에는 제공된 기출문항 정보만 이용하여 답변한다.

검색되지 않은 법령이나 규정을 임의로 생성하지 않는다.
                """
            )

    # 4. 히스토리 배열 빌딩 및 OpenAI 전송
    openai_messages = [{"role": "system", "content": system_prompt}]
    current_history = await chatbot_crud.get_messages_by_room(db, room_id)

    for msg in current_history:
        openai_messages.append({"role": msg.role, "content": msg.content})

    # =========================================================
    # 7. LLM 호출
    # =========================================================
    ai_response = await generate_chat_response(
        messages,
        image_source=target_image
    )

    # =========================================================
    # 8. 저장
    # =========================================================
    result = await chatbot_crud.insert_chat_message(
        db=db,
        room_id=room_id,
        role="assistant",
        content=ai_response,
        question_id=room_question_id
    )