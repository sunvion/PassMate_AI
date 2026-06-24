"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Header from "@/components/Header";
import Sidebar from "@/components/Sidebar";

type ExamMeta = {
  exam_type: string;
  year: number;
  subject: string;
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

const getExamTypeLabel = (examType: string) => {
  switch (examType) {
    case "CS_GENERAL":
      return "국가직";

    case "CS_LOCAL":
      return "지방직";

    case "DRIVERS_LICENSE_1":
    case "DRIVERS_LICENSE_2":
      return "필기시험";

    default:
      return examType;
  }
};

const getSubjectLabel = (subject: string) => {
  switch (subject) {
    case "운전면허 학과":
      return "운전면허 필기";

    default:
      return subject;
  }
};

export default function FullExamPage() {
  const router = useRouter();

  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [selectedYear, setSelectedYear] = useState("전체");
  const [selectedSubject, setSelectedSubject] = useState("전체");

  const [exams, setExams] = useState<ExamMeta[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    const fetchExams = async () => {
      try {
        setIsLoading(true);
        setErrorMessage("");

        const res = await fetch(`${API_BASE_URL}/api/v1/exams`, {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
          cache: "no-store",
        });

        if (!res.ok) {
          throw new Error("시험 목록 조회 실패");
        }

        const data: ExamMeta[] = await res.json();
        setExams(data);
      } catch (error) {
        console.error(error);
        setErrorMessage("시험 목록을 불러오지 못했습니다.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchExams();
  }, []);

  const yearOptions = [
    "전체",
    ...Array.from(new Set(exams.map((exam) => String(exam.year)))).sort(
      (a, b) => Number(b) - Number(a)
    ),
  ];

  const subjectOptions = [
    "전체",
    ...Array.from(new Set(exams.map((exam) => getSubjectLabel(exam.subject)))),
  ];

  const filteredExams = exams.filter((exam) => {
    const isDriverLicense = exam.exam_type.startsWith("DRIVERS_LICENSE");

    const yearMatched =
      isDriverLicense ||
      selectedYear === "전체" ||
      String(exam.year) === selectedYear;

    const subjectMatched =
      selectedSubject === "전체" ||
      getSubjectLabel(exam.subject) === selectedSubject;

    return yearMatched && subjectMatched;
  });

  const handleStartExam = (exam: ExamMeta) => {
    const examKey = `${exam.year}-${exam.exam_type}-${exam.subject}`;

    router.push(
      `/exam/solve/${encodeURIComponent(
        examKey
      )}?exam_type=${encodeURIComponent(
        exam.exam_type
      )}&subject=${encodeURIComponent(exam.subject)}&year=${exam.year}`
    );
  };

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <Header
        onMenuClick={() => setIsMenuOpen(true)}
        onLoginClick={() => { }}
      />

      <Sidebar isOpen={isMenuOpen} onClose={() => setIsMenuOpen(false)} />

      <section className="mx-auto w-full max-w-6xl px-6 pb-12 pt-28">
        <div className="mb-8">
          <p className="mb-3 text-sm font-medium text-slate-500">
            기출문제 <span className="mx-2">›</span>
            <span className="text-slate-900">전체 회차 풀기</span>
          </p>

          <h1 className="text-3xl font-bold">전체 회차 풀기</h1>
          <p className="mt-2 text-slate-500">
            과거 기출문제를 실제 시험처럼 풀어보세요.
          </p>
        </div>

        <div className="space-y-6">
          <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="text-xl font-bold">검색 조건</h2>

            <div className="mt-6 grid gap-4 md:grid-cols-3">
              <div>
                <label className="mb-2 block text-sm font-semibold text-slate-700">
                  과목
                </label>
                <select
                  value={selectedSubject}
                  onChange={(e) => setSelectedSubject(e.target.value)}
                  className="h-12 w-full rounded-xl border border-slate-200 bg-white px-4 text-slate-900 outline-none focus:border-blue-500"
                >
                  {subjectOptions.map((subject) => (
                    <option key={subject}>{subject}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="mb-2 block text-sm font-semibold text-slate-700">
                  연도
                </label>
                <select
                  value={selectedYear}
                  onChange={(e) => setSelectedYear(e.target.value)}
                  className="h-12 w-full rounded-xl border border-slate-200 bg-white px-4 text-slate-900 outline-none focus:border-blue-500"
                >
                  {yearOptions.map((year) => (
                    <option key={year}>{year}</option>
                  ))}
                </select>
              </div>

              <div className="flex items-end">
                <button
                  type="button"
                  className="h-12 w-full rounded-xl bg-blue-600 font-bold text-white shadow-md transition hover:bg-blue-700"
                >
                  검색
                </button>
              </div>
            </div>

            <p className="mt-3 text-sm text-slate-400">
              해당 조건 중 하나 이상 설정해 주세요.
            </p>
          </section>

          <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-bold">전체 회차 목록</h2>
              <span className="text-sm text-slate-500">
                총 {filteredExams.length}개 회차
              </span>
            </div>

            <div className="mt-6 grid gap-4">
              {isLoading ? (
                <div className="rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-10 text-center">
                  <p className="font-bold text-slate-700">
                    시험 목록을 불러오는 중입니다...
                  </p>
                </div>
              ) : errorMessage ? (
                <div className="rounded-2xl border border-dashed border-red-300 bg-red-50 p-10 text-center">
                  <p className="font-bold text-red-600">{errorMessage}</p>
                </div>
              ) : filteredExams.length > 0 ? (
                filteredExams.map((exam) => (
                  <div
                    key={`${exam.year}-${exam.exam_type}-${exam.subject}`}
                    className="flex flex-col gap-5 rounded-2xl border border-slate-200 bg-white p-5 transition hover:border-blue-200 hover:bg-blue-50/40 hover:shadow-sm md:flex-row md:items-center md:justify-between"
                  >
                    <div>
                      <div className="flex items-center gap-3">
                        <h3 className="text-lg font-extrabold text-slate-900">
                          {getSubjectLabel(exam.subject)}
                        </h3>

                        <span className="rounded-full bg-blue-50 px-3 py-1 text-sm font-bold text-blue-600">
                          {exam.exam_type.startsWith("DRIVERS_LICENSE") ? "상시" : `${exam.year}년`}
                        </span>

                        <span className="rounded-full bg-slate-100 px-3 py-1 text-sm font-bold text-slate-600">
                          {getExamTypeLabel(exam.exam_type)}
                        </span>
                      </div>

                      <p className="mt-2 text-sm text-slate-500">
                        전체 회차 풀이
                      </p>
                    </div>

                    <button
                      type="button"
                      onClick={() => handleStartExam(exam)}
                      className="h-12 rounded-xl bg-blue-600 px-7 font-bold text-white shadow-md transition hover:bg-blue-700 md:w-auto"
                    >
                      응시하기
                    </button>
                  </div>
                ))
              ) : (
                <div className="rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-10 text-center">
                  <p className="font-bold text-slate-700">
                    검색 결과가 없습니다.
                  </p>
                  <p className="mt-2 text-sm text-slate-500">
                    다른 조건으로 다시 검색해보세요.
                  </p>
                </div>
              )}
            </div>
          </section>
        </div>
      </section>
    </main>
  );
}