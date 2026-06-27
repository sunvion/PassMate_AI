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
  role: "user" | "assistant";
  content: string;
};

type ChatRoomResponse = {
  id: number;
  user_id: number;
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
}): Promise<{ answer: string }> {
  // 1. 채팅방 생성
  const roomRes = await fetch(`${API_BASE_URL}/api/v1/chatbot/rooms`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({
      title: "오답노트 AI 테스트",
    }),
  });

  if (!roomRes.ok) {
    const errorText = await roomRes.text();

    console.error("AI 채팅방 생성 실패 상태:", roomRes.status);
    console.error("AI 채팅방 생성 실패 응답:", errorText);

    throw new Error("AI 채팅방 생성 실패");
  }

  const room: ChatRoomResponse = await roomRes.json();

  // 2. 생성된 채팅방에 질문 전송
  const messageRes = await fetch(
    `${API_BASE_URL}/api/v1/chatbot/rooms/${room.id}/messages`,
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
    answer:
      data.answer ??
      data.content ??
      data.message ??
      "AI 답변을 불러왔지만 응답 내용이 비어 있습니다.",
  };
}