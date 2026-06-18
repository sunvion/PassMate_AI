"use client";

import { useEffect, useState } from "react";

import Header from "../../components/Header";
import Sidebar from "../../components/Sidebar";

import {
  BarChart3,
  ClipboardList,
  RotateCcw,
  Sparkles,
  Target,
} from "lucide-react";

const subjects = [
  {
    name: "국가직 9급 컴퓨터일반",
    areas: [
      "컴퓨터구조",
      "운영체제",
      "데이터베이스",
      "자료 구조",
      "프로그래밍 언어론",
      "소프트웨어 공학 및 시스템 설계",
      "데이터 통신과 네트워크",
      "인터넷 및 최신 기술 용어",
    ],
  },
  {
    name: "지방직 9급 컴퓨터일반",
    areas: [
      "컴퓨터구조",
      "운영체제",
      "데이터베이스",
      "자료 구조",
      "프로그래밍 언어론",
      "소프트웨어 공학 및 시스템 설계",
      "데이터 통신과 네트워크",
      "인터넷 및 최신 기술 용어",
    ],
  },
  {
    name: "운전면허",
    areas: ["교통법규", "안전운전", "도로표지", "응급처치", "차량관리"],
  },
];

export default function MyPage() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);

  const [selectedSubject, setSelectedSubject] = useState(0);
  const [values, setValues] = useState<number[]>([]);
  const [expectedScore, setExpectedScore] = useState(72);

  const current = subjects[selectedSubject];

  useEffect(() => {
    const makeRandomValues = () => {
      setValues(current.areas.map(() => Math.floor(Math.random() * 35) + 45));
      setExpectedScore(Math.floor(Math.random() * 20) + 65);
    };

    makeRandomValues();

    const timer = setInterval(() => {
      makeRandomValues();
    }, 1500);

    return () => clearInterval(timer);
  }, [selectedSubject, current.areas]);

  const polygonPoints = values
    .map((value, index) => {
      const angle = (Math.PI * 2 * index) / values.length - Math.PI / 2;
      const radius = value * 1.15;
      const x = 150 + Math.cos(angle) * radius;
      const y = 150 + Math.sin(angle) * radius;
      return `${x},${y}`;
    })
    .join(" ");

  const averageRate =
    values.length > 0
      ? Math.round(values.reduce((sum, value) => sum + value, 0) / values.length)
      : 0;

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <Header
        onMenuClick={() => setIsMenuOpen(!isMenuOpen)}
        onLoginClick={() => setIsLoginModalOpen(true)}
      />

      <div className="flex pt-16">
        <Sidebar
          isOpen={isMenuOpen}
          onClose={() => setIsMenuOpen(false)}
        />

        <section className="mx-auto w-full max-w-[1500px] px-10 py-8">
          <div className="mb-8 flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold">
                마이페이지 <span className="text-slate-400">›</span> 학습 통계
              </h1>
              <p className="mt-2 text-slate-500">
                아직 학습 데이터가 없어요. 문제를 풀면 나만의 학습 통계가 생성됩니다.
              </p>
            </div>

            <p className="text-sm text-slate-500">
              추후 OAuth 연동 후 프로필 영역으로 변경 예정
            </p>
          </div>

          <div className="mb-6 grid grid-cols-3 overflow-hidden rounded-2xl border border-slate-200 bg-white">
            {subjects.map((subject, index) => {
              const isSelected = selectedSubject === index;

              return (
                <button
                  key={subject.name}
                  onClick={() => setSelectedSubject(index)}
                  className={`relative py-5 text-lg font-semibold transition
          ${isSelected
                      ? "border-t-4 border-blue-600 bg-gradient-to-b from-blue-100 to-white text-blue-600"
                      : "text-slate-700 hover:bg-slate-50"
                    }
          ${index !== subjects.length - 1 ? "border-r border-slate-200" : ""}
        `}
                >
                  {subject.name}
                </button>
              );
            })}
          </div>

          <div className="grid grid-cols-2 gap-6">
            <article className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
              <div className="mb-6 flex items-center justify-between">
                <h2 className="text-2xl font-bold">
                  {current.areas.length}개 단원별 예상 정답률
                </h2>

                <span className="rounded-full bg-blue-50 px-3 py-1 text-sm font-semibold text-blue-600">
                  예시 화면
                </span>
              </div>

              <div className="flex justify-center">
                <svg width="470" height="390" viewBox="0 0 300 300">
                  {[45, 85, 120].map((r) => (
                    <circle
                      key={r}
                      cx="150"
                      cy="150"
                      r={r}
                      fill="none"
                      stroke="#dbe4f0"
                    />
                  ))}

                  {current.areas.map((area, index) => {
                    const angle =
                      (Math.PI * 2 * index) / current.areas.length -
                      Math.PI / 2;

                    const lineX = 150 + Math.cos(angle) * 120;
                    const lineY = 150 + Math.sin(angle) * 120;
                    const textX = 150 + Math.cos(angle) * 150;
                    const textY = 150 + Math.sin(angle) * 150;

                    return (
                      <g key={area}>
                        <line
                          x1="150"
                          y1="150"
                          x2={lineX}
                          y2={lineY}
                          stroke="#dbe4f0"
                        />

                        <text
                          x={textX}
                          y={textY}
                          textAnchor="middle"
                          dominantBaseline="middle"
                          className="fill-slate-700 text-[8px] font-semibold"
                        >
                          {area.length > 10 ? area.slice(0, 10) + "..." : area}
                        </text>
                      </g>
                    );
                  })}

                  <polygon
                    points={polygonPoints}
                    fill="rgba(37, 99, 235, 0.18)"
                    stroke="#2563eb"
                    strokeWidth="2"
                    style={{
                      transition: "points 500ms ease",
                    }}
                  />

                  {values.map((value, index) => {
                    const angle =
                      (Math.PI * 2 * index) / values.length - Math.PI / 2;
                    const radius = value * 1.15;
                    const x = 150 + Math.cos(angle) * radius;
                    const y = 150 + Math.sin(angle) * radius;

                    return (
                      <circle
                        key={index}
                        cx={x}
                        cy={y}
                        r="4"
                        fill="#2563eb"
                        style={{
                          transition: "cx 500ms ease, cy 500ms ease",
                        }}
                      />
                    );
                  })}
                </svg>
              </div>

              <div className="mt-4 rounded-2xl bg-blue-50 p-5 text-center">
                <p className="font-bold text-blue-600">
                  문제를 풀면 실제 데이터로 학습 통계가 채워집니다.
                </p>
                <p className="mt-1 text-sm text-slate-600">
                  단원별 정답률, 취약 영역, 복습 우선순위를 확인할 수 있어요.
                </p>
              </div>
            </article>

            <article className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
              <h2 className="mb-6 text-2xl font-bold">최근 응시 기출문제</h2>

              <div className="rounded-3xl border border-blue-100 bg-blue-50 p-8 text-center">
                <Sparkles className="mx-auto mb-4 text-blue-600" size={42} />

                <p className="text-lg font-semibold text-slate-700">
                  아직 응시한 기출문제가 없어요
                </p>

                <p className="mt-2 text-slate-500">
                  첫 문제를 풀면 최근 응시 기록과 예상 점수가 표시됩니다.
                </p>

                <div className="mt-6 text-6xl font-black text-blue-600">
                  {expectedScore}
                  <span className="text-2xl">점</span>
                </div>

                <p className="mt-2 text-sm text-slate-500">예시 예상 점수</p>
              </div>

              <div className="mt-6 grid grid-cols-2 gap-4">
                <div className="rounded-2xl border border-slate-200 p-5 text-center">
                  <Target className="mx-auto mb-2 text-blue-600" />
                  <p className="text-sm text-slate-500">예상 정답률</p>
                  <p className="text-2xl font-bold">{averageRate}%</p>
                </div>

                <div className="rounded-2xl border border-slate-200 p-5 text-center">
                  <RotateCcw className="mx-auto mb-2 text-blue-600" />
                  <p className="text-sm text-slate-500">복습 필요 단원</p>
                  <p className="text-2xl font-bold">0개</p>
                </div>
              </div>

              <button className="mt-6 flex w-full items-center justify-center gap-2 rounded-2xl bg-blue-600 py-4 font-bold text-white transition hover:bg-blue-700">
                <ClipboardList size={20} />
                기출문제 풀러가기
              </button>
            </article>
          </div>

          <article className="mt-6 rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
            <h2 className="mb-6 text-2xl font-bold">학습 요약</h2>

            <div className="grid grid-cols-3 gap-6">
              <div className="flex items-center gap-4 rounded-2xl bg-slate-50 p-6">
                <BarChart3 className="text-blue-600" size={36} />
                <div>
                  <p className="text-slate-500">총 풀이 문제 수</p>
                  <p className="text-3xl font-bold">0 문제</p>
                </div>
              </div>

              <div className="flex items-center gap-4 rounded-2xl bg-slate-50 p-6">
                <Target className="text-blue-600" size={36} />
                <div>
                  <p className="text-slate-500">평균 정답률</p>
                  <p className="text-3xl font-bold">- %</p>
                </div>
              </div>

              <div className="flex items-center gap-4 rounded-2xl bg-slate-50 p-6">
                <ClipboardList className="text-blue-600" size={36} />
                <div>
                  <p className="text-slate-500">최근 응시 기록</p>
                  <p className="text-3xl font-bold">없음</p>
                </div>
              </div>
            </div>
          </article>
        </section>
      </div>
    </main>
  );
}