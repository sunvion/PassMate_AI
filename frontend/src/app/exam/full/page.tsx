"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { ChevronDown } from "lucide-react";

import Header from "@/components/Header";
import Sidebar from "@/components/Sidebar";

type ExamMeta = {
  exam: string; // 큰 시험 분류
  exam_type: string; // 시험구분 내부 코드
  year: number; // 시험 연도
  subject: string; // 실제 과목
  round?: string; // 회차가 있는 시험용
  is_mock?: boolean; // mock 데이터 여부
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

// 확장성 테스트용 mock 데이터
const MOCK_EXAMS: ExamMeta[] = [
  {
    exam: "9급 공무원",
    exam_type: "IP_GENERAL",
    year: 2026,
    subject: "정보보호론",
    is_mock: true,
  },
  {
    exam: "9급 공무원",
    exam_type: "IP_LOCAL",
    year: 2026,
    subject: "정보보호론",
    is_mock: true,
  },
  {
    exam: "7급 공무원",
    exam_type: "PS7_GENERAL",
    year: 2026,
    subject: "자료구조론",
    is_mock: true,
  },
  {
    exam: "7급 공무원",
    exam_type: "PS7_GENERAL",
    year: 2026,
    subject: "데이터베이스론",
    is_mock: true,
  },
  {
    exam: "7급 공무원",
    exam_type: "PS7_LOCAL",
    year: 2026,
    subject: "정보보호론",
    is_mock: true,
  },
  {
    exam: "정보처리기사",
    exam_type: "INFORMATION_PROCESSING_ENGINEER_WRITTEN",
    year: 2026,
    subject: "필기",
    round: "1회",
    is_mock: true,
  },
  {
    exam: "정보처리기사",
    exam_type: "INFORMATION_PROCESSING_ENGINEER_WRITTEN",
    year: 2026,
    subject: "필기",
    round: "2회",
    is_mock: true,
  },
];

// 백엔드 데이터에 exam 필드가 없을 경우 임시 분류
const normalizeExam = (
  exam: Omit<ExamMeta, "exam"> & { exam?: string }
): ExamMeta => {
  if (exam.exam) return exam as ExamMeta;

  if (exam.exam_type === "CS_GENERAL" || exam.exam_type === "CS_LOCAL") {
    return { ...exam, exam: "9급 공무원" };
  }

  if (exam.exam_type.startsWith("DRIVERS_LICENSE")) {
    return { ...exam, exam: "운전면허 필기" };
  }

  return { ...exam, exam: "기타" };
};

// 시험구분 표시명 변환
const getExamTypeLabel = (examType: string) => {
  switch (examType) {
    case "CS_GENERAL":
    case "IP_GENERAL":
    case "PS7_GENERAL":
      return "국가직";

    case "CS_LOCAL":
    case "IP_LOCAL":
    case "PS7_LOCAL":
      return "지방직";

    case "DRIVERS_LICENSE_1":
    case "DRIVERS_LICENSE_2":
      return "상시";

    case "INFORMATION_PROCESSING_ENGINEER_WRITTEN":
      return "필기";

    default:
      return examType;
  }
};

// 과목 표시명 변환
const getSubjectLabel = (subject: string) => {
  switch (subject) {
    case "운전면허 학과":
      return "교통법규";

    default:
      return subject;
  }
};

// 가나다/숫자/영문 자연 정렬
const sortByKorean = (a: string, b: string) =>
  a.localeCompare(b, "ko-KR", {
    numeric: true,
    sensitivity: "base",
  });

export default function FullExamPage() {
  const router = useRouter();

  // 사이드바 열림 상태
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  // 토글 조건 상태
  const [selectedExam, setSelectedExam] = useState("");
  const [selectedSubject, setSelectedSubject] = useState("");
  const [selectedYear, setSelectedYear] = useState("전체");
  const [selectedExamType, setSelectedExamType] = useState("전체");
  const [selectedRound, setSelectedRound] = useState("전체");

  // 키워드 검색 상태
  const [keyword, setKeyword] = useState("");
  const [submittedKeyword, setSubmittedKeyword] = useState("");

  // 시험 목록 상태
  const [exams, setExams] = useState<ExamMeta[]>([]);

  // 로딩/에러 상태
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");

  // 시험 목록 조회
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

        const data = await res.json();
        const normalizedData: ExamMeta[] = data.map(normalizeExam);

        setExams([...normalizedData, ...MOCK_EXAMS]);
      } catch (error) {
        console.error(error);
        setErrorMessage("시험 목록을 불러오지 못했습니다.");
        setExams(MOCK_EXAMS);
      } finally {
        setIsLoading(false);
      }
    };

    fetchExams();
  }, []);

  // 시험 옵션 생성
  const examOptions = useMemo(() => {
    return Array.from(new Set(exams.map((exam) => exam.exam))).sort(
      sortByKorean
    );
  }, [exams]);

  // 선택한 시험에 맞는 데이터
  const availableExams = useMemo(() => {
    if (!selectedExam) return exams;
    return exams.filter((exam) => exam.exam === selectedExam);
  }, [exams, selectedExam]);

  // 과목 옵션 생성
  const subjectOptions = useMemo(() => {
    return Array.from(
      new Set(availableExams.map((exam) => getSubjectLabel(exam.subject)))
    ).sort(sortByKorean);
  }, [availableExams]);

  // 연도 옵션 생성
  const yearOptions = useMemo(() => {
    return [
      "전체",
      ...Array.from(
        new Set(availableExams.map((exam) => String(exam.year)))
      ).sort((a, b) => Number(b) - Number(a)),
    ];
  }, [availableExams]);

  // 회차 옵션 생성
  const roundOptions = useMemo(() => {
    return [
      "전체",
      ...Array.from(
        new Set(
          availableExams
            .map((exam) => exam.round)
            .filter((round): round is string => Boolean(round))
        )
      ).sort(sortByKorean),
    ];
  }, [availableExams]);

  // 시험구분 옵션 생성
  const examTypeOptions = useMemo(() => {
    const types = Array.from(
      new Set(availableExams.map((exam) => getExamTypeLabel(exam.exam_type)))
    ).sort(sortByKorean);

    return ["전체", ...types];
  }, [availableExams]);

  // 선택 여부
  const isExamSelected = selectedExam !== "";
  const isSubjectSelected = selectedSubject !== "";

  // 시험별 조건 제어
  const isDriverLicense = selectedExam === "운전면허 필기";
  const isEngineer = selectedExam === "정보처리기사";
  const hasExamType = selectedExam.includes("공무원");
  const hasRound = isEngineer;

  // 사용자가 토글을 하나라도 선택했거나 검색을 실행했는지 확인
  const hasAnyFilter =
    selectedExam !== "" ||
    selectedSubject !== "" ||
    selectedYear !== "전체" ||
    selectedExamType !== "전체" ||
    selectedRound !== "전체" ||
    submittedKeyword.trim() !== "";

  // 토글 선택과 키워드 검색 결과를 자동 계산
  const filteredExams = useMemo(() => {
    const trimmedKeyword = submittedKeyword.trim().toLowerCase();

    return availableExams
      .filter((exam) => {
        const subjectMatched =
          !selectedSubject ||
          getSubjectLabel(exam.subject) === selectedSubject;

        const yearMatched =
          isDriverLicense ||
          selectedYear === "전체" ||
          String(exam.year) === selectedYear;

        const examTypeMatched =
          !hasExamType ||
          selectedExamType === "전체" ||
          getExamTypeLabel(exam.exam_type) === selectedExamType;

        const roundMatched =
          !hasRound ||
          selectedRound === "전체" ||
          exam.round === selectedRound;

        const searchText = `${exam.exam} ${getSubjectLabel(exam.subject)} ${exam.year
          } ${getExamTypeLabel(exam.exam_type)} ${exam.round ?? ""}`.toLowerCase();

        const keywordMatched =
          trimmedKeyword === "" || searchText.includes(trimmedKeyword);

        return (
          subjectMatched &&
          yearMatched &&
          examTypeMatched &&
          roundMatched &&
          keywordMatched
        );
      })
      .sort((a, b) => {
        if (b.year !== a.year) return b.year - a.year;

        const subjectCompare = sortByKorean(
          getSubjectLabel(a.subject),
          getSubjectLabel(b.subject)
        );

        if (subjectCompare !== 0) return subjectCompare;

        return sortByKorean(
          getExamTypeLabel(a.exam_type),
          getExamTypeLabel(b.exam_type)
        );
      });
  }, [
    availableExams,
    selectedSubject,
    selectedYear,
    selectedExamType,
    selectedRound,
    submittedKeyword,
    isDriverLicense,
    hasExamType,
    hasRound,
  ]);

  // 시험 변경 시 하위 조건 초기화
  const handleExamChange = (value: string) => {
    setSelectedExam(value);
    setSelectedSubject("");
    setSelectedYear("전체");
    setSelectedExamType("전체");
    setSelectedRound("전체");
  };

  // 과목 변경 시 하위 조건 초기화
  const handleSubjectChange = (value: string) => {
    setSelectedSubject(value);
    setSelectedYear("전체");
    setSelectedExamType("전체");
    setSelectedRound("전체");
  };

  // 검색 버튼은 키워드 검색만 실행
  const handleSearch = () => {
    setSubmittedKeyword(keyword);
  };

  // 토글 조건과 키워드 전체 초기화
  const handleResetSearch = () => {
    setSelectedExam("");
    setSelectedSubject("");
    setSelectedYear("전체");
    setSelectedExamType("전체");
    setSelectedRound("전체");
    setKeyword("");
    setSubmittedKeyword("");
  };

  // 실제 문제 풀이 페이지 이동
  const handleStartExam = (exam: ExamMeta) => {
    if (exam.is_mock) return;

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
      <Header onMenuClick={() => setIsMenuOpen(true)} onLoginClick={() => { }} />

      <Sidebar isOpen={isMenuOpen} onClose={() => setIsMenuOpen(false)} />

      <section className="mx-auto w-full max-w-6xl px-6 pb-12 pt-28">
        <div className="mb-8">
          <p className="mb-3 text-sm font-medium text-slate-500">
            기출문제 <span className="mx-2">›</span>
            <span className="text-slate-900">전체 회차 풀기</span>
          </p>

          <h1 className="text-3xl font-bold">전체 회차 풀기</h1>
          <p className="mt-2 text-slate-500">
            토글을 선택하면 회차 목록이 바로 반영되고, 검색창은 키워드 검색에 사용할 수 있습니다.
          </p>
        </div>

        <div className="space-y-6">
          <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="text-xl font-bold">검색 조건</h2>

            {/* 1줄: 토글 조건 + 초기화 버튼 */}
            <div className="mt-6 grid gap-4 md:grid-cols-[1fr_1fr_1fr_1fr_auto]">
              <SelectBox
                label="시험"
                value={selectedExam}
                onChange={handleExamChange}
                options={examOptions}
                placeholder="선택해주세요"
              />

              <SelectBox
                label="과목"
                value={selectedSubject}
                onChange={handleSubjectChange}
                options={subjectOptions}
                placeholder={isExamSelected ? "선택해주세요" : "시험 먼저 선택"}
                disabled={!isExamSelected}
              />

              <SelectBox
                label="연도"
                value={selectedYear}
                onChange={setSelectedYear}
                options={yearOptions}
                disabled={!isSubjectSelected || isDriverLicense}
              />

              {hasRound ? (
                <SelectBox
                  label="회차"
                  value={selectedRound}
                  onChange={setSelectedRound}
                  options={roundOptions}
                  disabled={!isSubjectSelected}
                />
              ) : (
                <SelectBox
                  label="시험구분"
                  value={selectedExamType}
                  onChange={setSelectedExamType}
                  options={examTypeOptions}
                  disabled={!isSubjectSelected || !hasExamType}
                />
              )}

              <div className="flex items-end">
                <button
                  type="button"
                  onClick={handleResetSearch}
                  className="h-12 rounded-xl border border-slate-200 bg-white px-5 font-semibold text-slate-600 transition hover:border-blue-200 hover:bg-blue-50 hover:text-blue-600"
                >
                  초기화
                </button>
              </div>
            </div>

            {/* 2줄: 키워드 검색창 + 검색 버튼 */}
            <div className="mt-4 flex flex-col gap-3 md:flex-row">
              <input
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") handleSearch();
                }}
                placeholder="시험명, 과목, 연도, 회차를 검색해보세요."
                className="h-12 flex-1 rounded-xl border border-slate-200 bg-white px-4 text-sm font-medium text-slate-800 outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:ring-4 focus:ring-blue-50"
              />

              <button
                type="button"
                onClick={handleSearch}
                className="h-12 rounded-xl bg-blue-600 px-8 font-bold text-white shadow-md transition hover:bg-blue-700"
              >
                검색
              </button>
            </div>
          </section>

          <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-bold">회차 목록</h2>

              <span className="text-sm text-slate-500">
                총 {filteredExams.length}개 회차
              </span>
            </div>

            <div className="mt-6 grid gap-4">
              {isLoading ? (
                <EmptyBox title="시험 목록을 불러오는 중입니다..." />
              ) : errorMessage && exams.length === 0 ? (
                <EmptyBox title={errorMessage} isError />
              ) : !hasAnyFilter ? (
                <EmptyBox
                  title="시험을 선택하거나 검색어를 입력해보세요."
                  description="조건을 선택하면 회차 목록이 바로 표시됩니다."
                />
              ) : filteredExams.length > 0 ? (
                filteredExams.map((exam) => (
                  <div
                    key={`${exam.year}-${exam.exam_type}-${exam.subject}-${exam.round ?? ""
                      }`}
                    className="flex flex-col gap-5 rounded-2xl border border-slate-200 bg-white p-5 transition hover:border-blue-200 hover:bg-blue-50/40 hover:shadow-sm md:flex-row md:items-center md:justify-between"
                  >
                    <div>
                      <div className="flex flex-wrap items-center gap-3">
                        <h3 className="text-lg font-extrabold text-slate-900">
                          {exam.exam} · {getSubjectLabel(exam.subject)}
                        </h3>

                        <span className="rounded-full bg-blue-50 px-3 py-1 text-sm font-bold text-blue-600">
                          {exam.exam === "운전면허 필기"
                            ? "상시"
                            : `${exam.year}년`}
                        </span>

                        {exam.round && (
                          <span className="rounded-full bg-orange-50 px-3 py-1 text-sm font-bold text-orange-600">
                            {exam.round}
                          </span>
                        )}

                        <span className="rounded-full bg-slate-100 px-3 py-1 text-sm font-bold text-slate-600">
                          {getExamTypeLabel(exam.exam_type)}
                        </span>

                        {exam.is_mock && (
                          <span className="rounded-full bg-purple-50 px-3 py-1 text-sm font-bold text-purple-600">
                            mock
                          </span>
                        )}
                      </div>

                      <p className="mt-2 text-sm text-slate-500">
                        전체 회차 풀이
                      </p>
                    </div>

                    <button
                      type="button"
                      onClick={() => handleStartExam(exam)}
                      disabled={exam.is_mock}
                      className="h-12 rounded-xl bg-blue-600 px-7 font-bold text-white shadow-md transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-300 md:w-auto"
                    >
                      {exam.is_mock ? "준비중" : "응시하기"}
                    </button>
                  </div>
                ))
              ) : (
                <EmptyBox
                  title="표시할 회차가 없습니다."
                  description="조건을 바꾸거나 검색어를 다시 입력해보세요."
                />
              )}
            </div>
          </section>
        </div>
      </section>
    </main>
  );
}

