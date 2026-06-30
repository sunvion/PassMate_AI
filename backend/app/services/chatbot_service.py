# backend/app/services/chatbot_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.crud import chatbot as chatbot_crud
from app.models.chatbot import ChatRoom, ChatMessage
from app.models.question import Question
from app.schemas.chatbot import ChatRoomCreate, ChatMessageCreate 

# 💡 프로젝트 구조에 준비되어 있는 LLM 및 컨텍스트 빌더 모듈 임포트
from app.services.context_builder import build_question_context
from app.services.llm_service import generate_chat_response
from app.services.rag.law_rag import search_law

# 💡 [★멀티모달 시각 지침★]
# 1. 현재 문제의 보기(①~④)는 데이터베이스에 텍스트로 저장되어 있지 않고, 함께 입력되는 '이미지 파일'에 포함되어 있어.
# 2. 학생이 '4번 보기 왜 틀림?', '③번 보기 보충 설명해줘'와 같이 특정 보기를 짚어 질문하면, 이미지 속에서 해당 번호의 텍스트와 내용을 직접 눈으로 확인하고 정확하게 매칭하여 해설해줘.
# 3. 이미지에 포함된 글자가 조금 흐릿하더라도 맥락(컴퓨터일반 지식)을 고려하여 가장 정확한 IT 전문 용어로 해석해야 해.
# 4. 만약 이미지 식별이 불가능할 정도로 깨져 있다면 환각(지어내기)을 일으키지 말고, '회원님, 이미지 속 보기 글자가 흐려 정확한 식별이 어렵습니다. 번거로우시겠지만 보기 내용을 적어주시면 더 자세히 설명해 드릴게요!'라고 안내해줘.


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

    # =========================================================
    # 3. 과목 분류별 페르소나 및 이미지 스소스/기출 정보 준비 단계
    # =========================================================
    persona = "너는 친절하고 전문적인 기출문제 오답 클리닉 선생님이야."
    q_info = None
    target_image = None
    q_context = "제공된 명시적 문항 정보가 없습니다."
    law_context = ""

    if room_question_id:
        q_info = await db.get(Question, room_question_id)
        if q_info:
            target_image = q_info.image_url
            # 💡 기출문제의 세부 텍스트 덩어리(발문, 선지, 정답) 고속 빌드
            q_context = await build_question_context(db, room_question_id)

            if "컴퓨터" in q_info.subject:
                persona = "너는 컴퓨터구조, 데이터베이스, 운영체제론, 자료 구조, 프로그래밍 언어론, 소프트웨어 공학 및 시스템 설계, 데이터 통신 및 네트워크, 인터넷 및 최신 기술 용어의 내부 원리를 꿰뚫고 있는 전산직 공무원 1:1 전문 기술 과외 강사야. 전공 도메인 지식에 근거해 매우 논리적이고 단계적으로 가르쳐줘."
            elif "도로" in q_info.subject or "운전" in q_info.subject:
                persona = "너는 국가 도로교통법 조항 및 교통안전 규칙 표준 지침에 정통한 법규 강사야. 벌점 기준, 행정 처분, 도로 수칙 등의 법적 근거를 명확히 선언하며 차분하게 설명해줘."
                
                # RAG 검색 수행 (질문을 기반으로 관련 법령 검색)
                try:
                    law_chunks = search_law(message_in.content)
                    print("=" * 50)
                    print("RAG SEARCH RESULT")
                    print(law_chunks)
                    print("=" * 50)
                    if law_chunks:
                        law_text = "\n".join([f"- {c['content']}" for c in law_chunks])
                        law_context = f"\n[검색 결과]\n{law_text}\n"
                except Exception as e:
                    # RAG 검색 실패 시에도 로그만 출력하고 빈 컨텍스트로 fallback하여 기존 GPT 동작 유지
                    print(f"⚠️ [RAG_SEARCH_FALLBACK] RAG 검색 중 오류 발생으로 기본 GPT 우회: {str(e)}")

    # =========================================================
    # 4. 프롬프트 프레임 생성 (공통 가이드라인 선언)
    # =========================================================
    common_rules = """역할
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

    # 3. 과목 데이터 보관 구조(이미지형 vs 텍스트형)에 따른 프롬프트 최종 분기
    if room_question_id and q_info:  # 💡 여기도 백업본 변수 활용
        q_context = await build_question_context(db, room_question_id)
        
        if "컴퓨터" in q_info.subject:
            system_prompt = f"""{persona}
[공통 규칙]
{common_rules}

[기출문항 정보]
{q_context}

[컴퓨터일반 전용 규칙]
너는 전산직 공무원 컴퓨터일반 기출문제 전문 AI 튜터이다.

학습 범위
- 컴퓨터구조, 운영체제, 데이터베이스, 자료구조, 네트워크, 소프트웨어공학, 프로그래밍언어, 정보보안, 인터넷 및 최신 IT 기술


