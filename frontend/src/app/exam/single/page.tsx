"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Header from "@/components/Header";
import Sidebar from "@/components/Sidebar";
import {
  BookOpen,
  ChevronDown,
  Code2,
  Database,
  Folder,
  Lightbulb,
  Network,
  Search,
  ServerCog,
  ShieldCheck,
  TrafficCone,
  X,
} from "lucide-react";

const colorMap = {
  blue: "bg-blue-50 text-blue-600",
  green: "bg-emerald-50 text-emerald-600",
  purple: "bg-purple-50 text-purple-600",
  orange: "bg-orange-50 text-orange-600",
  cyan: "bg-cyan-50 text-cyan-600",
  indigo: "bg-indigo-50 text-indigo-600",
  yellow: "bg-yellow-50 text-yellow-600",
};

const iconMap = {
  computer: Code2,
  os: ServerCog,
  database: Database,
  network: Network,
  data: Folder,
  code: Code2,
  software: BookOpen,
  term: Lightbulb,
  traffic: TrafficCone,
  safety: ShieldCheck,
};

type Unit = {
  id: number;
  name: string;
  questionCount: number;
  accuracy: number;
  wrongCount: number;
  icon: keyof typeof iconMap;
  color: keyof typeof colorMap;
};

type Subject = {
  id: number;
  name: string;
  years: string[];
  totalQuestionCount: number;
  units: Unit[];
};

type ExamGroup = {
  id: number;
  name: string;
  subjects: Subject[];
};

type SelectedUnit = Unit & {
  examName: string;
  subjectName: string;
};

type StudyMode = "10" | "20" | "all";

const studyExams: ExamGroup[] = [
  {
    id: 1,
    name: "국가직 9급",
    subjects: [
      {
        id: 101,
        name: "컴퓨터일반",
        years: ["2024", "2023"],
        totalQuestionCount: 40,
        units: [
          {
            id: 1,
            name: "컴퓨터구조",
            questionCount: 24,
            accuracy: 72,
            wrongCount: 18,
            icon: "computer",
            color: "blue",
          },
          {
            id: 2,
            name: "운영체제",
            questionCount: 20,
            accuracy: 58,
            wrongCount: 32,
            icon: "os",
            color: "green",
          },
          {
            id: 3,
            name: "데이터베이스",
            questionCount: 18,
            accuracy: 84,
            wrongCount: 9,
            icon: "database",
            color: "purple",
          },
          {
            id: 4,
            name: "네트워크",
            questionCount: 18,
            accuracy: 63,
            wrongCount: 27,
            icon: "network",
            color: "orange",
          },
        ],
      },
    ],
  },
  {
    id: 2,
    name: "지방직 9급",
    subjects: [
      {
        id: 201,
        name: "컴퓨터일반",
        years: ["2023", "2022"],
        totalQuestionCount: 40,
        units: [
          {
            id: 5,
            name: "자료구조",
            questionCount: 16,
            accuracy: 70,
            wrongCount: 16,
            icon: "data",
            color: "cyan",
          },
          {
            id: 6,
            name: "프로그래밍 언어론",
            questionCount: 14,
            accuracy: 68,
            wrongCount: 14,
            icon: "code",
            color: "indigo",
          },
          {
            id: 7,
            name: "소프트웨어 공학",
            questionCount: 14,
            accuracy: 66,
            wrongCount: 12,
            icon: "software",
            color: "blue",
          },
          {
            id: 8,
            name: "최신기술용어",
            questionCount: 12,
            accuracy: 71,
            wrongCount: 8,
            icon: "term",
            color: "yellow",
          },
        ],
      },
    ],
  },
  {
    id: 3,
    name: "한국도로교통공단",
    subjects: [
      {
        id: 301,
        name: "운전면허 필기",
        years: ["2024", "2023"],
        totalQuestionCount: 80,
        units: [
          {
            id: 9,
            name: "도로교통법",
            questionCount: 30,
            accuracy: 69,
            wrongCount: 21,
            icon: "traffic",
            color: "yellow",
          },
          {
            id: 10,
            name: "안전운전",
            questionCount: 28,
            accuracy: 74,
            wrongCount: 15,
            icon: "safety",
            color: "green",
          },
          {
            id: 11,
            name: "표지판",
            questionCount: 22,
            accuracy: 81,
            wrongCount: 10,
            icon: "term",
            color: "orange",
          },
        ],
      },
    ],
  },
];

