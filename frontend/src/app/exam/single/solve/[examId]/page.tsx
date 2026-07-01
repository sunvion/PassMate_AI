// 한 문제씩 풀기
"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

import Header from "@/components/Header";
import Sidebar from "@/components/Sidebar";
import SolveHeader from "@/components/exams/SolveHeader";
import QuestionCard from "@/components/exams/QuestionCard";
import QuestionNavigator from "@/components/exams/QuestionNavigator";

import { getExamQuestions, getResumeAttemptQuestions, submitBulkAnswers, saveLearningProgress } from "@/lib/examApi";
import { Question, SelectedAnswers } from "@/types/exam";

export default function SingleSolvePage() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const examType = searchParams.get("exam_type") || "";
  const subject = searchParams.get("subject") || "";
  const year = searchParams.get("year") || "";
  const limit = searchParams.get("limit");
  const random = searchParams.get("random");
  // 한 문제 씩 이어풀기
  const isResume = searchParams.get("resume") === "true";
  const lastQuestionId = Number(searchParams.get("last_question_id"));

  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<SelectedAnswers>({});
  const [checkedQuestions, setCheckedQuestions] = useState<Record<number, boolean>>({});
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");
  const [saveMessage, setSaveMessage] = useState("");

  const currentQuestion = questions[currentIndex];

  const attemptId = searchParams.get("attempt_id");

  const answeredCount = Object.keys(answers).length;
  const progressPercent =
    questions.length > 0 ? Math.round((answeredCount / questions.length) * 100) : 0;

  const getExamTypeLabel = (examType: string) => {
    switch (examType) {
      case "CS_GENERAL":
        return "국가직";
      case "CS_LOCAL":
        return "지방직";
      case "DRIVERS_LICENSE_1":
      case "DRIVERS_LICENSE_2":
        return "운전면허 필기";
      default:
        return examType;
    }
  };

  const displayTitle = useMemo(() => {
    if (examType.startsWith("DRIVERS_LICENSE")) {
      return "운전면허 필기";
    }

    if (year) {
      return `${year} ${getExamTypeLabel(examType)} ${subject}`;
    }

    return `${getExamTypeLabel(examType)} ${subject}`;
  }, [examType, subject, year]);

  useEffect(() => {
    const fetchQuestions = async () => {
      try {
        setIsLoading(true);
        setErrorMessage("");

        let data;

        if (isResume && attemptId) {
          // 이어풀기 정보(선택했던 답)
          const resumeData = await getResumeAttemptQuestions(Number(attemptId));

          // 기존 문제 정보(정답 포함)
          const originalData = await getExamQuestions({
            examType,
            subject,
            year: year || undefined,
          });

          // resume + 기존 문제를 id 기준으로 합침
          const mergedQuestions = resumeData.questions.map((resumeQuestion: any) => {
            const originalQuestion = originalData.questions.find(
              (question) => question.id === resumeQuestion.id
            );

            return {
              ...resumeQuestion,

              // 기존 문제 API에서 정답 가져오기
              answer: originalQuestion?.answer ?? [],
            };
          });

          data = {
            ...resumeData,
            questions: mergedQuestions,
          };
        } else {
          data = await getExamQuestions({
            examType,
            subject,
            year: year || undefined,
            limit: limit ? Number(limit) : undefined,
            random: random === "true",
          });
        }

        const formattedQuestions = data.questions
          .map((q: any) => ({
            id: q.id,
            number: q.number,
            text: q.text ?? q.question ?? "",
            imageUrl: q.imageUrl ?? q.image_url ?? null,
            explanation: q.explanation ?? null,
            answer: Array.isArray(q.answer)
              ? q.answer.map(Number)
              : [Number(q.answer)],
            selected_option: Array.isArray(q.selected_option)
              ? q.selected_option.map(Number)
              : [],
            choices: Object.entries(q.options ?? {}).map(([number, text]) => ({
              id: Number(number),
              number: Number(number),
              text: String(text),
              imageUrl: null,
            })),
          }))
          .sort((a: Question, b: Question) => a.number - b.number);

        setQuestions(formattedQuestions);

        if (isResume) {
          const restoredAnswers: SelectedAnswers = {};

          formattedQuestions.forEach((question: any) => {
            if (question.selected_option?.length > 0) {
              restoredAnswers[question.id] = question.selected_option[0];
            }
          });

          setAnswers(restoredAnswers);
        }

        if (isResume && lastQuestionId) {
          const resumeIndex = formattedQuestions.findIndex(
            (question) => question.id === lastQuestionId
          );

          if (resumeIndex >= 0) {
            setCurrentIndex(resumeIndex);
          }
        }
      } catch (error) {
        console.error(error);
        setErrorMessage("문제를 불러오지 못했습니다.");
      } finally {
        setIsLoading(false);
      }
    };

    if (!examType || !subject) {
      setIsLoading(false);
      setErrorMessage("시험 정보가 부족합니다.");
      return;
    }

    fetchQuestions();
  }, [examType, subject, year, limit, random, isResume, lastQuestionId, attemptId]);

  const handleSelectChoice = (questionId: number, choiceNumber: number) => {
    if (checkedQuestions[questionId]) return;

    setAnswers((prev) => ({
      ...prev,
      [questionId]: choiceNumber,
    }));
  };

  const handleCheckAnswer = () => {
    if (!currentQuestion) return;

    if (answers[currentQuestion.id] === undefined) {
      alert("먼저 답을 선택해주세요.");
      return;
    }

    setCheckedQuestions((prev) => ({
      ...prev,
      [currentQuestion.id]: true,
    }));
  };

  const handleSaveProgress = async () => {
    if (!currentQuestion) return;

    try {
      // 현재 선택한 답변들도 저장
      await submitBulkAnswers(examType, answers, questions);

      // 이어풀기 위치/진행률 저장
      await saveLearningProgress(
        examType,
        subject,
        year ? Number(year) : null,
        currentQuestion.id,
        answeredCount
      );

      setSaveMessage("학습 상태가 저장되었어요.");

      setTimeout(() => {
        router.push("/mypage");
      }, 900);
    } catch (error) {
      console.error(error);
      setSaveMessage("학습 상태 저장에 실패했어요.");
    }
  };

  const handleMoveQuestion = (index: number) => {
    setCurrentIndex(index);
  };

  const handlePrev = () => {
    setCurrentIndex((prev) => Math.max(prev - 1, 0));
  };

  const handleNext = () => {
    setCurrentIndex((prev) => Math.min(prev + 1, questions.length - 1));
  };

  const handleSubmitSolvedOnly = async () => {
    if (Object.keys(answers).length === 0) {
      alert("채점할 문제가 없습니다.");
      return;
    }

    try {
      await submitBulkAnswers(examType, answers, questions);
      router.push("/wrong-note");
    } catch (error) {
      console.error(error);
      alert("채점 중 오류가 발생했습니다.");
    }
  };

  if (isLoading) {
    return (
      <main className="min-h-screen bg-slate-50 text-slate-900">
        <Header onMenuClick={() => setIsMenuOpen(true)} onLoginClick={() => { }} />
        <Sidebar isOpen={isMenuOpen} onClose={() => setIsMenuOpen(false)} />
        <div className="pt-28 text-center text-slate-500">
          문제를 불러오는 중입니다...
        </div>
      </main>
    );
  }

  if (errorMessage || questions.length === 0) {
    return (
      <main className="min-h-screen bg-slate-50 text-slate-900">
        <Header onMenuClick={() => setIsMenuOpen(true)} onLoginClick={() => { }} />
        <Sidebar isOpen={isMenuOpen} onClose={() => setIsMenuOpen(false)} />
        <div className="pt-28 text-center text-red-500">
          {errorMessage || "문제가 없습니다."}
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <Header onMenuClick={() => setIsMenuOpen(true)} onLoginClick={() => { }} />
      <Sidebar isOpen={isMenuOpen} onClose={() => setIsMenuOpen(false)} />

      <section className="pt-16">
        <div className="min-h-screen bg-white">
          <SolveHeader
            title={displayTitle}
            currentNumber={currentIndex + 1}
            totalCount={questions.length}
            answeredCount={answeredCount}
            progressPercent={progressPercent}
            onSubmit={handleSubmitSolvedOnly}
          />

          <div className="mx-auto grid w-full max-w-6xl grid-cols-[1fr_320px] gap-6 bg-slate-50 px-8 py-8">
            <div className="space-y-6">
              <QuestionCard
                question={currentQuestion}
                selectedChoice={answers[currentQuestion.id]}
                examType={examType}
                onSelectChoice={handleSelectChoice}
                isChecked={checkedQuestions[currentQuestion.id]}
                correctAnswer={currentQuestion.answer}
              />

              {checkedQuestions[currentQuestion.id] && (
                <div className="rounded-2xl border border-blue-100 bg-blue-50 p-5">
                  <h3 className="mb-2 text-sm font-extrabold text-blue-700">
                    정답 확인
                  </h3>

                  <p className="text-sm font-semibold text-slate-700">
                    정답: {currentQuestion.answer.join(", ")}번
                  </p>

                  {currentQuestion.explanation && (
                    <p className="mt-3 whitespace-pre-line text-sm leading-relaxed text-slate-700">
                      {currentQuestion.explanation}
                    </p>
                  )}
                </div>
              )}

              <div className="flex items-center justify-between gap-3">
                <button
                  onClick={handlePrev}
                  disabled={currentIndex === 0}
                  className="rounded-xl border border-slate-200 bg-white px-5 py-3 text-sm font-bold text-slate-600 hover:bg-slate-50 disabled:opacity-40"
                >
                  이전 문제
                </button>

                <button
                  onClick={handleSaveProgress}
                  className="rounded-xl border border-blue-200 bg-white px-6 py-3 text-sm font-bold text-blue-600 hover:bg-blue-50"
                >
                  나중에 학습
                </button>

                <button
                  onClick={handleCheckAnswer}
                  className="rounded-xl bg-blue-600 px-6 py-3 text-sm font-bold text-white hover:bg-blue-700"
                >
                  문제 정답 보기
                </button>

                <button
                  onClick={handleNext}
                  disabled={currentIndex === questions.length - 1}
                  className="rounded-xl border border-slate-200 bg-white px-5 py-3 text-sm font-bold text-slate-600 hover:bg-slate-50 disabled:opacity-40"
                >
                  다음 문제
                </button>
              </div>
              {saveMessage && (
                <div className="rounded-2xl border border-blue-100 bg-blue-50 px-5 py-4 text-center text-sm font-bold text-blue-700 shadow-sm">
                  {saveMessage}
                </div>
              )}
            </div>

            <div className="sticky top-[184px] self-start">
              <QuestionNavigator
                questions={questions}
                currentIndex={currentIndex}
                answers={answers}
                onMove={handleMoveQuestion}
              />
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}