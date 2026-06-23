"use client";

import { useState } from "react";
import { useSearchParams } from "next/navigation";

import Header from "@/components/Header";
import Sidebar from "@/components/Sidebar";
import ResultHero from "@/components/exams/result/ResultHero";
import ScoreSummaryCard from "@/components/exams/result/ScoreSummaryCard";
import WrongNoteBanner from "@/components/exams/result/WrongNoteBanner";
import type { ExamResult } from "@/types/examResult";

const mockResult: ExamResult = {
  examTitle: "2025년 1회차 기출문제",
  examType: "공무원 전산직 기출문제",
  round: "2025년 1회차",
  totalCount: 20,
  correctCount: 16,
  wrongCount: 4,
  score: 80,
  accuracy: 80,
  submittedAt: "2025. 05. 20 (화) 15:30",
  elapsedTime: "40분 15초",
  averageTime: "2분 00초 / 문제",
  subjectStats: [
    { subject: "운영체제", total: 10, correct: 9, accuracy: 90 },
    { subject: "데이터베이스", total: 5, correct: 2, accuracy: 40 },
    { subject: "자료 구조", total: 5, correct: 4, accuracy: 80 },
    { subject: "컴퓨터구조", total: 4, correct: 3, accuracy: 75 },
    { subject: "프로그래밍 언어론", total: 5, correct: 3, accuracy: 60 },
    { subject: "데이터 통신과 네트워크", total: 10, correct: 7, accuracy: 70 },
  ],
};

function formatExamType(type: string) {
  switch (type) {
    case "CS_GENERAL":
      return "컴퓨터일반";
    case "DRIVERS_LICENSE_1":
      return "운전면허 1종";
    case "DRIVERS_LICENSE_2":
      return "운전면허 2종";
    default:
      return type;
  }
}

export default function ExamResultPage() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const searchParams = useSearchParams();

  const examType = searchParams.get("exam_type") || "";
  const subject = searchParams.get("subject") || "";
  const year = searchParams.get("year") || "";

  const total = Number(searchParams.get("total") || 0);
  const correct = Number(searchParams.get("correct") || 0);
  const wrong = Number(searchParams.get("wrong") || 0);
  const score = Number(searchParams.get("score") || 0);

  const displaySubject = subject || formatExamType(examType) || "시험";
  const displayYear = year || "연도 미상";

  const result: ExamResult = {
    ...mockResult,
    examTitle: `${displayYear}년 ${displaySubject} 기출문제`,
    examType: formatExamType(examType),
    round: `${displayYear}년`,
    totalCount: total,
    correctCount: correct,
    wrongCount: wrong,
    score,
    accuracy: score,
  };

  return (
    <main className="min-h-screen bg-slate-50">
      <Header onMenuClick={() => setIsMenuOpen(true)} onLoginClick={() => {}} />
      <Sidebar isOpen={isMenuOpen} onClose={() => setIsMenuOpen(false)} />

      <div className="mx-auto max-w-6xl px-8 py-12">
        <ResultHero
          examTitle={result.examTitle}
          wrongCount={result.wrongCount}
        />

        <div className="mx-auto mt-10 max-w-md">
          <ScoreSummaryCard
            score={result.score}
            totalCount={result.totalCount}
            correctCount={result.correctCount}
            wrongCount={result.wrongCount}
            accuracy={result.accuracy}
          />
        </div>

        <div className="mt-6">
          <WrongNoteBanner wrongCount={result.wrongCount} />
        </div>
      </div>
    </main>
  );
}