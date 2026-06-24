"use client";

import Header from "@/components/Header";
import Sidebar from "@/components/Sidebar";
import {
    deleteWrongNotebook,
    getWrongNotebookSummary,
    WrongNoteSummary,
} from "@/lib/wrongNoteApi";
import { BookOpen, ChevronRight, Trash2, X } from "lucide-react";
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
    const [deletingId, setDeletingId] = useState<number | null>(null);
    const [deleteTarget, setDeleteTarget] = useState<WrongNoteSummary | null>(
        null
    );

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
        router.push(`/wrong-note/${note.id}`);
    };

    const openDeleteModal = (
        e: React.MouseEvent<HTMLButtonElement>,
        note: WrongNoteSummary
    ) => {
        e.stopPropagation();
        setDeleteTarget(note);
    };

    const closeDeleteModal = () => {
        if (deletingId !== null) return;
        setDeleteTarget(null);
    };

    const handleDeleteNote = async () => {
        if (!deleteTarget) return;

        try {
            setDeletingId(deleteTarget.id);

            await deleteWrongNotebook(deleteTarget.id);

            setWrongNotes((prev) =>
                prev.filter((note) => note.id !== deleteTarget.id)
            );
            setDeleteTarget(null);
        } catch (error) {
            console.error(error);
            alert("오답노트 삭제 중 오류가 발생했습니다.");
        } finally {
            setDeletingId(null);
        }
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
                        <h2 className="text-xl font-bold text-slate-900">
                            오답노트 목록
                        </h2>
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
                                const isDeleting = deletingId === note.id;

                                return (
                                    <div
                                        key={note.id}
                                        onClick={() => handleClickNote(note)}
                                        className="group cursor-pointer rounded-2xl border border-slate-200 bg-white p-6 text-left transition hover:border-blue-500 hover:shadow-md"
                                    >
                                        <div className="mb-8 flex items-start justify-between gap-4">
                                            <div>
                                                <div className="mb-3 flex flex-wrap items-center gap-2">
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
                                                        : `${getExamTypeLabel(note.exam_type)} · ${note.subject
                                                        }`}
                                                </p>
                                            </div>

                                            <div className="flex shrink-0 items-center gap-2">
                                                <button
                                                    type="button"
                                                    onClick={(e) => openDeleteModal(e, note)}
                                                    disabled={isDeleting}
                                                    className="flex items-center gap-1 rounded-full border border-red-100 bg-red-50 px-3 py-1 text-xs font-semibold text-red-500 transition hover:bg-red-100 disabled:cursor-not-allowed disabled:opacity-50"
                                                >
                                                    <Trash2 size={14} />
                                                    {isDeleting ? "삭제 중" : "삭제"}
                                                </button>

                                                <ChevronRight
                                                    size={22}
                                                    className="text-slate-400 transition group-hover:translate-x-1 group-hover:text-blue-600"
                                                />
                                            </div>
                                        </div>

                                        <div className="mb-5 grid grid-cols-3 gap-3 text-sm">
                                            <div>
                                                <p className="text-slate-400">오답 문제</p>
                                                <p className="mt-1 font-bold text-red-500">
                                                    {note.wrong_count}개
                                                </p>
                                            </div>

                                            <div>
                                                <p className="text-slate-400">미풀이</p>
                                                <p className="mt-1 font-bold text-amber-500">
                                                    {note.unsolved_count}개
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
                                            총 {note.total_count}문제 · 생성일 {note.created_at}
                                        </p>
                                    </div>
                                );
                            })}
                        </div>
                    )}
                </div>
            </section>

            {deleteTarget && (
                <div
                    className="fixed inset-0 z-[100] flex items-center justify-center bg-slate-900/40 px-4 backdrop-blur-sm"
                    onClick={closeDeleteModal}
                >
                    <div
                        className="w-full max-w-md rounded-3xl bg-white p-7 shadow-2xl"
                        onClick={(e) => e.stopPropagation()}
                    >
                        <div className="mb-5 flex items-start justify-between">
                            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-red-50 text-red-500">
                                <Trash2 size={26} />
                            </div>

                            <button
                                type="button"
                                onClick={closeDeleteModal}
                                disabled={deletingId !== null}
                                className="rounded-full p-2 text-slate-400 transition hover:bg-slate-100 hover:text-slate-600 disabled:cursor-not-allowed disabled:opacity-50"
                            >
                                <X size={20} />
                            </button>
                        </div>

                        <h2 className="text-2xl font-bold text-slate-900">
                            오답노트를 삭제할까요?
                        </h2>

                        <p className="mt-3 text-sm leading-6 text-slate-500">
                            <span className="font-semibold text-slate-800">
                                {getWrongNoteTitle(deleteTarget)}
                            </span>
                            을 삭제하면 연결된 오답 문제와 미풀이 기록도 함께 삭제됩니다.
                        </p>

                        <div className="mt-5 rounded-2xl bg-slate-50 p-4 text-sm text-slate-500">
                            삭제한 오답노트는 다시 복구할 수 없어요.
                        </div>

                        <div className="mt-7 flex gap-3">
                            <button
                                type="button"
                                onClick={closeDeleteModal}
                                disabled={deletingId !== null}
                                className="flex-1 rounded-xl border border-slate-200 bg-white py-3 text-sm font-semibold text-slate-600 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
                            >
                                취소
                            </button>

                            <button
                                type="button"
                                onClick={handleDeleteNote}
                                disabled={deletingId !== null}
                                className="flex-1 rounded-xl bg-red-500 py-3 text-sm font-semibold text-white transition hover:bg-red-600 disabled:cursor-not-allowed disabled:opacity-60"
                            >
                                {deletingId !== null ? "삭제 중..." : "삭제하기"}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </main>
    );
}