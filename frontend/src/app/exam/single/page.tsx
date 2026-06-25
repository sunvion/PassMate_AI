'use client'

import { useEffect, useMemo, useState } from 'react'
import { useRouter } from 'next/navigation'

import Header from '@/components/Header'
import Sidebar from '@/components/Sidebar'

import {
  BookOpen,
  Code2,
  Loader2,
  Search,
  ShieldCheck,
  TrafficCone,
  X,
} from 'lucide-react'

import {
  getSingleStudyExams,
  SingleStudyExam,
} from '@/lib/singleStudyApi'

const colorMap = {
  blue: 'bg-blue-50 text-blue-600',
  green: 'bg-emerald-50 text-emerald-600',
  orange: 'bg-orange-50 text-orange-600',
}

const examIconMap = {
  CS_GENERAL: Code2,
  CS_LOCAL: BookOpen,
  DRIVERS_LICENSE_1: TrafficCone,
  DRIVERS_LICENSE_2: ShieldCheck,
}

// 화면 카드에서 사용할 데이터 형태
type ExamCard = {
  id: string
  name: string
  examType: string
  subject: string
  years: string[]
  totalQuestionCount: number
}

// 시험 종류별 아이콘 반환
function getExamIcon(examType: string) {
  return examIconMap[examType as keyof typeof examIconMap] ?? BookOpen
}

// 시험 종류별 카드 색상 반환
function getExamColor(examType: string) {
  switch (examType) {
    case 'CS_GENERAL':
      return colorMap.blue
    case 'CS_LOCAL':
      return colorMap.green
    case 'DRIVERS_LICENSE_1':
    case 'DRIVERS_LICENSE_2':
      return colorMap.orange
    default:
      return colorMap.blue
  }
}

// 운전면허는 화면에 보여줄 과목명을 고정
function getExamSubjectName(exam: SingleStudyExam) {
  if (
    exam.examType === 'DRIVERS_LICENSE_1' ||
    exam.examType === 'DRIVERS_LICENSE_2'
  ) {
    return '운전면허 필기 기출'
  }

  return exam.subjects[0]?.name ?? ''
}

// 시험별 전체 문제 수 계산
function getExamTotalQuestionCount(exam: SingleStudyExam) {
  return exam.subjects.reduce((subjectSum, subject) => {
    return subjectSum + subject.totalQuestionCount
  }, 0)
}

// 국가직/지방직 회차 연도 목록 추출
function getExamYears(exam: SingleStudyExam) {
  const years = exam.subjects.flatMap((subject) => subject.years)

  return Array.from(new Set(years)).sort((a, b) => Number(b) - Number(a))
}

// 운전면허 필기 여부 확인
function isDriverLicense(examType: string) {
  return examType.startsWith('DRIVERS_LICENSE')
}

