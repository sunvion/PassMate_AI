export type WrongNoteSummary = {
  exam_type: string;
  year: number | null;
  subject: string;
  wrong_count: number;
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
  const res = await fetch(`${API_BASE_URL}/api/v1/statistics/wrong-notebook`, {
    headers: getAuthHeaders(),
  });

  if (!res.ok) {
    throw new Error("오답노트 목록 조회 실패");
  }

  return res.json();
}