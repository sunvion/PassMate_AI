"use client";

import { useState } from "react";
import Header from "@/components/Header";
import Sidebar from "@/components/Sidebar";
import {
    Camera,
    UserRound,
    Mail,
    Monitor,
    Code2,
    Car,
    Plus,
    LogOut,
    Trash2,
    ChevronRight,
    Minus,
} from "lucide-react";

export default function SettingPage() {
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const [subjects, setSubjects] = useState([
        {
            id: 1,
            icon: <Monitor size={22} />,
            title: "국가직 9급 컴퓨터일반",
        },
        {
            id: 2,
            icon: <Code2 size={22} />,
            title: "정보처리기사",
        },
        {
            id: 3,
            icon: <Car size={22} />,
            title: "운전면허",
        },
    ]);

    const removeSubject = (id: number) => {
        setSubjects(subjects.filter((subject) => subject.id !== id));
    };

    return (
        <main className="min-h-screen bg-slate-50 text-slate-900">
            <Header
                onMenuClick={() => setIsMenuOpen(true)}
                onLoginClick={() => { }}
            />

            <Sidebar
                isOpen={isMenuOpen}
                onClose={() => setIsMenuOpen(false)}
            />

            <section className="mx-auto w-full max-w-5xl px-6 pb-12 pt-28">
                <div className="mb-8">
                    <p className="mb-3 text-sm font-medium text-slate-500">
                        마이페이지 <span className="mx-2">›</span>
                        <span className="text-slate-900">계정 관리</span>
                    </p>

                    <h1 className="text-3xl font-bold">계정 관리</h1>
                    <p className="mt-2 text-slate-500">
                        계정 정보를 확인하고 관리할 수 있습니다.
                    </p>
                </div>

                <div className="space-y-6">
                    {/* 프로필 */}
                    <section className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
                        <h2 className="mb-6 text-xl font-bold">프로필</h2>

                        <div className="flex flex-col gap-8 md:flex-row md:items-center">
                            <div className="relative w-fit">
                                <div className="flex h-40 w-40 items-center justify-center rounded-full bg-gradient-to-br from-blue-200 to-blue-600 shadow-lg">
                                    <UserRound size={72} className="text-white" />
                                </div>

                                <button className="absolute bottom-2 right-2 flex h-14 w-14 items-center justify-center rounded-full border border-slate-200 bg-white shadow-md transition hover:scale-105 hover:bg-blue-50">
                                    <Camera size={24} className="text-blue-600" />
                                </button>
                            </div>

                            <div>
                                <h3 className="text-2xl font-bold">
                                    안녕하세요, 혜진님! 👋
                                </h3>
                                <p className="mt-3 leading-7 text-slate-500">
                                    프로필 이미지를 변경하고 <br />
                                    나를 더 잘 표현해보세요.
                                </p>

                                <button className="mt-5 rounded-2xl border border-blue-200 px-6 py-3 font-semibold text-blue-600 transition hover:bg-blue-50">
                                    사진 변경하기
                                </button>
                            </div>
                        </div>
                    </section>

                    {/* 닉네임 */}
                    <section className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
                        <h2 className="mb-5 text-xl font-bold">닉네임</h2>

                        <div className="flex flex-col gap-4 md:flex-row">
                            <input
                                value="PassMateUser"
                                readOnly
                                className="h-14 flex-1 rounded-2xl border border-slate-200 px-5 text-lg outline-none"
                            />

                            <button className="h-14 rounded-2xl border border-blue-500 px-10 font-semibold text-blue-600 transition hover:bg-blue-50">
                                수정
                            </button>
                        </div>
                    </section>

                    {/* 이메일 */}
                    <section className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
                        <div className="flex flex-col gap-5 md:flex-row md:items-center md:justify-between">
                            <div>
                                <h2 className="mb-5 text-xl font-bold">이메일</h2>

                                <p className="text-lg font-medium">user@gmail.com</p>

                                <div className="mt-3 flex items-center gap-2 text-slate-500">
                                    <Mail size={18} />
                                    <span>Google 계정으로 로그인 중입니다.</span>
                                </div>
                            </div>

                            <button className="w-fit rounded-2xl bg-slate-100 px-6 py-3 font-semibold text-slate-400">
                                변경 불가
                            </button>
                        </div>
                    </section>

                    {/* 학습 과목 */}
                    <section className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
                        <h2 className="text-xl font-bold">학습 과목 관리</h2>
                        <p className="mt-2 text-slate-500">
                            학습 중인 과목을 관리하고 추가할 수 있습니다.
                        </p>

                        <div className="mt-6 space-y-3">
                            {subjects.map((subject) => (
                                <SubjectItem
                                    key={subject.id}
                                    icon={subject.icon}
                                    title={subject.title}
                                    onRemove={() => removeSubject(subject.id)}
                                />
                            ))}

                            <button className="flex h-14 w-full items-center justify-center gap-2 rounded-2xl border border-dashed border-blue-300 font-semibold text-blue-600 transition hover:bg-blue-50">
                                <Plus size={20} />
                                과목 추가하기
                            </button>
                        </div>
                    </section>

                    {/* 계정 관리 */}
                    <section className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
                        <h2 className="mb-4 text-xl font-bold">계정 관리</h2>

                        <AccountAction
                            icon={<LogOut size={24} />}
                            title="로그아웃"
                            description="현재 계정에서 로그아웃합니다."
                        />

                        <div className="my-4 border-t border-slate-100" />

                        <AccountAction
                            danger
                            icon={<Trash2 size={24} />}
                            title="회원 탈퇴"
                            description="계정을 삭제하고 모든 데이터를 제거합니다."
                        />
                    </section>
                </div>
            </section>
        </main>
    );
}

function SubjectItem({
    icon,
    title,
    onRemove,
}: {
    icon: React.ReactNode;
    title: string;
    onRemove: () => void;
}) {
    return (
        <div className="flex h-14 items-center justify-between rounded-2xl border border-slate-200 px-5">
            <div className="flex items-center gap-4">
                <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
                    {icon}
                </div>
                <span className="font-semibold">{title}</span>
            </div>

            <button
                onClick={onRemove}
                className="flex h-8 w-8 items-center justify-center rounded-full text-red-500 transition hover:bg-red-50 hover:text-red-600"
            >
                <Minus size={22} strokeWidth={3} />
            </button>
        </div>
    );
}

function AccountAction({
    icon,
    title,
    description,
    danger = false,
}: {
    icon: React.ReactNode;
    title: string;
    description: string;
    danger?: boolean;
}) {
    return (
        <button className="flex w-full items-center justify-between rounded-2xl p-3 text-left transition hover:bg-slate-50">
            <div className="flex items-center gap-5">
                <div className={danger ? "text-red-500" : "text-slate-600"}>
                    {icon}
                </div>

                <div>
                    <p
                        className={`font-bold ${danger ? "text-red-500" : "text-slate-900"
                            }`}
                    >
                        {title}
                    </p>
                    <p className="mt-1 text-sm text-slate-500">{description}</p>
                </div>
            </div>

            <ChevronRight size={22} className="text-slate-400" />
        </button>
    );
}