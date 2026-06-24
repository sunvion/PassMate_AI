'use client'

import { useEffect, useState } from 'react'
import Image from 'next/image'

import Header from '../components/Header'
import Sidebar from '../components/Sidebar'
import LoginModal from '../components/LoginModal'

export default function HomePage() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [isLoginOpen, setIsLoginOpen] = useState(false)
  const [isLoggedIn, setIsLoggedIn] = useState(false)

  useEffect(() => {
    const token = localStorage.getItem('token')
    setIsLoggedIn(!!token)
  }, [])

  return (
    <main className="min-h-screen bg-white text-slate-900">
      <Header
        onMenuClick={() => setIsMenuOpen(!isMenuOpen)}
        onLoginClick={() => setIsLoginOpen(true)}
      />

      <Sidebar isOpen={isMenuOpen} onClose={() => setIsMenuOpen(false)} />

      {/* 1. 메인 소개 섹션 */}
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

            {!isLoggedIn && (
              <button
                onClick={() => setIsLoginOpen(true)}
                className="rounded-lg bg-blue-600 px-10 py-4 font-bold text-white shadow-lg hover:bg-blue-700"
              >
                지금 시작하기
              </button>
            )}
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

      {/* 2. 자동 분석 섹션 */}
      <section className="flex min-h-screen flex-col items-center justify-center bg-white px-10 py-24">
        <span className="mb-4 rounded-full bg-blue-100 px-4 py-2 text-sm font-bold text-blue-600">
          자동 분석
        </span>

        <h2 className="mb-4 text-center text-4xl font-extrabold leading-tight">
          풀이 후 자동으로 오답을 모으고,
          <br />
          약점까지 분석해 드려요
        </h2>

        <p className="mb-14 text-center text-lg leading-8 text-slate-500">
          문제 제출부터 오답노트 생성, 약점 분석까지 하나의 흐름으로 이어집니다.
        </p>

        <div className="grid w-full max-w-6xl grid-cols-1 items-stretch gap-6 lg:grid-cols-[1fr_40px_1fr_40px_1fr]">
          <AnalysisStepCard
            number="1"
            title="문제 풀이"
            subtitle="2024 국가직 9급"
          >
            <div className="mt-6 space-y-4">
              <SkeletonLine />
              <SkeletonLine short />
              <OptionRow label="A" />
              <OptionRow label="B" wrong />
              <OptionRow label="C" />
              <OptionRow label="D" />
            </div>
          </AnalysisStepCard>

          <FlowArrow />

          <AnalysisStepCard
            number="2"
            title="자동 분석"
            subtitle="정답률과 오답 유형 확인"
          >
            <div className="mt-6 flex items-center justify-center gap-8">
              <div className="relative flex h-32 w-32 items-center justify-center">
                <svg
                  className="-rotate-90"
                  width="128"
                  height="128"
                  viewBox="0 0 128 128"
                >
                  {/* 배경 */}
                  <circle
                    cx="64"
                    cy="64"
                    r="52"
                    fill="none"
                    stroke="#DBEAFE"
                    strokeWidth="12"
                  />

                  {/* 진행률 */}
                  <circle
                    cx="64"
                    cy="64"
                    r="52"
                    fill="none"
                    stroke="#2563EB"
                    strokeWidth="12"
                    strokeLinecap="round"
                    strokeDasharray={327}
                    strokeDashoffset={327 - (327 * 75) / 100}
                  />
                </svg>

                <div className="absolute text-3xl font-extrabold text-blue-600">
                  75%
                </div>
              </div>

              <div className="space-y-3">
                <ResultBadge label="정답" value="15" />
                <ResultBadge label="오답" value="3" />
                <ResultBadge label="미응답" value="2" />
              </div>
            </div>

            <div className="mt-7 space-y-3">
              <WeakBar label="운영체제" percent="82%" />
              <WeakBar label="데이터베이스" percent="64%" />
              <WeakBar label="네트워크" percent="45%" />
            </div>
          </AnalysisStepCard>

          <FlowArrow />

          <AnalysisStepCard
            number="3"
            title="오답노트 생성"
            subtitle="복습할 문제 자동 정리"
          >
            <div className="mt-7 rounded-2xl bg-blue-50 p-5 text-center">
              <p className="text-sm font-bold text-blue-600">
                오답노트 생성 완료
              </p>
              <h3 className="mt-2 text-xl font-extrabold text-slate-900">
                2024 컴퓨터일반 오답
              </h3>

              <div className="mt-5 grid grid-cols-2 gap-3">
                <div className="rounded-xl bg-white p-4">
                  <p className="text-2xl font-extrabold text-blue-600">5개</p>
                  <p className="text-sm text-slate-500">틀린 문제</p>
                </div>
                <div className="rounded-xl bg-white p-4">
                  <p className="text-2xl font-extrabold text-blue-600">15개</p>
                  <p className="text-sm text-slate-500">맞은 문제</p>
                </div>
              </div>
            </div>

            <div className="mt-5 rounded-2xl bg-blue-600 p-5 text-white">
              <p className="text-sm font-semibold text-blue-100">
                추천 복습
              </p>
              <p className="mt-1 text-xl font-extrabold">
                네트워크 과목 복습
              </p>
            </div>
          </AnalysisStepCard>
        </div>
      </section>

      {/* 3. AI 해설 섹션 */}
      <section className="flex min-h-screen items-center justify-center bg-gradient-to-br from-blue-50 via-white to-blue-50 px-10 py-24">
        <div className="grid w-full max-w-6xl grid-cols-1 items-center gap-16 lg:grid-cols-2">
          <div>
            <span className="mb-4 inline-block rounded-full bg-purple-100 px-4 py-2 text-sm font-bold text-purple-600">
              AI 해설
            </span>

            <h2 className="mb-6 text-4xl font-extrabold leading-tight">
              해설을 읽어도 모르겠다면,
              <br />
              AI에게 바로 물어보세요
            </h2>

            <p className="mb-8 text-lg leading-8 text-slate-600">
              단순 정답 확인에서 끝나지 않고, 왜 틀렸는지와<br /> 
              어떤 개념을 다시 봐야 하는지
              대화형으로 학습할 수 있습니다.
            </p>

            <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
              <AIPointCard title="오답 이유" desc="왜 틀렸는지 설명" />
              <AIPointCard title="개념 정리" desc="핵심 개념 요약" />
              <AIPointCard title="추가 학습" desc="비슷한 문제 연결" />
            </div>
          </div>

          <div className="rounded-[2rem] border border-purple-100 bg-white p-6 shadow-2xl shadow-blue-100">
            <div className="mb-5 flex items-center gap-3 border-b border-slate-100 pb-4">
              <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-purple-100 font-extrabold text-purple-600">
                AI
              </div>
              <div>
                <p className="font-extrabold text-slate-900">
                  PassMate AI 해설
                </p>
                <p className="text-sm text-slate-400">
                  오답 원인과 핵심 개념을 함께 설명해요
                </p>
              </div>
            </div>

            <div className="space-y-5">
              <div className="flex justify-end">
                <div className="max-w-sm rounded-2xl bg-purple-500 px-5 py-3 text-white">
                  이 선택지가 왜 오답인가요?
                </div>
              </div>

              <div className="max-w-lg rounded-3xl bg-slate-50 p-5">
                <p className="mb-3 text-sm font-bold text-purple-600">
                  AI 해설
                </p>
                <p className="leading-8 text-slate-700">
                  좋은 질문이에요. <br />
                  이 선택지는 문제에서 요구한 조건을 만족하지 못해서
                  오답입니다. <br />
                  정답 선택지는 핵심 개념의 기준을 정확히 포함하고 있어요.
                </p>
              </div>

              <div className="max-w-lg rounded-3xl bg-blue-50 p-5">
                <p className="mb-3 text-sm font-bold text-blue-600">
                  핵심 개념 정리
                </p>
                <ol className="space-y-2 text-slate-700">
                  <li>1. 문제의 조건을 먼저 확인합니다.</li>
                  <li>2. 선택지의 핵심 키워드를 비교합니다.</li>
                  <li>3. 조건과 맞지 않는 선택지를 제거합니다.</li>
                </ol>
              </div>
            </div>
          </div>
        </div>
      </section>

      {isLoginOpen && <LoginModal onClose={() => setIsLoginOpen(false)} />}
    </main>
  )
}

