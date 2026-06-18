"use client";

import { useState } from "react";
import Header from "@/components/Header";
import Sidebar from "@/components/Sidebar";
import LoginModal from "@/components/LoginModal";

export default function MyPage() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isLoginOpen, setIsLoginOpen] = useState(false);

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <Header
        onMenuClick={() => setIsMenuOpen(!isMenuOpen)}
        onLoginClick={() => setIsLoginOpen(true)}
      />

      <Sidebar
        isOpen={isMenuOpen}
        onClose={() => setIsMenuOpen(false)}
      />

      <section className="px-8 pb-12 pt-24">
        <div className="mx-auto max-w-7xl">
          <p className="text-sm font-semibold text-slate-500">
            마이페이지 &gt; 학습 통계
          </p>

          <h1 className="mt-2 text-3xl font-extrabold">
            학습 통계
          </h1>

          <div className="mt-8 grid grid-cols-3 overflow-hidden rounded-2xl border border-slate-200 bg-white">
            <button className="border border-blue-600 bg-blue-50 py-5 text-lg font-bold text-blue-600">
              국가직 9급 컴퓨터일반
            </button>
            <button className="py-5 text-lg font-bold text-slate-700">
              지방직 9급 컴퓨터일반
            </button>
            <button className="py-5 text-lg font-bold text-slate-700">
              운전면허
            </button>
          </div>

          <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-2">
            <div className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
              <h2 className="text-2xl font-extrabold">
                7대 단원별 정답률
              </h2>

              <div className="mt-8 rounded-2xl border border-dashed border-blue-200 bg-blue-50 p-16 text-center">
                <p className="font-bold text-blue-600">
                  방사형 그래프 자리
                </p>
                <p className="mt-3 text-sm text-slate-600">
                  다음 단계에서 파란색 그래프 애니메이션을 넣을 거야.
                </p>
              </div>
            </div>

            <div className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
              <h2 className="text-2xl font-extrabold">
                최근 응시 기출문제
              </h2>

              <div className="mt-8 rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-10 text-center">
                <p className="text-lg font-bold text-slate-700">
                  아직 응시한 기출문제가 없어요
                </p>

                <p className="mt-3 text-sm leading-6 text-slate-500">
                  기출문제를 풀면 최근 응시 기록과 점수가 이곳에 표시됩니다.
                </p>
              </div>
            </div>
          </div>

          <div className="mt-6 rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
            <h2 className="text-2xl font-extrabold">
              학습 요약
            </h2>

            <div className="mt-6 grid grid-cols-1 gap-6 md:grid-cols-2">
              <SummaryCard title="총 풀이 문제 수" value="0 문제" />
              <SummaryCard title="평균 정답률" value="0%" />
            </div>
          </div>
        </div>
      </section>

      {isLoginOpen && (
        <LoginModal onClose={() => setIsLoginOpen(false)} />
      )}
    </main>
  );
}

function SummaryCard({
  title,
  value,
}: {
  title: string;
  value: string;
}) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6">
      <p className="text-sm font-bold text-slate-500">{title}</p>
      <p className="mt-3 text-3xl font-extrabold text-slate-900">{value}</p>
    </div>
  );
}