export default function OneQuestionPage() {
  const router = useRouter()

  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [studyExams, setStudyExams] = useState<SingleStudyExam[]>([])
  const [selectedExam, setSelectedExam] = useState<ExamCard | null>(null)
  const [searchText, setSearchText] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [errorMessage, setErrorMessage] = useState('')

  // 한 문제씩 학습 가능한 시험 목록 조회
  useEffect(() => {
    async function fetchStudyExams() {
      try {
        setIsLoading(true)
        setErrorMessage('')

        const data = await Promise.race([
          getSingleStudyExams(),
          new Promise<never>((_, reject) =>
            setTimeout(
              () => reject(new Error('API 요청 시간이 초과됐어요.')),
              8000,
            ),
          ),
        ])

        if (!Array.isArray(data)) {
          throw new Error('API 응답이 배열 형태가 아니에요.')
        }

        setStudyExams(data)
      } catch (error) {
        console.error('한 문제씩 학습 데이터 조회 실패:', error)
        setErrorMessage('한 문제씩 학습 데이터를 불러오지 못했어요.')
      } finally {
        setIsLoading(false)
      }
    }

    fetchStudyExams()
  }, [])

  // API 응답 데이터를 카드 UI에서 쓰기 좋은 형태로 변환
  const examCards = useMemo<ExamCard[]>(() => {
    return studyExams.map((exam) => ({
      id: exam.id,
      name: exam.name,
      examType: exam.examType,
      subject: getExamSubjectName(exam),
      years: getExamYears(exam),
      totalQuestionCount: getExamTotalQuestionCount(exam),
    }))
  }, [studyExams])

  // 검색어 기준으로 시험 카드 필터링
  const filteredExamCards = useMemo(() => {
    const keyword = searchText.trim().toLowerCase()

    if (!keyword) return examCards

    return examCards.filter((exam) => {
      return (
        exam.name.toLowerCase().includes(keyword) ||
        exam.subject.toLowerCase().includes(keyword) ||
        exam.years.some((year) => year.includes(keyword))
      )
    })
  }, [examCards, searchText])

  // 카드 클릭 시 동작
  // 운전면허: 바로 랜덤 40문제 풀이로 이동
  // 국가직/지방직: 연도 선택 모달 열기
  const handleExamClick = (exam: ExamCard) => {
    if (isDriverLicense(exam.examType)) {
      handleStartStudy(exam)
      return
    }

    setSelectedExam(exam)
  }

  // 실제 풀이 페이지로 이동
  // 국가직/지방직은 year 포함
  // 운전면허는 limit=40, random=true 포함
  const handleStartStudy = (exam: ExamCard, year?: string) => {
    const params = new URLSearchParams({
      exam_type: exam.examType,
      subject: exam.subject,
    })

    if (isDriverLicense(exam.examType)) {
      params.append('limit', '40')
      params.append('random', 'true')
    } else if (year) {
      params.append('year', year)
    }

    router.push(`/exam/single/solve/${exam.id}?${params.toString()}`)
  }

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <Header
        onMenuClick={() => setIsMenuOpen(true)}
        onLoginClick={() => { }}
      />

      <Sidebar isOpen={isMenuOpen} onClose={() => setIsMenuOpen(false)} />

      <section className="mx-auto w-full max-w-6xl px-8 pb-12 pt-28">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <p className="mb-3 text-sm font-medium text-slate-500">
              기출문제 <span className="mx-2">›</span>
              <span className="text-slate-900">한 문제씩 학습</span>
            </p>

            <h1 className="text-3xl font-bold">한 문제씩 학습</h1>
            <p className="mt-2 text-slate-500">
              국가직·지방직은 회차별로, 운전면허 필기는 랜덤 40문제로
              학습할 수 있어요.
            </p>
          </div>

          <button
            onClick={() => router.push('/mypage')}
            className="rounded-xl border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-700 shadow-sm transition hover:border-blue-300 hover:text-blue-600"
          >
            학습 통계
          </button>
        </div>

        <div className="mb-6 flex items-center gap-3 rounded-2xl border border-slate-200 bg-white px-5 py-4 shadow-sm">
          <Search size={20} className="text-slate-400" />
          <input
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            placeholder="시험명, 과목명, 연도를 검색해보세요."
            className="w-full bg-transparent text-sm outline-none placeholder:text-slate-400"
          />
        </div>

        {isLoading && (
          <div className="rounded-3xl border border-slate-200 bg-white p-12 text-center shadow-sm">
            <Loader2
              className="mx-auto mb-4 animate-spin text-blue-600"
              size={36}
            />
            <p className="font-bold text-slate-700">
              실제 문제 데이터를 불러오는 중이에요.
            </p>
            <p className="mt-2 text-sm text-slate-500">
              등록된 시험별 전체 문제를 확인하고 있어요.
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

        {!isLoading && !errorMessage && (
          <section className="grid grid-cols-1 gap-5 lg:grid-cols-3">
            {filteredExamCards.map((exam) => {
              const Icon = getExamIcon(exam.examType)

              return (
                <button
                  key={exam.id}
                  onClick={() => handleExamClick(exam)}
                  className="group rounded-3xl border border-slate-200 bg-white p-6 text-left shadow-sm transition duration-300 hover:-translate-y-1 hover:border-blue-300 hover:shadow-md"
                >
                  <div
                    className={`mb-6 flex h-20 w-20 items-center justify-center rounded-2xl transition duration-300 group-hover:scale-105 ${getExamColor(
                      exam.examType,
                    )}`}
                  >
                    <Icon size={34} />
                  </div>

                  <h2 className="text-xl font-bold">
                    {isDriverLicense(exam.examType) ? '운전면허 필기' : exam.name}
                  </h2>

                  <p className="mt-2 text-sm text-slate-500">
                    {exam.subject}
                  </p>

                  <p className="mt-1 text-sm text-slate-500">
                    {isDriverLicense(exam.examType)
                      ? '랜덤 40문제'
                      : exam.years.length > 0
                        ? `${exam.years.join(', ')}년 기출`
                        : '등록된 연도 정보 없음'}
                  </p>

                  <div className="mt-6 flex items-center justify-between rounded-2xl bg-slate-50 px-4 py-3">
                    <span className="text-sm font-semibold text-slate-500">
                      {isDriverLicense(exam.examType)
                        ? '학습 문제'
                        : '전체 문제'}
                    </span>
                    <span className="font-black text-blue-600">
                      {isDriverLicense(exam.examType)
                        ? '40문제'
                        : `${exam.totalQuestionCount}문제`}
                    </span>
                  </div>

                  <span className="mt-5 inline-flex rounded-xl border border-blue-200 px-5 py-3 text-sm font-bold text-blue-600 transition group-hover:bg-blue-600 group-hover:text-white">
                    {isDriverLicense(exam.examType)
                      ? '랜덤 40문제 풀기'
                      : '회차 선택하기'}
                  </span>
                </button>
              )
            })}

            {filteredExamCards.length === 0 && (
              <div className="col-span-full rounded-3xl border border-slate-200 bg-white p-10 text-center shadow-sm">
                <p className="font-bold text-slate-700">검색 결과가 없어요.</p>
                <p className="mt-2 text-sm text-slate-500">
                  다른 시험명, 과목명, 연도로 검색해보세요.
                </p>
              </div>
            )}
          </section>
        )}
      </section>

      {selectedExam && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/30 px-4">
          <div className="w-full max-w-md animate-[modalUp_0.25s_ease-out] rounded-3xl bg-white p-7 shadow-2xl">
            <div className="mb-6 flex items-start justify-between">
              <div>
                <h2 className="text-xl font-bold">{selectedExam.name}</h2>
                <p className="mt-1 text-sm text-slate-500">
                  한 문제씩 풀 회차를 선택해주세요.
                </p>
              </div>

              <button
                onClick={() => setSelectedExam(null)}
                className="rounded-full p-2 text-slate-400 transition hover:bg-slate-100 hover:text-slate-700"
              >
                <X size={22} />
              </button>
            </div>

            {selectedExam.years.length > 0 ? (
              <div className="grid grid-cols-2 gap-3">
                {selectedExam.years.map((year) => (
                  <button
                    key={year}
                    onClick={() => handleStartStudy(selectedExam, year)}
                    className="rounded-2xl border border-slate-200 bg-slate-50 px-5 py-4 text-left font-bold text-slate-800 transition hover:border-blue-300 hover:bg-blue-50 hover:text-blue-600"
                  >
                    {year}년
                  </button>
                ))}
              </div>
            ) : (
              <div className="rounded-2xl bg-slate-50 p-5 text-center">
                <p className="font-bold text-slate-700">
                  등록된 회차가 없어요.
                </p>
                <p className="mt-2 text-sm text-slate-500">
                  백엔드 문제 데이터의 연도 정보를 확인해주세요.
                </p>
              </div>
            )}
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
  )
}