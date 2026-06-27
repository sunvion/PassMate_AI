import { ExamQuestionsResponse, Question, SelectedAnswers } from "@/types/exam";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export async function getExamQuestions(params: {
  examType: string;
  subject: string;
  year?: string;
  limit?: number;
  random?: boolean;
}): Promise<ExamQuestionsResponse> {
  const query = new URLSearchParams({
    exam_type: params.examType,
    subject: params.subject,
  });

  if (params.year) query.append("year", params.year);
  if (params.limit) query.append("limit", String(params.limit));
  if (params.random) query.append("random", "true");

  const res = await fetch(
    `${API_BASE_URL}/api/v1/exams/questions?${query.toString()}`,
    {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      cache: "no-store",
    }
  );

  if (!res.ok) {
    const errorText = await res.text();
    console.error("문제 조회 실패:", res.status, errorText);
    throw new Error("문제를 불러오지 못했습니다.");
  }

  const data: Question[] = await res.json();
  const isDriverLicense = params.examType.startsWith("DRIVERS_LICENSE");

  const questions = isDriverLicense
    ? [...data]
        .sort(() => Math.random() - 0.5)
        .slice(0, params.limit ?? 40)
        .map((question, index) => ({
          ...question,
          number: index + 1,
        }))
    : data.map((question) => ({ ...question }));

  return {
    examId: 0,
    title: `${params.year ?? ""} ${params.examType} ${params.subject}`,
    questions,
  };
}

export async function submitBulkAnswers(
  examId: string,
  answers: SelectedAnswers,
  questions: Question[]
) {
  const body = {
    attempts: questions.map((question) => ({
      question_id: question.id,
      selected_option:
        answers[question.id] !== undefined ? [answers[question.id]] : [],
      time: 0,
    })),
  };

  const token = localStorage.getItem("token");

  const res = await fetch(`${API_BASE_URL}/api/v1/attempts/bulk`, {
    method: "POST",
    mode: "cors",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const errorText = await res.text();
    console.error("제출 실패:", res.status, errorText);
    throw new Error("제출에 실패했습니다.");
  }

  return res.json();
}

export async function saveLearningProgress(
  examType: string,
  subject: string,
  year: number | null,
  lastQuestionId: number,
  solvedCount: number
) {
  const token = localStorage.getItem("token");

  const res = await fetch(`${API_BASE_URL}/api/v1/statistics/progress`, {
    method: "POST",
    mode: "cors",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({
      exam_type: examType,
      subject,
      year,
      last_question_id: lastQuestionId,
      solved_count: solvedCount,
    }),
  });

  if (!res.ok) {
    const errorText = await res.text();
    console.error("진행 상태 저장 실패:", res.status, errorText);
    throw new Error("진행 상태 저장 실패");
  }

  return res.json();
}

export type LatestProgress = {
  exam_type: string;
  subject: string;
  year: number | null;
  last_question_id: number;
  solved_count: number;
  total_count: number;
  remaining_count: number;
  progress_percent: number;
  updated_at: string;
};

export async function getLatestProgress(): Promise<LatestProgress[]> {
  const token = localStorage.getItem("token");

  const res = await fetch(`${API_BASE_URL}/api/v1/statistics/latest-progress`, {
    method: "GET",
    mode: "cors",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    cache: "no-store",
  });

  if (!res.ok) {
    const errorText = await res.text();
    console.error("최근 학습 진행 상태 조회 실패:", res.status, errorText);
    throw new Error("최근 학습 진행 상태 조회 실패");
  }

  return res.json();
}

export async function getResumeAttemptQuestions(
  attemptId: number
): Promise<ExamQuestionsResponse> {
  const token = localStorage.getItem("token");

  const res = await fetch(`${API_BASE_URL}/api/v1/attempts/${attemptId}/resume`, {
    method: "GET",
    mode: "cors",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    cache: "no-store",
  });

  if (!res.ok) {
    const errorText = await res.text();
    console.error("이어풀기 문제 조회 실패:", res.status, errorText);
    throw new Error("이어풀기 문제를 불러오지 못했습니다.");
  }

  const data = await res.json();

  return {
    examId: attemptId,
    title: data.title ?? "이어풀기",
    questions: data.questions ?? data,
  };
}