const studyModes: {
  value: StudyMode;
  title: string;
  desc: string;
}[] = [
  {
    value: "10",
    title: "랜덤 10문제",
    desc: "가볍게 학습하기 좋아요.",
  },
  {
    value: "20",
    title: "랜덤 20문제",
    desc: "좀 더 다양한 문제로 학습할 수 있어요.",
  },
  {
    value: "all",
    title: "전체 랜덤",
    desc: "모든 문제 중에서 랜덤으로 계속 출제돼요.",
  },
];

export default function OneQuestionPage() {
  const router = useRouter();

  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [selectedUnit, setSelectedUnit] = useState<SelectedUnit | null>(null);
  const [studyMode, setStudyMode] = useState<StudyMode>("10");
  const [searchText, setSearchText] = useState("");
  const [openExamIds, setOpenExamIds] = useState<number[]>([1]);

  const allUnits = studyExams.flatMap((exam) =>
    exam.subjects.flatMap((subject) =>
      subject.units.map((unit) => ({
        ...unit,
        examName: exam.name,
        subjectName: subject.name,
      }))
    )
  );

  const recommendedUnit = [...allUnits].sort(
    (a, b) => b.wrongCount - a.wrongCount
  )[0];

  const filteredExams = studyExams
    .map((exam) => ({
      ...exam,
      subjects: exam.subjects
        .map((subject) => {
          const keyword = searchText.trim().toLowerCase();

          if (!keyword) return subject;

          return {
            ...subject,
            units: subject.units.filter(
              (unit) =>
                exam.name.toLowerCase().includes(keyword) ||
                subject.name.toLowerCase().includes(keyword) ||
                subject.years.some((year) => year.includes(keyword)) ||
                unit.name.toLowerCase().includes(keyword)
            ),
          };
        })
        .filter((subject) => subject.units.length > 0),
    }))
    .filter((exam) => exam.subjects.length > 0);

  const toggleExam = (examId: number) => {
    setOpenExamIds((prev) =>
      prev.includes(examId)
        ? prev.filter((id) => id !== examId)
        : [...prev, examId]
    );
  };

  const openStudyModal = (
    unit: Unit,
    examName: string,
    subjectName: string
  ) => {
    setSelectedUnit({
      ...unit,
      examName,
      subjectName,
    });
    setStudyMode("10");
  };

  const handleStartStudy = () => {
    if (!selectedUnit) return;

    // 나중에 문제풀이 페이지 생기면 이것만 수정
    // router.push(`/exam/one/${selectedUnit.id}?mode=${studyMode}`);
    console.log("학습 시작:", selectedUnit, studyMode);
  };

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

      <section className="mx-auto w-full max-w-7xl px-6 pb-12 pt-28">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <p className="mb-3 text-sm font-medium text-slate-500">
              기출문제 <span className="mx-2">›</span>
              <span className="text-slate-900">한 문제씩 학습</span>
            </p>

            <h1 className="text-3xl font-bold">한 문제씩 학습</h1>
            <p className="mt-2 text-slate-500">
              시험과 과목을 선택하고 단원별로 랜덤 문제를 풀어보세요.
            </p>
          </div>

          <button
            onClick={() => router.push("/mypage")}
            className="rounded-xl border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-700 shadow-sm transition hover:border-blue-300 hover:text-blue-600"
          >
            학습 기록
          </button>
        </div>

        <div className="mb-6 flex items-center gap-3 rounded-2xl border border-slate-200 bg-white px-5 py-4 shadow-sm">
          <Search size={20} className="text-slate-400" />
          <input
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            placeholder="시험명, 과목명, 연도, 단원명을 검색해보세요."
            className="w-full bg-transparent text-sm outline-none placeholder:text-slate-400"
          />
        </div>

        {recommendedUnit && (
          <section className="mb-8 rounded-3xl border border-blue-200 bg-white p-6 shadow-sm">
            <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
              <div className="flex items-center gap-5">
                <div className="flex h-20 w-20 items-center justify-center rounded-3xl bg-blue-50 text-3xl">
                  🤖
                </div>

                <div>
                  <span className="rounded-full bg-blue-600 px-4 py-1 text-sm font-semibold text-white">
                    AI 추천 학습
                  </span>
                  <h2 className="mt-3 text-xl font-bold">
                    오답이 가장 많은 단원이에요
                  </h2>
                  <p className="mt-1 text-sm text-slate-500">
                    최근 오답 기록을 기준으로 1개 단원을 추천합니다.
                  </p>
                </div>
              </div>

              <div className="flex w-full items-center justify-between rounded-2xl border border-slate-100 bg-slate-50 p-4 lg:max-w-md">
                <div className="flex items-center gap-4">
                  {(() => {
                    const Icon = iconMap[recommendedUnit.icon];

                    return (
                      <div
                        className={`flex h-14 w-14 items-center justify-center rounded-2xl ${colorMap[recommendedUnit.color]}`}
                      >
                        <Icon size={26} />
                      </div>
                    );
                  })()}

                  <div>
                    <p className="font-bold">{recommendedUnit.name}</p>
                    <p className="text-sm text-slate-500">
                      {recommendedUnit.examName} · {recommendedUnit.subjectName}
                    </p>
                    <p className="text-sm text-slate-500">
                      오답 {recommendedUnit.wrongCount}개 · 정답률{" "}
                      <span className="font-bold text-blue-600">
                        {recommendedUnit.accuracy}%
                      </span>
                    </p>
                  </div>
                </div>

                <button
                  onClick={() =>
                    openStudyModal(
                      recommendedUnit,
                      recommendedUnit.examName,
                      recommendedUnit.subjectName
                    )
                  }
                  className="rounded-xl bg-blue-600 px-5 py-3 text-sm font-bold text-white shadow-sm transition hover:bg-blue-700 active:scale-95"
                >
                  학습하기
                </button>
              </div>
            </div>
          </section>
        )}

        <section className="space-y-5">
          {filteredExams.map((exam) => {
            const isOpen = openExamIds.includes(exam.id);
            const subjectCount = exam.subjects.length;
            const unitCount = exam.subjects.reduce(
              (sum, subject) => sum + subject.units.length,
              0
            );

            return (
              <div
                key={exam.id}
                className="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm"
              >
                <button
                  onClick={() => toggleExam(exam.id)}
                  className="flex w-full items-center justify-between px-6 py-5 text-left transition hover:bg-slate-50"
                >
                  <div>
                    <h2 className="text-xl font-bold">{exam.name}</h2>
                    <p className="mt-1 text-sm text-slate-500">
                      {subjectCount}개 과목 · {unitCount}개 단원
                    </p>
                  </div>

                  <ChevronDown
                    size={24}
                    className={`text-slate-400 transition duration-300 ${
                      isOpen ? "rotate-180" : ""
                    }`}
                  />
                </button>

                {isOpen && (
                  <div className="border-t border-slate-100 px-6 py-6">
                    {exam.subjects.map((subject) => (
                      <div key={subject.id} className="mb-8 last:mb-0">
                        <div className="mb-4">
                          <h3 className="text-lg font-bold">
                            {subject.name}
                          </h3>
                          <p className="mt-1 text-sm text-slate-500">
                            {subject.years.join(", ")}년 기출 · 총{" "}
                            {subject.totalQuestionCount}문제
                          </p>
                        </div>

                        <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
                          {subject.units.map((unit) => {
                            const Icon = iconMap[unit.icon];

                            return (
                              <button
                                key={unit.id}
                                onClick={() =>
                                  openStudyModal(
                                    unit,
                                    exam.name,
                                    subject.name
                                  )
                                }
                                className="group flex items-center justify-between rounded-3xl border border-slate-200 bg-white p-6 text-left shadow-sm transition duration-300 hover:-translate-y-1 hover:border-blue-300 hover:shadow-md"
                              >
                                <div className="flex items-center gap-6">
                                  <div
                                    className={`flex h-20 w-20 items-center justify-center rounded-2xl transition duration-300 group-hover:scale-105 ${colorMap[unit.color]}`}
                                  >
                                    <Icon size={34} />
                                  </div>

                                  <div>
                                    <h4 className="text-xl font-bold">
                                      {unit.name}
                                    </h4>
                                    <p className="mt-2 text-sm text-slate-500">
                                      기출문제 {unit.questionCount}개
                                    </p>
                                    <p className="mt-1 text-sm text-slate-500">
                                      오답 {unit.wrongCount}개 · 최근 정답률{" "}
                                      <span className="font-bold text-blue-600">
                                        {unit.accuracy}%
                                      </span>
                                    </p>
                                  </div>
                                </div>

                                <span className="rounded-xl border border-blue-200 px-5 py-3 text-sm font-bold text-blue-600 transition group-hover:bg-blue-600 group-hover:text-white">
                                  학습하기
                                </span>
                              </button>
                            );
                          })}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })}

          {filteredExams.length === 0 && (
            <div className="rounded-3xl border border-slate-200 bg-white p-10 text-center shadow-sm">
              <p className="font-bold text-slate-700">검색 결과가 없어요.</p>
              <p className="mt-2 text-sm text-slate-500">
                다른 시험명, 과목명, 연도, 단원명으로 검색해보세요.
              </p>
            </div>
          )}
        </section>
      </section>

      {selectedUnit && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/30 px-4">
          <div className="w-full max-w-md animate-[modalUp_0.25s_ease-out] rounded-3xl bg-white p-7 shadow-2xl">
            <div className="mb-6 flex items-start justify-between">
              <div className="flex items-center gap-4">
                <div
                  className={`flex h-16 w-16 items-center justify-center rounded-2xl ${colorMap[selectedUnit.color]}`}
                >
                  {(() => {
                    const Icon = iconMap[selectedUnit.icon];
                    return <Icon size={30} />;
                  })()}
                </div>

                <div>
                  <h2 className="text-xl font-bold">{selectedUnit.name}</h2>
                  <p className="mt-1 text-sm text-slate-500">
                    {selectedUnit.examName} · {selectedUnit.subjectName}
                  </p>
                  <p className="mt-1 text-sm text-slate-500">
                    총 문제 수 {selectedUnit.questionCount}개
                  </p>
                </div>
              </div>

              <button
                onClick={() => setSelectedUnit(null)}
                className="rounded-full p-2 text-slate-400 transition hover:bg-slate-100 hover:text-slate-700"
              >
                <X size={22} />
              </button>
            </div>

            <h3 className="mb-4 font-bold">어떻게 학습할까요?</h3>

            <div className="space-y-3">
              {studyModes.map((mode) => (
                <button
                  key={mode.value}
                  onClick={() => setStudyMode(mode.value)}
                  className="flex w-full items-start gap-4 rounded-2xl p-3 text-left transition hover:bg-slate-50"
                >
                  <span
                    className={`mt-1 flex h-5 w-5 items-center justify-center rounded-full border ${
                      studyMode === mode.value
                        ? "border-blue-600"
                        : "border-slate-300"
                    }`}
                  >
                    {studyMode === mode.value && (
                      <span className="h-2.5 w-2.5 rounded-full bg-blue-600" />
                    )}
                  </span>

                  <span>
                    <span className="block font-bold">{mode.title}</span>
                    <span className="mt-1 block text-sm text-slate-500">
                      {mode.desc}
                    </span>
                  </span>
                </button>
              ))}
            </div>

            <button
              onClick={handleStartStudy}
              className="mt-7 w-full rounded-xl bg-blue-600 py-4 font-bold text-white shadow-sm transition hover:bg-blue-700 active:scale-[0.98]"
            >
              시작하기
            </button>
          </div>
        </div>
      )}

      <style jsx>{`
        @keyframes modalUp {
          from {
            opacity: 0;
            transform: translateY(16px) scale(0.98);
          }
          to {
            opacity: 1;
            transform: translateY(0) scale(1);
          }
        }
      `}</style>
    </main>
  );
}