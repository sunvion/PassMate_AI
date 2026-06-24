"use client";

import Header from "@/components/Header";
import Sidebar from "@/components/Sidebar";
import { getWrongNotebookSummary, WrongNoteSummary } from "@/lib/wrongNoteApi";
import { BookOpen, ChevronRight } from "lucide-react";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

function getExamTypeLabel(examType: string) {
    switch (examType) {
        case "CS_GENERAL":
            return "국가직";
        case "CS_LOCAL":
            return "지방직";
        case "DRIVERS_LICENSE_1":
        case "DRIVERS_LICENSE_2":
            return "운전면허 필기";
        default:
            return examType;
    }
}

function isDriverLicense(examType: string) {
    return examType.startsWith("DRIVERS_LICENSE");
}

function getWrongNoteTitle(note: WrongNoteSummary) {
    const examLabel = getExamTypeLabel(note.exam_type);

    if (isDriverLicense(note.exam_type)) {
        return `${examLabel} 오답노트`;
    }

    return `${note.year} ${examLabel} ${note.subject} 오답노트`;
}

export default function WrongNotePage() {
    const router = useRouter();

    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const [wrongNotes, setWrongNotes] = useState<WrongNoteSummary[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        async function fetchWrongNotes() {
            try {
                const data = await getWrongNotebookSummary();
                setWrongNotes(data);
            } catch (error) {
                console.error(error);
            } finally {
                setIsLoading(false);
            }
        }

        fetchWrongNotes();
    }, []);

    const handleClickNote = (note: WrongNoteSummary) => {
        const params = new URLSearchParams({
            exam_type: note.exam_type,
            subject: note.subject,
        });

        if (note.year !== null) {
            params.set("year", String(note.year));
        }

        router.push(`/wrong-note/detail?${params.toString()}`);
    };

    return (
        <main className="min-h-screen bg-slate-50">
            <Header
                onMenuClick={() => setIsMenuOpen(true)}
                onLoginClick={() => { }}
            />
            <Sidebar isOpen={isMenuOpen} onClose={() => setIsMenuOpen(false)} />

            <section className="mx-auto max-w-6xl px-8 pt-28 pb-10">
                <div className="mb-8 flex items-start justify-between">
                    <div>
                        <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-slate-500">
                            <span>마이페이지</span>
                            <span>›</span>
                            <span className="text-slate-900">오답노트</span>
                        </div>

                        <h1 className="text-3xl font-bold text-slate-900">오답노트</h1>
                        <p className="mt-2 text-slate-500">
                            전체 회차 풀이에서 틀린 문제와 안 푼 문제를 모아 복습해보세요.
                        </p>
                    </div>
                </div>

                <div className="rounded-2xl border border-slate-200 bg-white p-6">
                    <div className="mb-6 flex items-center gap-2">
                        <BookOpen className="text-blue-600" size={22} />
                        <h2 className="text-xl font-bold text-slate-900">오답노트 목록</h2>
                    </div>

                    {isLoading ? (
                        <p className="py-10 text-center text-slate-500">
                            오답노트를 불러오는 중...
                        </p>
                    ) : wrongNotes.length === 0 ? (
                        <div className="rounded-2xl border border-dashed border-slate-300 py-14 text-center">
                            <p className="text-lg font-bold text-slate-700">
                                아직 생성된 오답노트가 없어요.
                            </p>
                            <p className="mt-2 text-slate-500">
                                전체 회차 문제를 제출하면 틀린 문제가 자동으로 저장됩니다.
                            </p>
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
                            {wrongNotes.map((note) => {
                                const title = getWrongNoteTitle(note);

                                return (
                                    <button
                                        key={`${note.exam_type}-${note.year}-${note.subject}`}
                                        onClick={() => handleClickNote(note)}
                                        className="group rounded-2xl border border-slate-200 bg-white p-6 text-left transition hover:border-blue-500 hover:shadow-md"
                                    >
                                        <div className="mb-8 flex items-start justify-between">
                                            <div>
                                                <div className="mb-3 flex items-center gap-2">
                                                    <h3 className="text-lg font-bold text-slate-900">
                                                        {title}
                                                    </h3>
                                                    <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-600">
                                                        전체 회차
                                                    </span>
                                                </div>

                                                <p className="text-sm text-slate-500">
                                                    {isDriverLicense(note.exam_type)
                                                        ? "운전면허 필기"
                                                        : `${getExamTypeLabel(note.exam_type)} · ${note.subject}`}
                                                </p>
                                            </div>

                                            <ChevronRight
                                                size={22}
                                                className="text-slate-400 transition group-hover:translate-x-1 group-hover:text-blue-600"
                                            />
                                        </div>

                                        <div className="mb-5 grid grid-cols-2 gap-3 text-sm">
                                            <div>
                                                <p className="text-slate-400">오답 문제</p>
                                                <p className="mt-1 font-bold text-red-500">
                                                    {note.wrong_count}개
                                                </p>
                                            </div>

                                            <div>
                                                <p className="text-slate-400">
                                                    {isDriverLicense(note.exam_type) ? "구분" : "연도"}
                                                </p>
                                                <p className="mt-1 font-semibold text-slate-700">
                                                    {isDriverLicense(note.exam_type) ? "상시" : note.year}
                                                </p>
                                            </div>
                                        </div>

                                        <p className="mt-4 text-sm text-slate-400">
                                            총 {note.wrong_count}문제
                                        </p>
                                    </button>
                                );
                            })}
                        </div>
                    )}
                </div>
            </section>
        </main>
    );
}