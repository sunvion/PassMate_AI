import { ExamQuestionsResponse, Question, SelectedAnswers } from "@/types/exam";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export async function getExamQuestions(params: {
  examType: string;
  subject: string;
  year?: string;
}): Promise<ExamQuestionsResponse> {
  const query = new URLSearchParams({
    exam_type: params.examType,
    subject: params.subject,
  });

  if (params.year) {
    query.append("year", params.year);
  }

  const res = await fetch(
    `${API_BASE_URL}/api/v1/exams/questions?${query.toString()}`,
    {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
      cache: "no-store",
    }
  );

  if (!res.ok) {
    const errorText = await res.text();
    console.error("문제 조회 실패:", res.status, errorText);
    throw new Error("문제를 불러오지 못했습니다.");
  }

  const data: Question[] = await res.json();

  let questions: Question[];

  if (params.examType === "DRIVERS_LICENSE_1") {
    questions = [...data]
      .sort(() => Math.random() - 0.5)
      .slice(0, 40)
      .map((question, index) => ({
        ...question,
        number: index + 1,
      }));
  } else {
    questions = data.map((question) => ({
      ...question,
    }));
  }

  return {
    examId: 0,
    title: `${params.year ?? ""} ${params.examType} ${params.subject}`,
    questions,
  };
}

export async function submitBulkAnswers(
  examId: string,
  answers: SelectedAnswers
) {
  const body = {
    exam_id: Number(examId),
    answers: Object.entries(answers).map(([questionId, selectedChoice]) => ({
      question_id: Number(questionId),
      selected_choice: selectedChoice,
    })),
  };

  const res = await fetch(`${API_BASE_URL}/api/v1/attempts/bulk`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
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