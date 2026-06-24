// 실제 시험
"use client";

import { useEffect, useRef, useState } from "react";
import { useParams, useRouter, useSearchParams } from "next/navigation";

import Header from "@/components/Header";
import Sidebar from "@/components/Sidebar";
import SolveHeader from "@/components/exams/SolveHeader";
import QuestionCard from "@/components/exams/QuestionCard";
import QuestionNavigator from "@/components/exams/QuestionNavigator";
import SubmitConfirmModal from "@/components/exams/SubmitConfirmModal";

import { getExamQuestions, submitBulkAnswers } from "@/lib/examApi";
import { Question, SelectedAnswers } from "@/types/exam";

export default function ExamSolvePage() {
  const router = useRouter();
  const params = useParams();
  const searchParams = useSearchParams();

  const examId = params.examId as string;

  const examType = searchParams.get("exam_type") || "";
  const subject = searchParams.get("subject") || "";
  const year = searchParams.get("year") || "";

  const getExamTypeLabel = (examType: string) => {
    switch (examType) {
      case "CS_GENERAL":
        return "국가직";

      case "CS_LOCAL":
        return "지방직";

      case "DRIVERS_LICENSE_1":
        return "운전면허 1종";

      case "DRIVERS_LICENSE_2":
        return "운전면허 2종";

      default:
        return examType;
    }
  };

  const displayTitle = `${year} ${subject} ${getExamTypeLabel(examType)}`;

  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<SelectedAnswers>({});
  const questionRefs = useRef<(HTMLDivElement | null)[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");
  const [isSubmitModalOpen, setIsSubmitModalOpen] = useState(false);

  const answeredCount = Object.keys(answers).length;
  const progressPercent =
    questions.length > 0
      ? Math.round((answeredCount / questions.length) * 100)
      : 0;

  const unansweredNumbers = questions
    .filter((question) => answers[question.id] === undefined)
    .map((question) => question.number);

  useEffect(() => {
    const fetchQuestions = async () => {
      try {
        setIsLoading(true);
        setErrorMessage("");

        const data = await getExamQuestions({
          examType,
          subject,
          year,
        });

        console.log("첫 번째 문제:", data.questions[0]);

        const formattedQuestions = data.questions
          .map((q: any) => ({
            id: q.id,
            number: q.number,
            text: q.text ?? q.question ?? "",
            imageUrl: q.imageUrl ?? q.image_url ?? null,
            explanation: q.explanation ?? null,
            answer: Array.isArray(q.answer) ? q.answer.map(Number) : [Number(q.answer)],
            choices: Object.entries(q.options ?? {}).map(([number, text]) => ({
              id: Number(number),
              number: Number(number),
              text: String(text),
              imageUrl: null,
            })),
          }))
          .sort((a: Question, b: Question) => a.number - b.number);

        setTitle(data.title);
        setQuestions(formattedQuestions);
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
  }, [examType, subject, year]);

  const handleSelectChoice = (questionId: number, choiceNumber: number) => {
    setAnswers((prev: SelectedAnswers) => ({
      ...prev,
      [questionId]: choiceNumber,
    }));
  };

  useEffect(() => {
    const handleScroll = () => {
      let nextIndex = currentIndex;

      questionRefs.current.forEach((el, index) => {
        if (!el) return;

        const rect = el.getBoundingClientRect();

        if (rect.top <= 160 && rect.bottom >= 184) {
          nextIndex = index;
        }
      });

      if (nextIndex !== currentIndex) {
        setCurrentIndex(nextIndex);
      }
    };

    window.addEventListener("scroll", handleScroll);

    return () => {
      window.removeEventListener("scroll", handleScroll);
    };
  }, [currentIndex]);

  const handleMoveQuestion = (index: number) => {
    setCurrentIndex(index);

    const el = document.getElementById(`question-${index}`);

    if (el) {
      const y = el.getBoundingClientRect().top + window.scrollY - 184;

      window.scrollTo({
        top: y,
        behavior: "smooth",
      });
    }
  };

  const submitExam = async () => {
    try {
      const result = await submitBulkAnswers(examId, answers, questions);

      console.log("제출 결과:", result);

      const totalCount = questions.length;

      const resultList = result.results ?? [];

      const correctCount = resultList.filter(
        (item: { is_correct: boolean }) => item.is_correct
      ).length;

      const wrongCount = totalCount - correctCount;

      const score =
        totalCount > 0 ? Math.round((correctCount / totalCount) * 100) : 0;

      const query = new URLSearchParams({
        exam_type: examType,
        subject,
        year,
        total: String(totalCount),
        correct: String(correctCount),
        wrong: String(wrongCount),
        score: String(score),
      });

      router.push(`/exam/full/result?${query.toString()}`);
    } catch (error) {
      console.error(error);
      alert("제출 중 오류가 발생했습니다.");
    }
  };

  const handleSubmit = async () => {
    if (Object.keys(answers).length < questions.length) {
      setIsSubmitModalOpen(true);
      return;
    }

    await submitExam();
  };

  if (isLoading) {
    return (
      <main className="min-h-screen bg-slate-50 text-slate-900">
        <Header
          onMenuClick={() => setIsMenuOpen(true)}
          onLoginClick={() => { }}
        />
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
        <Header
          onMenuClick={() => setIsMenuOpen(true)}
          onLoginClick={() => { }}
        />
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
            onSubmit={handleSubmit}
          />

          <div className="mx-auto grid w-full max-w-6xl grid-cols-[1fr_320px] gap-6 bg-slate-50 px-8 py-8">
            <div className="space-y-8">
              {questions.map((question, index) => (
                <div
                  key={question.id}
                  id={`question-${index}`}
                  ref={(el) => {
                    questionRefs.current[index] = el;
                  }}
                >
                  <QuestionCard
                    question={question}
                    selectedChoice={answers[question.id]}
                    examType={examType}
                    onSelectChoice={handleSelectChoice}
                  />
                </div>
              ))}
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

      {isSubmitModalOpen && (
        <SubmitConfirmModal
          totalCount={questions.length}
          answeredCount={answeredCount}
          unansweredNumbers={unansweredNumbers}
          onClose={() => setIsSubmitModalOpen(false)}
          onSubmitAnyway={() => {
            setIsSubmitModalOpen(false);
            submitExam();
          }}
          onMoveQuestion={(index) => {
            setIsSubmitModalOpen(false);
            handleMoveQuestion(index);
          }}
        />
      )}
    </main>
  );
}