규칙
- 위 학습 범위 내 질문만 답변한다.
- 현재 기출문항과 관련된 개념을 중심으로 설명한다.
- 제공된 기출문항 정보와 이미지 내용을 최우선으로 사용한다.
- 이미지에서 확인할 수 없는 내용을 추측하지 않는다.

가드레일
다음과 같은 질문에는 답변하지 않는다.
- 연예, 정치, 사회, 시사, 음식, 여행, 상담, 자기소개서 작성, 일반 프로그래밍 코드 작성, 현재 과목과 무관한 IT 질문

관련 없는 질문이라면 다음과 같이 답한다.
"죄송합니다. 저는 컴퓨터일반 기출문제 학습을 위한 AI입니다.
컴퓨터일반 과목과 관련된 질문만 답변할 수 있습니다."
"""
        else:
            system_prompt = f"""{persona}

[공통 규칙]
{common_rules}

[기출문항 정보]
{q_context}

{law_context}

[운전면허 전용 규칙]

너는 운전면허 필기시험 기출문제 전문 AI 강사이다.

==========================
학습 범위
==========================

다음 범위에 대해서만 답변한다.

- 도로교통법
- 도로교통법 시행령
- 도로교통법 시행규칙
- 자동차 및 자동차부품의 성능과 기준에 관한 규칙
- 교통안전
- 교통표지
- 신호
- 운전자의 의무
- 벌점
- 범칙금
- 행정처분
- 운전면허 필기시험 범위

==========================
답변 원칙
==========================

- 현재 기출문항을 우선적으로 참고한다.
- 이전 대화 내용을 함께 고려한다.
- 검색 결과(RAG)가 제공된 경우 검색 결과를 가장 중요한 근거로 사용한다.
- 검색 결과에 포함된 법령명과 조항은 가능한 그대로 인용한다.
- 검색 결과에 없는 법령은 절대로 만들어내지 않는다.
- 확실하지 않은 내용은 모른다고 답한다.
- 법령을 설명할 때에는 법령명과 함께 설명한다.
- 단순히 정답만 말하지 말고 이유도 함께 설명한다.

==========================
관련 질문의 범위
==========================

다음 질문은 모두 운전면허 시험 범위의 질문으로 간주한다.

- 현재 문제에 대한 질문
- 보기에 대한 질문
- 정답 이유
- 오답 이유
- 관련 개념
- 관련 교통법규
- 관련 법령
- 특정 법 조항
- 신호의 의미
- 교통표지
- 벌점
- 범칙금
- 안전운전 방법
- 운전면허 시험에서 출제되는 모든 내용

==========================
가드레일
==========================

다음 질문에는 답변하지 않는다.

- 정치
- 연예
- 투자
- 건강 상담
- 일반 상식
- 프로그래밍
- 번역
- 자기소개서
- 현재 운전면허 시험과 무관한 질문

다만,

운전면허 시험 범위와 관련된 질문이라면

- 법령 질문
- 교통법규 질문
- 신호 질문
- 운전 상황 질문
- 시험 개념 질문

모두 답변한다.

검색 결과가 존재하는 경우에는
해당 질문을 운전면허 시험 범위의 질문으로 판단하고
절대로 "시험 범위를 벗어난 질문"이라고 거절하지 않는다.

==========================
검색 결과 활용 규칙
==========================

검색 결과가 존재하면

1. 검색 결과
2. 기출문항 정보
3. 이전 대화

순으로 활용하여 답변한다.

검색 결과가 존재하면
검색 결과의 법령을 근거로 설명한다.

검색 결과가 없으면
기출문항 정보만 활용한다.

==========================
거절 문구
==========================

운전면허 시험과 전혀 관계없는 질문인 경우에만 아래 문장을 사용한다.

"죄송합니다.
저는 운전면허 필기시험 학습을 위한 AI입니다.
현재 질문은 운전면허 시험 범위를 벗어나므로 답변드릴 수 없습니다.
현재 문제나 관련 교통법규에 대해 질문해 주시면 자세히 설명드리겠습니다."
"""
    else:
        system_prompt = f"{persona}\n학생의 질문에 정중하고 친절한 어조로 상세히 대답해줘."

    # =========================================================
    # 6. 히스토리 배열 빌딩 및 OpenAI 전송 팩 조립
    # =========================================================
    openai_messages = [{"role": "system", "content": system_prompt}]
    current_history = await chatbot_crud.get_messages_by_room(db, room_id)
    
    for msg in current_history:
        openai_messages.append({"role": msg.role, "content": msg.content})

    # 🚨 디버깅 가드 설치
    print("==== [VISION DEBUG] IMAGE SOURCE CHECK ====")
    print(f"🔹 DB에서 조회된 image_url: {target_image}")
    print(f"🔹 과목명(subject): {q_info.subject if q_info else '인포 없음'}")
    print("===========================================")

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