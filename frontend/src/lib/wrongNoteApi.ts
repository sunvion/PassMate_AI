export type WrongNoteSummary = {
  id: number;
  title: string;
  exam_type: string;
  year: number | null;
  subject: string;
  wrong_count: number;
  unsolved_count: number;
  total_count: number;
  created_at: string;
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

function getAuthHeaders() {
  const token = localStorage.getItem("token");

  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

export async function getWrongNotebookSummary(): Promise<WrongNoteSummary[]> {
  const res = await fetch(`${API_BASE_URL}/api/v1/wrong-notebooks`, {
    headers: getAuthHeaders(),
  });

  if (!res.ok) {
    throw new Error("오답노트 목록 조회 실패");
  }

  return res.json();
}

export async function deleteWrongNotebook(wrongNotebookId: number) {
  const res = await fetch(
    `${API_BASE_URL}/api/v1/wrong-notebooks/${wrongNotebookId}`,
    {
      method: "DELETE",
      headers: getAuthHeaders(),
    }
  );

  if (!res.ok) {
    throw new Error("오답노트 삭제 실패");
  }

  return res.json();
}

export type WrongNoteQuestion = {
  question_id: number;
  room_id?: number | null;
  chat_room_id?: number | null;
  question_number?: number;
  number?: number;
  question: string;
  image_url?: string | null;
  options: {
    [key: string]: string;
  };
  selected_option: number[];
  correct_answer: number[];
  is_correct: boolean;
  status: "wrong" | "unsolved";
  explanation: string | null;
  submitted_at: string;
};

export type WrongNotebookDetail = {
  id: number;
  title: string;
  exam_type: string;
  year: number | null;
  subject: string;
  items: WrongNoteQuestion[];
};

export async function getWrongNotebookDetail(
  wrongNotebookId: number
): Promise<WrongNotebookDetail> {
  const res = await fetch(
    `${API_BASE_URL}/api/v1/wrong-notebooks/${wrongNotebookId}`,
    {
      headers: getAuthHeaders(),
    }
  );

  if (!res.ok) {
    throw new Error("오답노트 상세 조회 실패");
  }

  return res.json();
}

export type WrongNoteChatMessage = {
  id?: number;
  room_id?: number;
  question_id?: number;
  role: "user" | "assistant";
  content: string;
  created_at?: string;
};

type ChatRoomResponse = {
  id: number;
  user_id: number;
  question_id?: number | null;
  title: string;
  created_at: string;
};

type ChatMessageResponse = {
  id?: number;
  role?: "user" | "assistant";
  content?: string;
  answer?: string;
  message?: string;
};

// AI 질문 요청
export async function askWrongNoteAI(params: {
  questionId: number;
  message: string;
  roomId?: number | null;
}): Promise<{ answer: string; roomId: number }> {
  let roomId = params.roomId;

  // 기존 채팅방이 없을 때만 새로 생성
  if (!roomId) {
    const roomRes = await fetch(`${API_BASE_URL}/api/v1/chatbot/rooms`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({
        title: "오답노트 AI 테스트",
        question_id: params.questionId,
      }),
    });

    if (!roomRes.ok) {
      const errorText = await roomRes.text();

      console.error("AI 채팅방 생성 실패 상태:", roomRes.status);
      console.error("AI 채팅방 생성 실패 응답:", errorText);

      throw new Error("AI 채팅방 생성 실패");
    }

    const room: ChatRoomResponse = await roomRes.json();
    roomId = room.id;
  }

  // 기존 채팅방 또는 새로 만든 채팅방에 질문 전송
  const messageRes = await fetch(
    `${API_BASE_URL}/api/v1/chatbot/rooms/${roomId}/messages`,
    {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({
        content: params.message,
        question_id: params.questionId,
      }),
    }
  );

  if (!messageRes.ok) {
    throw new Error("AI 질문 요청 실패");
  }

  const data: ChatMessageResponse = await messageRes.json();

  console.log("AI 응답:", data);

  return {
    roomId,
    answer:
      data.answer ??
      data.content ??
      data.message ??
      "AI 답변을 불러왔지만 응답 내용이 비어 있습니다.",
  };
}

//채팅방 기록 유지
export async function getWrongNoteChatMessages(
  roomId: number
): Promise<WrongNoteChatMessage[]> {
  const res = await fetch(
    `${API_BASE_URL}/api/v1/chatbot/rooms/${roomId}/messages`,
    {
      headers: getAuthHeaders(),
    }
  );

  if (!res.ok) {
    throw new Error("AI 대화 이력 조회 실패");
  }

  return res.json();
}