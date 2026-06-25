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

export type WrongNoteChatMessage = {
  role: "user" | "assistant";
  content: string;
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

export async function askWrongNoteAI(params: {
  questionId: number;
  message: string;
}): Promise<{ answer: string }> {
  const res = await fetch(`${API_BASE_URL}/api/v1/ai/wrong-note-chat`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({
      question_id: params.questionId,
      message: params.message,
    }),
  });

  if (!res.ok) {
    throw new Error("AI 질문 요청 실패");
  }

  return res.json();
}