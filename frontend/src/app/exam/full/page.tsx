"use client";

import { useState } from "react";
import Header from "@/components/Header";
import Sidebar from "@/components/Sidebar";

const exams = [
  {
    id: 1,
    year: "2024",
    agency: "국가직 9급",
    subject: "컴퓨터일반",
    questionCount: 20,
  },
  {
    id: 2,
    year: "2023",
    agency: "지방직 9급",
    subject: "컴퓨터일반",
    questionCount: 20,
  },
  {
    id: 3,
    year: "2023",
    agency: "국가직 9급",
    subject: "컴퓨터일반",
    questionCount: 20,
  },
  {
    id: 4,
    year: "2022",
    agency: "지방직 9급",
    subject: "컴퓨터일반",
    questionCount: 20,
  },
  {
    id: 5,
    year: "2024",
    agency: "한국도로교통공단",
    subject: "운전면허 필기",
    questionCount: 40,
  },
  {
    id: 6,
    year: "2023",
    agency: "한국도로교통공단",
    subject: "운전면허 필기",
    questionCount: 40,
  }
];

export default function FullExamPage() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [selectedYear, setSelectedYear] = useState("전체");
  const [selectedAgency, setSelectedAgency] = useState("전체");
  const [selectedSubject, setSelectedSubject] = useState("전체");

  const filteredExams = exams.filter((exam) => {
    const yearMatched =
      selectedYear === "전체" || exam.year === selectedYear;

    const agencyMatched =
      selectedAgency === "전체" || exam.agency === selectedAgency;

    const subjectMatched =
      selectedSubject === "전체" || exam.subject === selectedSubject;

    return yearMatched && agencyMatched && subjectMatched;
  });

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <Header
        onMenuClick={() => setIsMenuOpen(true)}
        onLoginClick={() => {}}
      />

      <Sidebar
        isOpen={isMenuOpen}
        onClose={() => setIsMenuOpen(false)}
      />

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

            <div className="mt-6 grid gap-4 md:grid-cols-4">
              <div>
                <label className="mb-2 block text-sm font-semibold text-slate-700">
                  연도
                </label>
                <select
                  value={selectedYear}
                  onChange={(e) => setSelectedYear(e.target.value)}
                  className="h-12 w-full rounded-xl border border-slate-200 bg-white px-4 text-slate-900 outline-none focus:border-blue-500"
                >
                  <option>전체</option>
                  <option>2024</option>
                  <option>2023</option>
                  <option>2022</option>
                </select>
              </div>

              <div>
                <label className="mb-2 block text-sm font-semibold text-slate-700">
                  시행처
                </label>
                <select
                  value={selectedAgency}
                  onChange={(e) => setSelectedAgency(e.target.value)}
                  className="h-12 w-full rounded-xl border border-slate-200 bg-white px-4 text-slate-900 outline-none focus:border-blue-500"
                >
                  <option>전체</option>
                  <option>국가직 9급</option>
                  <option>지방직 9급</option>
                  <option>한국도로교통공단</option>
                </select>
              </div>

              <div>
                <label className="mb-2 block text-sm font-semibold text-slate-700">
                  과목
                </label>
                <select
                  value={selectedSubject}
                  onChange={(e) => setSelectedSubject(e.target.value)}
                  className="h-12 w-full rounded-xl border border-slate-200 bg-white px-4 text-slate-900 outline-none focus:border-blue-500"
                >
                  <option>전체</option>
                  <option>컴퓨터일반</option>
                  <option>운전면허 필기</option>
                </select>
              </div>

              <div className="flex items-end">
                <button className="h-12 w-full rounded-xl bg-blue-600 font-bold text-white shadow-md transition hover:bg-blue-700">
                  검색
                </button>
              </div>
            </div>
          </section>

          <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-bold">전체 회차 목록</h2>
              <span className="text-sm text-slate-500">
                총 {filteredExams.length}개 회차
              </span>
            </div>

            <div className="mt-6 grid gap-4">
              {filteredExams.length > 0 ? (
                filteredExams.map((exam) => (
                  <div
                    key={exam.id}
                    className="flex flex-col gap-5 rounded-2xl border border-slate-200 bg-white p-5 transition hover:border-blue-200 hover:bg-blue-50/40 hover:shadow-sm md:flex-row md:items-center md:justify-between"
                  >
                    <div>
                      <h3 className="text-lg font-extrabold">
                        {exam.year} {exam.agency}
                      </h3>

                      <p className="mt-2 font-semibold text-slate-700">
                        {exam.subject}
                      </p>

                      <p className="mt-1 text-sm text-slate-500">
                        총 {exam.questionCount}문항
                      </p>
                    </div>

                    <button className="h-12 rounded-xl bg-blue-600 px-7 font-bold text-white shadow-md transition hover:bg-blue-700 md:w-auto">
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