function AnalysisStepCard({
  number,
  title,
  subtitle,
  children,
}: {
  number: string
  title: string
  subtitle: string
  children: React.ReactNode
}) {
  return (
    <div className="rounded-[2rem] border border-blue-100 bg-white p-7 shadow-xl shadow-blue-100">
      <div className="mb-5 flex items-center justify-between">
        <span className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-600 font-extrabold text-white">
          {number}
        </span>

        <span className="rounded-full bg-blue-50 px-4 py-2 text-sm font-bold text-blue-600">
          {subtitle}
        </span>
      </div>

      <h3 className="text-2xl font-extrabold text-slate-900">{title}</h3>

      {children}
    </div>
  )
}

function FlowArrow() {
  return (
    <div className="hidden items-center justify-center lg:flex">
      <span className="text-4xl font-extrabold text-blue-300">›</span>
    </div>
  )
}

function SkeletonLine({ short = false }: { short?: boolean }) {
  return (
    <div
      className={`h-3 rounded-full bg-slate-100 ${short ? 'w-2/3' : 'w-full'}`}
    />
  )
}

function OptionRow({
  label,
  wrong = false,
}: {
  label: string
  wrong?: boolean
}) {
  return (
    <div className="flex items-center gap-3 rounded-xl bg-slate-50 px-3 py-2">
      <span className="flex h-6 w-6 items-center justify-center rounded-full bg-white text-xs font-bold text-slate-500">
        {label}
      </span>
      <div className="h-2 flex-1 rounded-full bg-slate-100" />
      {wrong && <span className="text-sm text-red-400">×</span>}
    </div>
  )
}

function ResultBadge({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex w-28 items-center justify-between rounded-full bg-blue-50 px-4 py-2 text-sm font-bold">
      <span className="text-slate-500">{label}</span>
      <span className="text-blue-600">{value}</span>
    </div>
  )
}

function WeakBar({ label, percent }: { label: string; percent: string }) {
  return (
    <div>
      <div className="mb-2 flex justify-between text-sm font-bold text-slate-600">
        <span>{label}</span>
        <span>{percent}</span>
      </div>
      <div className="h-3 overflow-hidden rounded-full bg-blue-50">
        <div
          className="h-full rounded-full bg-blue-600"
          style={{ width: percent }}
        />
      </div>
    </div>
  )
}

function AIPointCard({ title, desc }: { title: string; desc: string }) {
  return (
    <div className="rounded-2xl border border-purple-100 bg-white p-5 shadow-md shadow-purple-50">
      <h3 className="font-extrabold text-slate-900">{title}</h3>
      <p className="mt-1 text-sm text-slate-500">{desc}</p>
    </div>
  )
}