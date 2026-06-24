"use client";

import { useEffect, useState } from "react";
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
  Loader2,
  Network,
  Search,
  ServerCog,
  ShieldCheck,
  TrafficCone,
  X,
} from "lucide-react";
import {
  getSingleStudyExams,
  SingleStudyExam,
  SingleStudyUnit,
} from "@/lib/singleStudyApi";

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

type SelectedUnit = SingleStudyUnit & {
  subjectName: string;
};

type StudyMode = "10" | "20" | "all";

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
  const [studyExams, setStudyExams] = useState<SingleStudyExam[]>([]);
  const [selectedUnit, setSelectedUnit] = useState<SelectedUnit | null>(null);
  const [studyMode, setStudyMode] = useState<StudyMode>("10");
  const [searchText, setSearchText] = useState("");
  const [openExamIds, setOpenExamIds] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    async function fetchStudyExams() {
      try {
        setIsLoading(true);
        setErrorMessage("");

        const data = await getSingleStudyExams();

        setStudyExams(data);

        if (data.length > 0) {
          setOpenExamIds([data[0].id]);
        }
      } catch (error) {
        console.error(error);
        setErrorMessage("한 문제씩 학습 데이터를 불러오지 못했어요.");
      } finally {
        setIsLoading(false);
      }
    }

    fetchStudyExams();
  }, []);

  const allUnits = studyExams.flatMap((exam) =>
    exam.subjects.flatMap((subject) =>
      subject.units.map((unit) => ({
        ...unit,
        examName: exam.name,
        subjectName: subject.name,
      }))
    )
  );

  const recommendedUnit = allUnits[0];

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

  const toggleExam = (examId: string) => {
    setOpenExamIds((prev) =>
      prev.includes(examId)
        ? prev.filter((id) => id !== examId)
        : [...prev, examId]
    );
  };

  const openStudyModal = (
    unit: SingleStudyUnit,
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

    const params = new URLSearchParams({
      exam_type: selectedUnit.examType,
      subject: selectedUnit.subject,
      unit: selectedUnit.name,
      mode: studyMode,
    });

    router.push(`/exam/single/solve?${params.toString()}`);
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

        {isLoading && (
          <div className="rounded-3xl border border-slate-200 bg-white p-12 text-center shadow-sm">
            <Loader2 className="mx-auto mb-4 animate-spin text-blue-600" size={36} />
            <p className="font-bold text-slate-700">
              실제 문제 데이터를 불러오는 중이에요.
            </p>
            <p className="mt-2 text-sm text-slate-500">
              등록된 시험, 과목, 연도별 문제를 확인하고 있어요.
            </p>
          </div>
        )}

        {!isLoading && errorMessage && (
          <div className="rounded-3xl border border-red-100 bg-white p-10 text-center shadow-sm">
            <p className="font-bold text-red-600">{errorMessage}</p>
            <p className="mt-2 text-sm text-slate-500">
              백엔드 서버가 켜져 있는지 확인해주세요.
            </p>
          </div>
        )}

        {!isLoading && !errorMessage && recommendedUnit && (
          <section className="mb-8 rounded-3xl border border-blue-200 bg-white p-6 shadow-sm">
            <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
              <div className="flex items-center gap-5">
                <div className="flex h-20 w-20 items-center justify-center rounded-3xl bg-blue-50 text-3xl">
                  🤖
                </div>

                <div>
                  <span className="rounded-full bg-blue-600 px-4 py-1 text-sm font-semibold text-white">
                    추천 학습
                  </span>
                  <h2 className="mt-3 text-xl font-bold">
                    바로 시작하기 좋은 단원이에요
                  </h2>
                  <p className="mt-1 text-sm text-slate-500">
                    실제 문제 데이터 기준으로 학습 가능한 단원을 보여줍니다.
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
                      기출문제 {recommendedUnit.questionCount}개
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

        {!isLoading && !errorMessage && (
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
                                        한 문제씩 랜덤 학습 가능
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
        )}
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