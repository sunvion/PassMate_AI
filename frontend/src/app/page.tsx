'use client'

import { useEffect, useRef, useState } from 'react'
import Image from 'next/image'

import Header from '../components/Header'
import Sidebar from '../components/Sidebar'
import LoginModal from '../components/LoginModal'
import { Send } from "lucide-react";

export default function HomePage() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [isLoginOpen, setIsLoginOpen] = useState(false)
  const [isLoggedIn, setIsLoggedIn] = useState(false)

  // 마우스를 천천히 따라오는 배경 블러
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 })
  const [smoothPosition, setSmoothPosition] = useState({ x: 0, y: 0 })

  // 눈 깜빡임 애니메이션
  const [isBlinking, setIsBlinking] = useState(false)

  // AI 해설 애니메이션
  const aiAnswer =
    '문제 6번의 답은 ②번입니다.\n\n10진수 29를 2진수로 바꾸면 11101입니다.\n\n여기서 2비트만큼 오른쪽으로 이동하면 00111이 되고,\n이를 다시 10진수로 변환하면 7입니다.\n\n따라서 정답은 ②번입니다.'
  const [typedAnswer, setTypedAnswer] = useState('')

  useEffect(() => {
    const token = localStorage.getItem('token')
    setIsLoggedIn(!!token)
  }, [])

  // 마우스 위치를 저장
  useEffect(() => {
    const handleMouseMove = (event: MouseEvent) => {
      setMousePosition({
        x: event.clientX,
        y: event.clientY,
      })
    }

    window.addEventListener('mousemove', handleMouseMove)

    return () => {
      window.removeEventListener('mousemove', handleMouseMove)
    }
  }, [])

  // 블러가 마우스를 바로 따라가지 않고 부드럽게 따라오도록 처리
  useEffect(() => {
    let animationFrameId: number

    const animate = () => {
      setSmoothPosition((prev) => ({
        x: prev.x + (mousePosition.x - prev.x) * 0.08,
        y: prev.y + (mousePosition.y - prev.y) * 0.08,
      }))

      animationFrameId = requestAnimationFrame(animate)
    }

    animationFrameId = requestAnimationFrame(animate)

    return () => {
      cancelAnimationFrame(animationFrameId)
    }
  }, [mousePosition])

  // 눈 깜빡임 애니메이션
  useEffect(() => {
    let timer: NodeJS.Timeout

    const blink = () => {
      setIsBlinking(true)

      setTimeout(() => {
        setIsBlinking(false)
      }, 180)

      timer = setTimeout(blink, 1400 + Math.random() * 1200)
    }

    timer = setTimeout(blink, 2000)

    return () => clearTimeout(timer)
  }, [])

  const typingIntervalRef = useRef<NodeJS.Timeout | null>(null)
  const aiSectionRef = useRef<HTMLDivElement | null>(null)

  // 시험 결과 애니메이션 추가
  const analysisSectionRef = useRef<HTMLDivElement | null>(null)
  const [isAnalysisVisible, setIsAnalysisVisible] = useState(false)

  useEffect(() => {
    const startTyping = () => {
      if (typingIntervalRef.current) {
        clearInterval(typingIntervalRef.current)
      }

      let index = 0
      setTypedAnswer('')

      typingIntervalRef.current = setInterval(() => {
        setTypedAnswer(aiAnswer.slice(0, index + 1))
        index += 1

        if (index >= aiAnswer.length && typingIntervalRef.current) {
          clearInterval(typingIntervalRef.current)
        }
      }, 35)
    }

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          startTyping()
        }
      },
      {
        threshold: 0.45,
      }
    )

    if (aiSectionRef.current) {
      observer.observe(aiSectionRef.current)
    }

    return () => {
      observer.disconnect()

      if (typingIntervalRef.current) {
        clearInterval(typingIntervalRef.current)
      }
    }
  }, [aiAnswer])

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsAnalysisVisible(true)
        } else {
          setIsAnalysisVisible(false)
        }
      },
      {
        threshold: 0.35,
      }
    )

    if (analysisSectionRef.current) {
      observer.observe(analysisSectionRef.current)
    }

    return () => observer.disconnect()
  }, [])

  return (
    <main className="relative min-h-screen overflow-x-hidden bg-white text-slate-900">
      {/* 마우스를 따라오는 블러 배경 */}
      <div
        className="
    pointer-events-none
    fixed
    z-0
    h-[620px]
    w-[620px]
    rounded-full
    bg-blue-400/15
    blur-[120px]
  "
        style={{
          left: smoothPosition.x - 310,
          top: smoothPosition.y - 310,
        }}
      />
      <div className="relative z-30 bg-white shadow-sm">
        <Header
          onMenuClick={() => setIsMenuOpen(!isMenuOpen)}
          onLoginClick={() => setIsLoginOpen(true)}
        />
      </div>

      <div className="relative z-20">
        <Sidebar isOpen={isMenuOpen} onClose={() => setIsMenuOpen(false)} />
      </div>

      {/* 1. 메인 소개 섹션 */}
      <section
        id="start-section"
        className="relative z-10 flex min-h-screen items-center justify-center bg-transparent px-10 pt-16"
      >
        <div className="grid w-full max-w-6xl grid-cols-1 items-center gap-10 lg:grid-cols-2">
          <div className="mx-auto max-w-xl lg:ml-20">
            <h1 className="mb-6 text-5xl font-extrabold leading-tight">
              <span className="text-blue-600">AI와 함께</span>
              <br />
              합격을 설계하는
              <br />
              <span className="text-blue-600">나만의 학습 파트너</span>
            </h1>

            <p className="mb-8 text-lg leading-8 text-slate-600">
              PassMate는 기출 분석과 AI 기술을 통해
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

          <div className="flex -translate-x-6 translate-y-2 justify-center">
            <Image
              src={
                isBlinking
                  ? "/images/homepage_main_close.png"
                  : "/images/homepage_main.png"
              }
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
      <section
        ref={analysisSectionRef}
        className="relative z-10 flex min-h-screen flex-col items-center justify-center bg-transparent px-10 py-24"
      >
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
            subtitle="2026 국가직 9급"
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
                    strokeDashoffset={isAnalysisVisible ? 327 - (327 * 75) / 100 : 327}
                    className="transition-[stroke-dashoffset] duration-[1400ms] ease-out"
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

            <div className="mt-7 rounded-2xl bg-blue-50 px-5 py-4">
              <div className="mb-3 flex items-center justify-between">
                <p className="text-sm font-black text-slate-700">최근 점수 추세</p>
                <p className="text-xs font-bold text-blue-600">72점 → 82점</p>
              </div>

              <svg viewBox="0 0 320 95" className="h-24 w-full overflow-visible">
                <polyline
                  points="20,68 95,55 170,42 245,32 300,24"
                  fill="none"
                  stroke="#2563eb"
                  strokeWidth="4"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeDasharray={isAnalysisVisible ? 420 : 0}
                  strokeDashoffset={isAnalysisVisible ? 0 : 420}
                  className="transition-[stroke-dashoffset] duration-[1600ms] ease-out"
                />

                {[
                  { x: 20, y: 68, score: 45 },
                  { x: 95, y: 55, score: 58 },
                  { x: 170, y: 42, score: 64 },
                  { x: 245, y: 32, score: 75 },
                  { x: 300, y: 24, score: 82 },
                ].map((point, index) => (
                  <g
                    key={point.score}
                    className={`transition-all duration-500 ${isAnalysisVisible ? 'opacity-100 scale-100' : 'opacity-0 scale-75'
                      }`}
                    style={{
                      transitionDelay: `${500 + index * 250}ms`,
                      transformOrigin: `${point.x}px ${point.y}px`,
                    }}
                  >
                    <circle cx={point.x} cy={point.y} r="5" fill="#2563eb" />
                    <circle
                      cx={point.x}
                      cy={point.y}
                      r="9"
                      fill="#2563eb"
                      opacity="0.15"
                    />

                    <text
                      x={point.x}
                      y={point.y - 10}
                      textAnchor="middle"
                      className="fill-blue-700 text-[10px] font-black"
                    >
                      {point.score}
                    </text>
                  </g>
                ))}
              </svg>
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
                2026 컴퓨터일반 오답
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
              <button
                className="mt-10 w-full rounded-2xl bg-blue-600 p-5 text-left text-xl font-extrabold text-white"
              >
                AI 에게 질문하기 →
              </button>
            </div>
          </AnalysisStepCard>
        </div>
      </section>

      {/* 3. AI 해설 섹션 */}
      <section
        ref={aiSectionRef}
        className="relative z-10 flex min-h-screen items-center justify-center bg-transparent px-10 py-24"
      >
        <div className="grid w-full max-w-6xl grid-cols-1 items-center gap-16 lg:grid-cols-2">
          <div>
            <span className="mb-4 inline-block rounded-full bg-purple-100 px-4 py-2 text-sm font-bold text-purple-600">
              AI 해설
            </span>

            <h2 className="mb-6 text-4xl font-extrabold leading-tight">
              틀린 이유를 모르겠다면,
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
            </div>
          </div>

          <div className="rounded-[2rem] border border-blue-100 bg-white p-6 shadow-2xl shadow-blue-100">
            <div className="mb-5 flex items-center gap-3 border-b border-slate-100 pb-4">
              <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-blue-100 font-extrabold text-blue-600">
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
                <div className="max-w-sm rounded-3xl bg-blue-600 px-5 py-3 text-white shadow-lg">
                  6번 문제 답 해설해줘
                </div>
              </div>

              <div className="h-[260px] max-w-lg rounded-3xl bg-slate-50 p-5">
                <p className="mb-3 text-sm font-bold text-blue-600">
                  AI 해설
                </p>

                <div className="h-[190px] overflow-hidden">
                  <p className="whitespace-pre-line text-sm leading-8 text-slate-700">
                    {typedAnswer}
                    {typedAnswer.length < aiAnswer.length && (
                      <span className="ml-1 animate-pulse text-blue-500">|</span>
                    )}
                  </p>
                </div>
              </div>

              <div className="mt-6 flex items-center gap-3 rounded-2xl border border-slate-200 bg-white p-3">
                <input
                  type="text"
                  placeholder="질문을 입력하세요..."
                  className="flex-1 bg-transparent px-3 py-2 text-sm outline-none placeholder:text-slate-400"
                  readOnly
                />

                <button className="flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-600 text-white hover:bg-blue-700 transition">
                  <Send size={17} />
                </button>
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