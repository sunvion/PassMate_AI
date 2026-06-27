'use client'

import { useEffect, useMemo, useState } from 'react'
import { useRouter } from 'next/navigation'

import Header from '../../components/Header'
import Sidebar from '../../components/Sidebar'

import {
  BookOpen,
  CalendarDays,
  ChevronDown,
  NotebookPen,
  Trophy,
  TrendingUp,
} from 'lucide-react'

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'

type ExamOption = {
  label: string
  examType: string
  subject: string
  totalBankQuestions: number
}

type LearnedDomain = {
  exam_type: string
  subject: string
}

type HistoryDetail = {
  id?: number
  attempt_id?: number
  exam_type: string
  year: number
  subject: string
  total_questions: number
  correct_count: number
  score: number
  submitted_at: string
}

type WrongNotebookSummary = {
  id: number
  title: string
  exam_type: string
  year: number | null
  subject: string
  wrong_count: number
  unsolved_count: number
  total_count: number
  created_at: string
}

type LatestProgress = {
  // 이어풀기 API 호출에 필요한 값
  attempt_id: number

  exam_id?: number
  exam_type: string
  subject: string
  year: number | null
  last_question_id: number
  solved_count: number
  total_count?: number
  remaining_count?: number
  progress_percent?: number
  updated_at: string
}

function isDriverLicenseExam(examType?: string) {
  return (
    examType?.startsWith('DRIVERS_LICENSE') ||
    examType?.startsWith('DRIVING_LICENSE')
  )
}

function getTotalBankQuestions(examType: string) {
  if (isDriverLicenseExam(examType)) {
    return 500
  }

  return 140
}

function getExamLabel(examType: string, subject: string) {
  switch (examType) {
    case 'CS_GENERAL':
      return `국가직 9급 ${subject}`
    case 'CS_LOCAL':
      return `지방직 9급 ${subject}`
    case 'DRIVERS_LICENSE_1':
    case 'DRIVERS_LICENSE_2':
      return '운전면허 필기'
    default:
      return `${examType} ${subject}`
  }
}

function getExamTypeLabel(examType: string) {
  switch (examType) {
    case 'CS_GENERAL':
      return '국가직'
    case 'CS_LOCAL':
      return '지방직'
    case 'DRIVERS_LICENSE_1':
    case 'DRIVERS_LICENSE_2':
      return '운전면허 필기'
    default:
      return examType
  }
}

function getDateText(date?: string) {
  if (!date) return '-'
  return date.slice(0, 10)
}

