"use client";

import Header from "@/components/Header";
import Sidebar from "@/components/Sidebar";
import { useState } from "react";
import { Plus, BookOpen, ChevronRight } from "lucide-react";

type WrongNote = {
    id: number;
    title: string;
    type: "전체 회차" | "한 문제씩";
    subject: string;
    wrongCount: number;
    unsolvedCount: number;
    createdAt: string;
    progress: number;
};

const mockWrongNotes: WrongNote[] = [
    {
        id: 1,
        title: "2026 국가직 컴퓨터일반 오답노트",
        type: "전체 회차",
        subject: "컴퓨터일반",
        wrongCount: 8,
        unsolvedCount: 2,
        createdAt: "2026.06.23",
        progress: 25,
    },
    {
        id: 2,
        title: "운영체제 오답노트",
        type: "한 문제씩",
        subject: "운영체제",
        wrongCount: 5,
        unsolvedCount: 0,
        createdAt: "2026.06.23",
        progress: 40,
    },
    {
        id: 3,
        title: "데이터베이스 오답노트",
        type: "한 문제씩",
        subject: "데이터베이스",
        wrongCount: 3,
        unsolvedCount: 1,
        createdAt: "2026.06.22",
        progress: 10,
    },
];

export default function WrongNotePage() {
    const [isMenuOpen, setIsMenuOpen] = useState(false);

    return (
        <main className="min-h-screen bg-slate-50">
            <Header
                onMenuClick={() => setIsMenuOpen(true)}
                onLoginClick={() => { }}
            />
            <Sidebar isOpen={isMenuOpen} onClose={() => setIsMenuOpen(false)} />

            <section className="mx-auto max-w-6xl px-8 py-10">
                <div className="mb-8 flex items-start justify-between">
                    <div>
                        <h1 className="text-3xl font-bold text-slate-900">오답노트</h1>
                        <p className="mt-2 text-slate-500">
                            틀린 문제와 안 푼 문제를 모아보고 복습해보세요.
                        </p>
                    </div>

                    <button className="flex items-center gap-2 rounded-xl bg-blue-600 px-5 py-3 font-semibold text-white shadow-sm transition hover:bg-blue-700">
                        <Plus size={20} />새 오답노트 생성
                    </button>
                </div>

                <div className="rounded-2xl border border-slate-200 bg-white p-6">
                    <div className="mb-6 flex items-center gap-2">
                        <BookOpen className="text-blue-600" size={22} />
                        <h2 className="text-xl font-bold text-slate-900">오답노트 목록</h2>
                    </div>

                    <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
                        {mockWrongNotes.map((note) => {
                            const totalCount = note.wrongCount + note.unsolvedCount;

                            return (
                                <button
                                    key={note.id}
                                    className="group rounded-2xl border border-slate-200 bg-white p-6 text-left transition hover:border-blue-500 hover:shadow-md"
                                >
                                    <div className="mb-5 flex items-start justify-between">
                                        <div>
                                            <div className="mb-3 flex items-center gap-2">
                                                <h3 className="text-lg font-bold text-slate-900">
                                                    {note.title}
                                                </h3>
                                                <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-600">
                                                    {note.type}
                                                </span>
                                            </div>

                                            <p className="text-sm text-slate-500">
                                                과목 {note.subject}
                                            </p>
                                        </div>

                                        <ChevronRight
                                            size={22}
                                            className="text-slate-400 transition group-hover:translate-x-1 group-hover:text-blue-600"
                                        />
                                    </div>

                                    <div className="mb-5 grid grid-cols-3 gap-3 text-sm">
                                        <div>
                                            <p className="text-slate-400">오답 문제</p>
                                            <p className="mt-1 font-bold text-red-500">
                                                {note.wrongCount}개
                                            </p>
                                        </div>

                                        <div>
                                            <p className="text-slate-400">안 푼 문제</p>
                                            <p className="mt-1 font-bold text-orange-500">
                                                {note.unsolvedCount}개
                                            </p>
                                        </div>

                                        <div>
                                            <p className="text-slate-400">생성일</p>
                                            <p className="mt-1 font-semibold text-slate-700">
                                                {note.createdAt}
                                            </p>
                                        </div>
                                    </div>

                                    <div className="flex items-center gap-4">
                                        <span className="text-sm text-slate-500">복습 진행률</span>
                                        <div className="h-2 flex-1 rounded-full bg-slate-100">
                                            <div
                                                className="h-2 rounded-full bg-blue-600"
                                                style={{ width: `${note.progress}%` }}
                                            />
                                        </div>
                                        <span className="text-sm font-semibold text-slate-600">
                                            {note.progress}%
                                        </span>
                                    </div>

                                    <p className="mt-4 text-sm text-slate-400">
                                        총 {totalCount}문제
                                    </p>
                                </button>
                            );
                        })}
                    </div>

                    <button className="mt-6 flex w-full items-center justify-center gap-2 rounded-2xl border border-dashed border-blue-300 py-6 font-semibold text-blue-600 transition hover:bg-blue-50">
                        <Plus size={20} />새 오답노트 만들기
                    </button>
                </div>
            </section>
        </main>
    );
}