function SelectBox({
  label,
  value,
  onChange,
  options,
  placeholder,
  disabled = false,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  options: string[];
  placeholder?: string;
  disabled?: boolean;
}) {
  return (
    <div>
      <label className="mb-2 block text-sm font-semibold text-slate-700">
        {label}
      </label>

      <div className="relative">
        <select
          value={value}
          onChange={(e) => onChange(e.target.value)}
          disabled={disabled}
          className="h-12 w-full appearance-none rounded-xl border border-slate-200 bg-white px-4 pr-10 text-[13px] font-semibold text-slate-800 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-50 disabled:cursor-not-allowed disabled:bg-slate-100 disabled:text-slate-400"
        >
          {placeholder && <option value="">{placeholder}</option>}

          {options.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>

        <ChevronDown
          size={18}
          className="pointer-events-none absolute right-4 top-1/2 -translate-y-1/2 text-slate-400"
        />
      </div>
    </div>
  );
}

function EmptyBox({
  title,
  description,
  isError = false,
}: {
  title: string;
  description?: string;
  isError?: boolean;
}) {
  return (
    <div
      className={`rounded-2xl border border-dashed p-10 text-center ${isError ? "border-red-300 bg-red-50" : "border-slate-300 bg-slate-50"
        }`}
    >
      <p className={`font-bold ${isError ? "text-red-600" : "text-slate-700"}`}>
        {title}
      </p>

      {description && (
        <p className="mt-2 text-sm text-slate-500">{description}</p>
      )}
    </div>
  );
}