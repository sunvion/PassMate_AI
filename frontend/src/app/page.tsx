"use client";

import { useState } from "react";
import Image from "next/image";

import Header from "../components/Header";
import Sidebar from "../components/Sidebar";
import LoginModal from "../components/LoginModal";

export default function HomePage() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isLoginOpen, setIsLoginOpen] = useState(false);
  const isLoggedIn = false; // 원격 dev 브랜치 로그인 상태 플래그 반영

  return (
    <main className="min-h-screen bg-white text-slate-900">
      <Header
        onMenuClick={() => setIsMenuOpen(!isMenuOpen)}
        onLoginClick={() => setIsLoginOpen(true)}
      />

      <Sidebar
        isOpen={isMenuOpen}
        onClose={() => setIsMenuOpen(false)}
        isLoggedIn={isLoggedIn} // 원격 dev 브랜치 프롭스 구조 반영
      />

      {/* 1. 메인 소개 섹션 (원격 dev 브랜치 id="start-section" 반영) */}
      <section 
        id="start-section"
        className="flex min-h-screen items-center justify-center bg-gradient-to-br from-blue-50 via-white to-blue-50 px-10 pt-16"
      >
        <div className="grid w-full max-w-6xl grid-cols-1 items-center gap-16 lg:grid-cols-2">
          <div className="mx-auto max-w-xl lg:ml-28">
            <h1 className="mb-6 text-5xl font-extrabold leading-tight">
              <span className="text-blue-600">AI와 함께</span>
              <br />
              합격을 설계하는
              <br />
              <span className="text-blue-600">나만의 학습 파트너</span>
            </h1>

            <p className="mb-8 text-lg leading-8 text-slate-600">
              PassMate AI는 기출 분석과 AI 기술을 통해
              <br />
              공무원 시험 합격까지 가장 스마트한 길을 제시합니다.
            </p>

            <button
              onClick={() => setIsLoginOpen(true)}
              className="rounded-lg bg-blue-600 px-10 py-4 font-bold text-white shadow-lg hover:bg-blue-700"
            >
              지금 시작하기
            </button>
          </div>

          <div className="flex translate-y-12 justify-center">
            <Image
              src="/images/homepage_main.png"
              alt="PassMate AI 메인 이미지"
              width={800}
              height={600}
              priority
              className="w-full max-w-[720px] object-contain px-4"
            />
          </div>
        </div>
      </section>

      {/* 2. 핵심 기능 섹션 */}
      <section className="flex min-h-screen flex-col items-center justify-center px-10">
        <span className="mb-4 rounded-full bg-blue-100 px-4 py-2 text-sm font-bold text-blue-600">
          핵심 기능
        </span>

        <h2 className="mb-12 text-4xl font-extrabold">
          AI가 분석하고, 합격까지 함께합니다
        </h2>

        <div className="grid w-full max-w-6xl grid-cols-3 gap-8">
          <FeatureCard
            icon="📘"
            title="자동 오답노트"
            desc="틀린 문제를 자동으로 저장하고 기출 연도별로 정리해줍니다."
          />
          <FeatureCard
            icon="🤖"
            title="AI 질문 & 해설"
            desc="이해되지 않는 문제는 AI에게 질문하고 해설을 받아볼 수 있습니다."
          />
          <FeatureCard
            icon="📊"
            title="약점 유형 분석"
            desc="자주 틀리는 단원과 유형을 분석해 학습 우선순위를 제안합니다."
          />
        </div>
      </section>

      {/* 3. 학습 흐름 섹션 */}
      <section className="flex min-h-screen flex-col items-center justify-center bg-blue-50 px-10">
        <span className="mb-4 rounded-full bg-blue-100 px-4 py-2 text-sm font-bold text-blue-600">
          학습 흐름
        </span>

        <h2 className="mb-16 text-4xl font-extrabold">
          PassMate AI와 함께하는 학습 과정
        </h2>

        <div className="grid w-full max-w-6xl grid-cols-5 gap-6 text-center">
          <StepCard number="1" icon="📝" title="기출문제 풀이" />
          <StepCard number="2" icon="✅" title="채점 및 결과 확인" />
          <StepCard number="3" icon="📘" title="오답 자동 저장" />
          <StepCard number="4" icon="🤖" title="AI 해설 질문" />
          <StepCard number="5" icon="📈" title="약점 유형 복습" />
        </div>
      </section>

      {isLoginOpen && (
        <LoginModal onClose={() => setIsLoginOpen(false)} />
      )}
    </main>
  );
}

function FeatureCard({
  icon,
  title,
  desc,
}: {
  icon: string;
  title: string;
  desc: string;
}) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-8 shadow-md transition hover:-translate-y-1 hover:shadow-xl">
      <div className="mb-6 text-6xl">{icon}</div>
      <h3 className="mb-3 text-xl font-bold">{title}</h3>
      <p className="leading-7 text-slate-600">{desc}</p>
    </div>
  );
}

function StepCard({
  number,
  icon,
  title,
}: {
  number: string;
  icon: string;
  title: string;
}) {
  return (
    <div className="rounded-xl border border-slate-100 bg-white p-6 shadow-sm">
      <div className="mx-auto mb-3 flex h-8 w-8 items-center justify-center rounded-full bg-blue-600 font-bold text-white text-sm">
        {number}
      </div>
      <div className="mb-2 text-4xl">{icon}</div>
      <h3 className="font-semibold text-slate-800">{title}</h3>
    </div>
  );
}