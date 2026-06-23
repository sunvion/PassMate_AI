// 실제 시험
"use client";

import { useEffect, useState, useRef } from "react";
import { useParams, useRouter, useSearchParams } from "next/navigation";

import Header from "@/components/Header";
import Sidebar from "@/components/Sidebar";
import SolveHeader from "@/components/exams/SolveHeader";
import QuestionCard from "@/components/exams/QuestionCard";
import QuestionNavigator from "@/components/exams/QuestionNavigator";

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

  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<SelectedAnswers>({});
  const questionRefs = useRef<(HTMLDivElement | null)[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");

  const answeredCount = Object.keys(answers).length;
  const progressPercent =
    questions.length > 0
      ? Math.round((answeredCount / questions.length) * 100)
      : 0;


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

        const formattedQuestions = data.questions
          .map((q: any) => ({
            id: q.id,
            number: q.number,
            text: q.question,
            imageUrl: q.image_url,
            explanation: q.explanation,
            answer: q.answer,
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

  const handleSubmit = async () => {
    if (Object.keys(answers).length < questions.length) {
      const ok = window.confirm(
        "아직 풀지 않은 문제가 있습니다. 그래도 제출할까요?"
      );

      if (!ok) return;
    }

    try {
      const result = await submitBulkAnswers(examId, answers);
      console.log("제출 결과:", result);

      alert("제출이 완료되었습니다.");

      router.push("/exam/full");
    } catch (error) {
      console.error(error);
      alert("제출 중 오류가 발생했습니다.");
    }
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
            title={title}
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
    </main>
  );
}