export default function MyPage() {
  const router = useRouter()

  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false)
  const [isSubjectOpen, setIsSubjectOpen] = useState(false)
  const [selectedExamIndex, setSelectedExamIndex] = useState(0)

  const [histories, setHistories] = useState<HistoryDetail[]>([])
  const [wrongNotes, setWrongNotes] = useState<WrongNotebookSummary[]>([])

  // 한 문제씩 학습 진행 상태 목록
  const [latestProgressList, setLatestProgressList] = useState<LatestProgress[]>([])
  const [learnedDomains, setLearnedDomains] = useState<LearnedDomain[]>([])
  const [isLoading, setIsLoading] = useState(true)

  const dynamicExamOptions: ExamOption[] = learnedDomains.map((domain) => ({
    label: getExamLabel(domain.exam_type, domain.subject),
    examType: domain.exam_type,
    subject: domain.subject,
    totalBankQuestions: getTotalBankQuestions(domain.exam_type),
  }))

  const examSelectOptions = dynamicExamOptions
  const selectedExam = examSelectOptions[selectedExamIndex]
  const isSelectedDriverLicense =
    isDriverLicenseExam(selectedExam?.examType)

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setIsLoading(true)

        const token =
          typeof window !== 'undefined' ? localStorage.getItem('token') : null

        const headers = {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        }

        // 마이페이지에서 필요한 데이터 3개를 한 번에 조회
        const [historyRes, wrongNoteRes, progressRes, learnedDomainRes] =
          await Promise.all([
            fetch(`${API_BASE_URL}/api/v1/statistics/history-details`, {
              method: 'GET',
              headers,
              cache: 'no-store',
            }),
            fetch(`${API_BASE_URL}/api/v1/wrong-notebooks`, {
              method: 'GET',
              headers,
              cache: 'no-store',
            }),
            fetch(`${API_BASE_URL}/api/v1/statistics/latest-progress`, {
              method: 'GET',
              headers,
              cache: 'no-store',
            }),
            fetch(`${API_BASE_URL}/api/v1/statistics/learned-domains`, {
              method: 'GET',
              headers,
              cache: 'no-store',
            }),
          ])

        if (historyRes.ok) {
          const historyData = await historyRes.json()
          setHistories(Array.isArray(historyData) ? historyData : [])
        } else {
          setHistories([])
        }

        if (wrongNoteRes.ok) {
          const wrongNoteData = await wrongNoteRes.json()
          setWrongNotes(Array.isArray(wrongNoteData) ? wrongNoteData : [])
        } else {
          setWrongNotes([])
        }

        if (progressRes.ok) {
          const progressData = await progressRes.json()
          setLatestProgressList(Array.isArray(progressData) ? progressData : [])
        } else {
          setLatestProgressList([])
        }

        if (learnedDomainRes.ok) {
          const learnedDomainData = await learnedDomainRes.json()
          setLearnedDomains(Array.isArray(learnedDomainData) ? learnedDomainData : [])
        } else {
          setLearnedDomains([])
        }
      } catch (error) {
        console.warn('학습 통계 데이터 조회 실패:', error)
        setHistories([])
        setWrongNotes([])
        setLatestProgressList([])
        setLearnedDomains([])
      } finally {
        setIsLoading(false)
      }
    }
    fetchDashboardData()
  }, [])

  useEffect(() => {
    if (selectedExamIndex >= examSelectOptions.length) {
      setSelectedExamIndex(0)
    }
  }, [examSelectOptions.length, selectedExamIndex])

  const filteredHistories = useMemo(() => {
    if (!selectedExam) return []
    return histories
      .filter((history) => {
        const examMatched = history.exam_type === selectedExam.examType

        const subjectMatched = isDriverLicenseExam(selectedExam.examType)
          ? true
          : history.subject === selectedExam.subject

        return examMatched && subjectMatched
      })
      .sort((a, b) => {
        const timeA = new Date(a.submitted_at).getTime()
        const timeB = new Date(b.submitted_at).getTime()
        return timeB - timeA
      })
  }, [histories, selectedExam])

  const filteredWrongNotes = useMemo(() => {
    if (!selectedExam) return []

    return wrongNotes
      .filter((note) => {
        const examMatched = note.exam_type === selectedExam.examType

        const subjectMatched = isDriverLicenseExam(selectedExam.examType)
          ? true
          : note.subject === selectedExam.subject

        return examMatched && subjectMatched
      })
      .sort((a, b) => b.created_at.localeCompare(a.created_at))
  }, [wrongNotes, selectedExam])

  const latestHistory = filteredHistories[0]
  const latestAttemptId = latestHistory?.attempt_id ?? latestHistory?.id
  const latestWrongNote = filteredWrongNotes[0]

  const hasStudyData = !!latestHistory

  const selectedProgress = selectedExam
    ? latestProgressList.find(
      (progress) =>
        progress.exam_type === selectedExam.examType &&
        (isSelectedDriverLicense ||
          progress.subject === selectedExam.subject),
    ) ?? null
    : null

  const hasLatestProgress = selectedProgress !== null

  const progressTotalCount =
    selectedProgress?.total_count ?? selectedExam?.totalBankQuestions ?? 20

  const progressSolvedCount = selectedProgress?.solved_count ?? 0

  const progressRemainingCount =
    selectedProgress?.remaining_count ??
    Math.max(progressTotalCount - progressSolvedCount, 0)

  const progressPercent =
    selectedProgress?.progress_percent ??
    (progressTotalCount > 0
      ? Math.round((progressSolvedCount / progressTotalCount) * 100)
      : 0)

  const totalQuestions = latestHistory?.total_questions ?? 20
  const correctCount = latestHistory?.correct_count ?? 0
  const score = latestHistory?.score ?? 0
  const incorrectCount = Math.max(totalQuestions - correctCount, 0)

  const recentHistories = filteredHistories.slice(0, 5)

  const scoreTrend = recentHistories.map((history, index) => ({
    id: `${history.exam_type}-${history.year}-${history.submitted_at}-${index}`,
    label: `${history.year} ${getExamTypeLabel(history.exam_type)}`,
    date: getDateText(history.submitted_at),
    score: history.score,
  }))

  const totalWrong = filteredWrongNotes.reduce(
    (sum, note) => sum + note.wrong_count,
    0,
  )

  const totalUnsolved = filteredWrongNotes.reduce(
    (sum, note) => sum + note.unsolved_count,
    0,
  )

  const totalReviewCount = filteredWrongNotes.reduce(
    (sum, note) => sum + note.total_count,
    0,
  )

  const handleStartSingleStudy = () => {
    if (isSelectedDriverLicense) {
      router.push('/exam/single')
      return
    }

    if (selectedProgress) {
      const params = new URLSearchParams({
        exam_type: selectedProgress.exam_type,
        subject: selectedProgress.subject,

        // 이어풀기 모드 여부
        resume: 'true',

        // 백엔드 resume API 호출에 필요한 id
        attempt_id: String(selectedProgress.attempt_id),

        // 이어서 보여줄 문제 위치
        last_question_id: String(selectedProgress.last_question_id),
      })

      if (selectedProgress.year) {
        params.set('year', String(selectedProgress.year))
      }

      // attempt_id를 solve 페이지로 넘겨서 selected_option을 복원하게 함
      router.push(
        `/exam/single/solve/${selectedProgress.attempt_id}?${params.toString()}`,
      )
      return
    }

    router.push('/exam/single')
  }

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <Header
        onMenuClick={() => setIsMenuOpen(!isMenuOpen)}
        onLoginClick={() => setIsLoginModalOpen(true)}
      />

      <div className="flex">
        <Sidebar isOpen={isMenuOpen} onClose={() => setIsMenuOpen(false)} />

        <section className="mx-auto w-full max-w-6xl px-8 pt-28 pb-10">
          <div className="mb-8 flex items-start justify-between gap-6">
            <div>
              <p className="mb-3 text-sm font-medium text-slate-500">
                마이페이지 <span className="mx-2">›</span>
                <span className="text-slate-900">학습 통계</span>
              </p>

              <h1 className="text-3xl font-black">학습 통계</h1>

              <p className="mt-3 text-slate-500">
                {isLoading
                  ? '학습 데이터를 불러오는 중이에요.'
                  : hasStudyData || hasLatestProgress
                    ? '최근 학습 데이터를 기반으로 분석한 결과입니다.'
                    : '아직 학습 데이터가 없어요. 문제를 풀면 학습 통계가 채워집니다.'}
              </p>
            </div>

            <div className="relative w-[340px]">
              <p className="mb-2 text-sm font-semibold text-slate-500">
                시험 선택
              </p>

              <button
                onClick={() => setIsSubjectOpen(!isSubjectOpen)}
                className="flex w-full items-center justify-between rounded-2xl border border-slate-200 bg-white px-5 py-4 text-left shadow-sm transition hover:border-blue-200 hover:shadow-md"
              >
                <span className="font-bold">
                  {selectedExam?.label ?? '학습한 시험이 없어요'}
                </span>

                <ChevronDown
                  size={20}
                  className={`text-slate-500 transition ${isSubjectOpen ? 'rotate-180' : ''
                    }`}
                />
              </button>

              {isSubjectOpen && (
                <div className="absolute z-20 mt-2 w-full overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-lg">
                  {examSelectOptions.map((exam, index) => (
                    <button
                      key={exam.label}
                      onClick={() => {
                        setSelectedExamIndex(index)
                        setIsSubjectOpen(false)
                      }}
                      className={`w-full px-5 py-4 text-left font-bold transition ${selectedExamIndex === index
                        ? 'bg-blue-50 text-blue-600'
                        : 'hover:bg-slate-50'
                        }`}
                    >
                      {exam.label}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-6">
            <article className="rounded-3xl border border-slate-200 bg-white p-7 shadow-sm">
              <div className="mb-6 flex items-center gap-3">
                <BookOpen className="text-blue-600" />
                <h2 className="text-xl font-black">한 문제씩 학습</h2>
              </div>

              <div className="flex items-center gap-8">
                <div className="relative flex h-40 w-40 items-center justify-center rounded-full bg-blue-50">
                  <div
                    className="absolute inset-0 rounded-full"
                    style={{
                      background: `conic-gradient(#2563eb ${progressPercent}%, #eaf2ff 0)`,
                    }}
                  />
                  <div className="relative flex h-32 w-32 items-center justify-center rounded-full bg-white">
                    <span className="text-4xl font-black">
                      {progressPercent}
                      <span className="text-xl">%</span>
                    </span>
                  </div>
                </div>

                <div className="flex-1">
                  <p className="text-sm font-semibold text-slate-500">
                    {hasLatestProgress
                      ? `${selectedProgress!.year ?? ''} ${getExamTypeLabel(
                        selectedProgress!.exam_type,
                      )} ${selectedProgress!.subject}`
                      : selectedExam?.label ?? '학습 기록 없음'}
                  </p>

                  <p className="mt-2 text-3xl font-black">
                    {hasLatestProgress ? '이어서 학습' : '학습 기록 없음'}
                  </p>

                  <p className="mt-4 text-3xl font-black">
                    {progressSolvedCount}
                    <span className="ml-1 text-lg text-slate-500">
                      / {progressTotalCount} 문제
                    </span>
                  </p>

                  <div className="mt-5 flex gap-5 text-sm font-bold">
                    <span className="text-blue-600">
                      푼 문제 {progressSolvedCount}
                    </span>
                    <span className="text-slate-300">|</span>
                    <span className="text-red-500">
                      안 푼 문제 {progressRemainingCount}
                    </span>
                  </div>
                </div>
              </div>

              <div className="mt-6 flex items-center justify-between rounded-2xl bg-blue-50 px-5 py-4">
                <div>
                  {isSelectedDriverLicense ? (
                    <p className="font-bold">
                      매번 새로운 랜덤 40문제로 학습합니다.
                    </p>
                  ) : hasLatestProgress ? (
                    <>
                      <p className="mt-1 text-sm font-semibold text-slate-500">
                        최근 학습일
                      </p>
                      <p className="font-bold">
                        {getDateText(selectedProgress.updated_at)}
                      </p>
                    </>
                  ) : (
                    <p className="font-bold">
                      아직 저장된 학습 위치가 없습니다.
                    </p>
                  )}
                </div>

                <button
                  onClick={handleStartSingleStudy}
                  className="rounded-xl bg-blue-600 px-6 py-3 font-bold text-white transition hover:bg-blue-700"
                >
                  {isSelectedDriverLicense
                    ? '랜덤 40문제 다시 시작 →'
                    : hasLatestProgress
                      ? '이어서 하기 →'
                      : '한 문제씩 학습하기 →'}
                </button>
              </div>
            </article>

            <article className="rounded-3xl border border-emerald-100 bg-white p-7 shadow-sm">
              <div className="mb-6 flex items-center gap-3">
                <Trophy className="text-emerald-600" />
                <h2 className="text-xl font-black">최근 응시 결과</h2>
              </div>

              <div className="flex items-center gap-8">
                <div className="relative flex h-40 w-40 items-center justify-center rounded-full bg-emerald-50">
                  <div
                    className="absolute inset-0 rounded-full"
                    style={{
                      background: `conic-gradient(#10b981 ${score}%, #e8f8f1 0)`,
                    }}
                  />
                  <div className="relative flex h-32 w-32 items-center justify-center rounded-full bg-white">
                    <span className="text-4xl font-black">
                      {score}
                      <span className="text-xl">점</span>
                    </span>
                  </div>
                </div>

                <div className="flex-1">
                  <p className="text-xl font-black">
                    {hasStudyData
                      ? `${latestHistory.year} ${getExamTypeLabel(
                        latestHistory.exam_type,
                      )} 9급 ${latestHistory.subject}`
                      : '최근 응시 기록이 없어요'}
                  </p>

                  <p className="mt-4 text-3xl font-black">
                    {correctCount}
                    <span className="ml-1 text-lg text-slate-500">
                      / {totalQuestions} 문제
                    </span>
                  </p>

                  <div className="mt-5 flex gap-5 text-sm font-bold">
                    <span className="text-emerald-600">
                      맞은 문제 {correctCount}
                    </span>
                    <span className="text-slate-300">|</span>
                    <span className="text-red-500">
                      틀림/미풀이 {incorrectCount}
                    </span>
                  </div>
                </div>
              </div>

              <div className="mt-6 flex items-center justify-between rounded-2xl bg-emerald-50 px-5 py-4">
                <div className="flex items-center gap-3">
                  <CalendarDays className="text-emerald-600" />
                  <div>
                    <p className="text-sm font-semibold text-slate-500">
                      응시일
                    </p>
                    <p className="font-bold">
                      {hasStudyData
                        ? getDateText(latestHistory.submitted_at)
                        : '아직 없음'}
                    </p>
                  </div>
                </div>

                <button
                  onClick={() => {
                    if (latestAttemptId) {
                      router.push(`/exam/result/${latestAttemptId}`)
                      return
                    }

                    router.push('/wrong-note')
                  }}
                  className="rounded-xl bg-emerald-600 px-6 py-3 font-bold text-white transition hover:bg-emerald-700"
                >
                  결과 상세 보기 →
                </button>
              </div>
            </article>
          </div>

          <div className="mt-6 grid grid-cols-2 gap-6">
            <article className="rounded-3xl border border-slate-200 bg-white p-7 shadow-sm">
              <div className="mb-6 flex items-center gap-3">
                <TrendingUp className="text-blue-600" />
                <h2 className="text-xl font-black">최근 5회 점수 변화</h2>
              </div>

              {hasStudyData ? (
                <div className="space-y-4">
                  {scoreTrend.map((item) => (
                    <div key={item.id}>
                      <div className="mb-2 flex items-center justify-between text-sm font-bold">
                        <span>{item.label}</span>
                        <span
                          className={
                            item.score >= 70 ? 'text-blue-600' : 'text-red-500'
                          }
                        >
                          {item.score}점
                        </span>
                      </div>

                      <div className="h-4 rounded-full bg-slate-100">
                        <div
                          className={`h-4 rounded-full ${item.score >= 70 ? 'bg-blue-600' : 'bg-red-400'
                            }`}
                          style={{ width: `${item.score}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="flex h-64 items-center justify-center rounded-2xl bg-slate-50 text-center">
                  <div>
                    <p className="text-lg font-black">
                      점수 변화 데이터가 없어요
                    </p>
                    <p className="mt-2 text-sm text-slate-500">
                      시험을 풀면 최근 5회 점수 추이가 표시됩니다.
                    </p>
                  </div>
                </div>
              )}
            </article>

            <article className="rounded-3xl border border-slate-200 bg-white p-7 shadow-sm">
              <div className="mb-6 flex items-center gap-3">
                <NotebookPen className="text-violet-600" />
                <h2 className="text-xl font-black">오답노트 현황</h2>
              </div>

              <div className="rounded-2xl bg-violet-50 p-6">
                <div className="flex items-center gap-5">
                  <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-2xl bg-white text-violet-600">
                    <NotebookPen size={34} />
                  </div>

                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-semibold text-slate-500">
                      복습 대상 문제
                    </p>

                    <p className="mt-1 text-4xl font-black">
                      {totalReviewCount}
                      <span className="ml-1 text-xl">개</span>
                    </p>

                    <div className="mt-3 flex gap-3 text-sm font-bold">
                      <span className="text-red-500">오답 {totalWrong}</span>
                      <span className="text-slate-300">|</span>
                      <span className="text-orange-500">
                        미풀이 {totalUnsolved}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="mt-5 rounded-xl bg-white/70 px-4 py-3">
                  <p className="text-sm font-semibold text-slate-500">
                    최근 오답노트
                  </p>
                  <p className="mt-1 truncate font-black">
                    {latestWrongNote ? latestWrongNote.title : '아직 없음'}
                  </p>
                </div>
              </div>

              <div className="mt-5 rounded-2xl border border-slate-200 p-6">
                <p className="mb-4 font-black">최근 추가된 오답노트</p>

                {filteredWrongNotes.length > 0 ? (
                  <div className="space-y-3">
                    {filteredWrongNotes.slice(0, 2).map((note) => (
                      <button
                        key={note.id}
                        onClick={() => router.push(`/wrong-note/${note.id}`)}
                        className="flex w-full items-center justify-between gap-3 rounded-xl bg-slate-50 px-4 py-3 text-left text-sm transition hover:bg-violet-50"
                      >
                        <span className="shrink-0 text-slate-500">
                          {getDateText(note.created_at)}
                        </span>

                        <span className="min-w-0 flex-1 truncate font-bold">
                          {note.title}
                        </span>

                        <span className="shrink-0 font-black text-red-500">
                          {note.total_count}문제
                        </span>
                      </button>
                    ))}
                  </div>
                ) : (
                  <div className="flex h-36 items-center justify-center text-center text-sm text-slate-500">
                    틀린 문제나 미풀이 문제가 있으면
                    <br />
                    오답노트가 자동 생성됩니다.
                  </div>
                )}
              </div>

              <div className="mt-6">
                <button
                  onClick={() => router.push('/wrong-note')}
                  className="w-full rounded-2xl border border-violet-300 py-4 font-black text-violet-600 transition hover:bg-violet-50"
                >
                  전체 오답노트 보기 →
                </button>
              </div>
            </article>
          </div>
        </section>
      </div>
    </main>
  )
}