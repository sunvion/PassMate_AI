"use client";

import { useState } from "react";
import Image from "next/image";
import Link from "next/link";
import {
  Home,
  UserRound,
  ClipboardList,
  ChevronRight,
} from "lucide-react";

export default function HomePage() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isWrongNoteOpen, setIsWrongNoteOpen] = useState(false);
  const [isExamOpen, setIsExamOpen] = useState(false);
  const [isLoginOpen, setIsLoginOpen] = useState(false);

  return (
    <main className="min-h-screen bg-white text-slate-900">
      {/* 상단 헤더 */}
      <header className="fixed left-0 top-0 z-50 flex h-16 w-full items-center justify-between border-b border-slate-200 bg-white/90 px-8 backdrop-blur">
        <div className="flex items-center gap-4 md:gap-8">
          <button
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            className="text-2xl"
          >
            ☰
          </button>

          <Link href="/">
            <div className="flex items-center gap-3 font-bold text-xl">
              <Image
                src="/images/PM_icon.png"
                alt="PassMate AI 로고"
                width={45}
                height={45}
                className="rounded-lg"
                priority
              />
              <span className="hidden md:block">PassMate AI</span>
            </div>
          </Link>
        </div>

        <button
          onClick={() => setIsLoginOpen(true)}
          className="rounded-lg bg-blue-600 px-5 py-2 text-sm font-semibold text-white shadow hover:bg-blue-700"
        >
          로그인
        </button>
      </header>

      {/* 메뉴 열렸을 때 배경 어둡게 */}
      {isMenuOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/40"
          onClick={() => setIsMenuOpen(false)}
        />
      )}

      {/* 사이드 메뉴 */}
      <aside
        className={`fixed left-4 top-20 z-40 h-[calc(100vh-6rem)] w-[90vw] max-w-[320px] overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-2xl transition-transform duration-300 ${isMenuOpen ? "translate-x-0" : "-translate-x-[120%]"
          }`}>

        <nav className="mt-4 flex flex-col gap-4 px-3 text-lg font-semibold">
          {/* 홈 */}
          <div>
            <Link
              href="/"
              onClick={() => setIsMenuOpen(false)}
              className="flex items-center justify-between rounded-2xl bg-blue-50 px-5 py-4 text-blue-600 shadow-sm transition hover:bg-blue-600 hover:text-white hover:shadow-md"
            >
              <span className="flex items-center gap-4">
                <Home size={28} />
                홈
              </span>
              <ChevronRight size={24} />
            </Link>
          </div>

          {/* 마이페이지 */}
          <div>
            <Link
              href="/mypage"
              onClick={() => setIsMenuOpen(false)}
              className="flex items-center gap-4 rounded-2xl px-5 py-4 transition hover:bg-blue-50 hover:text-blue-600 hover:shadow-md"
            >
              <UserRound size={28} />
              마이페이지
            </Link>

            <div className="ml-[68px] mt-3 flex flex-col gap-4 text-base font-medium text-slate-700">
              <Link
                href="/stats"
                onClick={() => setIsMenuOpen(false)}
                className="hover:text-blue-600"
              >
                학습 통계
              </Link>

              {/* 오답노트 접힘 메뉴 */}
              <button
                type="button"
                onClick={() => setIsWrongNoteOpen(!isWrongNoteOpen)}
                className="flex items-center justify-between text-left hover:text-blue-600"
              >
                <span>오답노트</span>
                <ChevronRight
                  size={18}
                  className={`transition-transform ${isWrongNoteOpen ? "rotate-90" : ""
                    }`}
                />
              </button>

              {isWrongNoteOpen && (
                <div className="ml-4 flex flex-col gap-3 text-sm text-slate-600">
                  <Link
                    href="/wrong-note/ai-helper"
                    onClick={() => setIsMenuOpen(false)}
                    className="hover:text-blue-600"
                  >
                    AI 학습 도우미
                  </Link>

                  <Link
                    href="/wrong-note/review"
                    onClick={() => setIsMenuOpen(false)}
                    className="hover:text-blue-600"
                  >
                    복습
                  </Link>
                </div>
              )}

              <Link
                href="/settings/account"
                onClick={() => setIsMenuOpen(false)}
                className="hover:text-blue-600"
              >
                계정 관리
              </Link>
            </div>
          </div>

          {/* 기출문제 */}
          <div>
            <Link
              href="/exams"
              onClick={() => setIsMenuOpen(false)}
              className="flex items-center gap-4 rounded-2xl px-5 py-4 transition hover:bg-blue-50 hover:text-blue-600 hover:shadow-md"
            >
              <ClipboardList size={28} />
              기출문제
            </Link>

            <div className="ml-[68px] mt-3 flex flex-col gap-4 text-base font-medium text-slate-700">
              {/* 회차별 풀기 접힘 메뉴 */}
              <button
                type="button"
                onClick={() => setIsExamOpen(!isExamOpen)}
                className="flex items-center justify-between text-left hover:text-blue-600"
              >
                <span>회차별 풀기</span>
                <ChevronRight
                  size={18}
                  className={`transition-transform ${isExamOpen ? "rotate-90" : ""
                    }`}
                />
              </button>

              {isExamOpen && (
                <div className="ml-4 flex flex-col gap-3 text-sm text-slate-600">
                  <Link
                    href="/exams/full"
                    onClick={() => setIsMenuOpen(false)}
                    className="hover:text-blue-600"
                  >
                    전체 회차 풀기
                  </Link>

                  <Link
                    href="/exams/single"
                    onClick={() => setIsMenuOpen(false)}
                    className="hover:text-blue-600"
                  >
                    한 문제씩 풀기
                  </Link>
                </div>
              )}
            </div>
          </div>
        </nav>
      </aside>

      {/* 1. 메인 소개 섹션 */}
      <section className="flex min-h-screen items-center justify-center bg-gradient-to-br from-blue-50 via-white to-blue-50 px-10 pt-16">
        <div className="grid w-full max-w-6xl grid-cols-1 lg:grid-cols-2 items-center gap-16">
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
              className="rounded-lg bg-blue-600 px-10 py-4 font-bold text-white shadow-lg hover:bg-blue-700">
              지금 시작하기
            </button>
          </div>

          <div className="flex justify-center translate-y-12">
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
          <StepCard number="5" icon="📈" title="취약 유형 복습" />
        </div>
      </section>
      {isLoginOpen && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center px-4">
          {/* 흐려지는 배경 */}
          <div
            className="absolute inset-0 bg-black/45 backdrop-blur-sm"
            onClick={() => setIsLoginOpen(false)}
          />

          {/* 로그인 모달 */}
          <div className="relative z-[101] w-full max-w-md rounded-3xl bg-white p-8 shadow-2xl">
            <button
              onClick={() => setIsLoginOpen(false)}
              className="absolute right-5 top-5 text-xl text-slate-400 hover:text-slate-700"
            >
              ×
            </button>

            <div className="mb-6 text-center">
              <h2 className="text-3xl font-extrabold text-slate-900">
                로그인 / 회원가입
              </h2>
              <p className="mt-3 text-sm leading-6 text-slate-500">
                Google 계정으로 간편하게 로그인하고
                <br />
                PassMate AI 학습을 시작하세요.
              </p>
            </div>

            <button className="relative flex w-full items-center rounded-xl border border-slate-300 bg-white px-6 py-4 font-bold text-slate-800 shadow-sm transition hover:bg-slate-50">
              <Image
                src="/images/google_logo.png"
                alt="Google 로고"
                width={36}
                height={36}
              />

              <span className="absolute left-1/2 -translate-x-1/2">
                Google로 계속하기
              </span>
            </button>

            <div className="mt-6 space-y-3 text-sm font-medium text-slate-600">
              <p className="flex items-center gap-3">
                <span className="flex h-6 w-6 items-center justify-center rounded-full bg-blue-100 text-blue-600">
                  ✓
                </span>
                Google 계정으로 안전하게 로그인
              </p>

              <p className="flex items-center gap-3">
                <span className="flex h-6 w-6 items-center justify-center rounded-full bg-blue-100 text-blue-600">
                  ✓
                </span>
                처음이신가요? 자동으로 회원가입이 진행돼요
              </p>
            </div>

            <div className="mt-8 rounded-2xl bg-blue-50 p-5">
              <p className="font-bold text-slate-800">안심하고 사용하세요</p>

              <p className="mt-2 text-sm leading-6 text-slate-600">
                개인정보는 안전하게 보호되며,
                <br />
                Google 계정 정보는 로그인 용도로만 사용됩니다.
              </p>
            </div>

            <p className="mt-8 text-center text-xs leading-5 text-slate-400">
              계속하면 서비스 이용약관 및 개인정보 처리방침에
              <br />
              동의하는 것으로 간주됩니다.
            </p>
          </div>
        </div>
  )
}
    </main >
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
    <div className="relative rounded-2xl bg-white p-6 shadow-md">
      <div className="absolute -top-4 left-1/2 flex h-8 w-8 -translate-x-1/2 items-center justify-center rounded-full bg-blue-600 text-sm font-bold text-white">
        {number}
      </div>
      <div className="mb-5 mt-4 text-5xl">{icon}</div>
      <h3 className="font-bold">{title}</h3>
    </div>
  );
}