"use client";

//npm install axios
import axios from "axios";
import { useEffect, useState } from "react";
import Header from "@/components/Header";
import Sidebar from "@/components/Sidebar";
import {
    UserRound,
    Mail,
    LogOut,
    Trash2,
    ChevronRight,
} from "lucide-react";

type LoginUser = {
    email: string;
    nickname: string;
};

export default function SettingPage() {
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const [user, setUser] = useState<LoginUser | null>(null);

    const [nicknameInput, setNicknameInput] = useState("");

    const [successMessage, setSuccessMessage] = useState<string | null>(null);
    const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);

    useEffect(() => {
        const fetchUser = async () => {
            try {
                const token = localStorage.getItem("token");

                if (!token) {
                    window.location.href = "/";
                    return;
                }

                const response = await axios.get(
                    "http://localhost:8000/api/v1/users/me",
                    {
                        headers: {
                            Authorization: `Bearer ${token}`,
                        },
                    }
                );

                setUser(response.data);
                setNicknameInput(response.data.nickname || "");
            } catch (error) {
                console.error("유저 정보 조회 실패:", error);

                localStorage.removeItem("token");
                localStorage.removeItem("nickname");
                localStorage.removeItem("user");

                window.location.href = "/";
            }
        };

        fetchUser();
    }, []);

    const handleNicknameSave = async () => {
        try {
            const token = localStorage.getItem("token");

            const response = await axios.put(
                "http://localhost:8000/api/v1/users/me",
                {
                    nickname: nicknameInput
                },
                {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                }
            );

            setUser(response.data);
            setNicknameInput(response.data.nickname || "");

            localStorage.setItem("nickname", response.data.nickname);
            localStorage.setItem("user", JSON.stringify(response.data));

            window.dispatchEvent(new Event("user-updated"));

            setSuccessMessage("닉네임이 수정되었습니다.");
        } catch (error: any) {
            setSuccessMessage(error.response?.data?.detail ?? "프로필 수정에 실패했습니다.");
        }
    };

    const handleLogout = () => {
        localStorage.removeItem("token");
        localStorage.removeItem("nickname");
        localStorage.removeItem("user");

        window.location.href = "/";
    };

    const handleDeleteAccount = async () => {
        try {
            const token = localStorage.getItem("token");

            await axios.delete("http://localhost:8000/api/v1/users/me", {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });

            localStorage.removeItem("token");
            localStorage.removeItem("nickname");
            localStorage.removeItem("user");

            window.location.href = "/";
        } catch (error: any) {
            setIsDeleteModalOpen(false);
            setSuccessMessage(error.response?.data?.detail ?? "회원 탈퇴에 실패했습니다.");
        }
    };

    return (
        <main className="min-h-screen bg-slate-50 text-slate-900">
            <Header
                onMenuClick={() => setIsMenuOpen(true)}
                onLoginClick={() => { }}
            />

            <Sidebar isOpen={isMenuOpen} onClose={() => setIsMenuOpen(false)} />

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
                    <section className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
                        <h2 className="mb-6 text-xl font-bold">프로필</h2>

                        <div className="flex flex-col gap-8 md:flex-row md:items-center">
                            <div className="relative w-fit">
                                <div className="flex h-40 w-40 items-center justify-center overflow-hidden rounded-full bg-gradient-to-br from-blue-200 to-blue-600 shadow-lg">
                                    <UserRound size={72} className="text-white" />
                                </div>
                            </div>

                            <div>
                                <h3 className="text-2xl font-bold">
                                    안녕하세요, {user?.nickname || "사용자"}님! 👋
                                </h3>
                                <p className="mt-3 leading-7 text-slate-500">
                                    닉네임과 계정 정보를 확인하고 <br />
                                    필요한 정보를 수정할 수 있습니다.
                                </p>
                            </div>
                        </div>
                    </section>

                    <section className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
                        <h2 className="mb-5 text-xl font-bold">닉네임</h2>

                        <div className="flex flex-col gap-4 md:flex-row">
                            <input
                                value={nicknameInput}
                                onChange={(e) => setNicknameInput(e.target.value)}
                                onKeyDown={(e) => {
                                    if (e.key === "Enter") {
                                        handleNicknameSave();
                                    }
                                }}
                                className="h-14 flex-1 rounded-2xl border border-slate-200 bg-white px-5 text-lg outline-none transition focus:border-blue-300 focus:ring-4 focus:ring-blue-50"
                            />

                            <button
                                onClick={handleNicknameSave}
                                className="h-14 rounded-2xl bg-blue-600 px-10 font-semibold text-white transition hover:bg-blue-700"
                            >
                                저장
                            </button>
                        </div>
                    </section>

                    <section className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
                        <div className="flex flex-col gap-5 md:flex-row md:items-center md:justify-between">
                            <div>
                                <h2 className="mb-5 text-xl font-bold">이메일</h2>

                                <p className="text-lg font-medium">
                                    Google 계정 로그인
                                </p>

                                <div className="mt-3 flex items-center gap-2 text-slate-500">
                                    <Mail size={18} />
                                    <span>
                                        {user?.email || "이메일 정보를 불러오는 중입니다."}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </section>

                    <section className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
                        <h2 className="mb-4 text-xl font-bold">계정 관리</h2>

                        <AccountAction
                            icon={<LogOut size={24} />}
                            title="로그아웃"
                            description="현재 계정에서 로그아웃합니다."
                            onClick={handleLogout}
                        />

                        <div className="my-4 border-t border-slate-100" />

                        <AccountAction
                            danger
                            icon={<Trash2 size={24} />}
                            title="회원 탈퇴"
                            description="계정을 삭제하고 모든 데이터를 제거합니다."
                            onClick={() => setIsDeleteModalOpen(true)}
                        />
                    </section>
                </div>
            </section>

            {successMessage && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 px-4">
                    <div className="w-full max-w-sm rounded-3xl bg-white p-7 text-center shadow-xl">
                        <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-blue-50 text-2xl text-blue-600">
                            ✓
                        </div>

                        <h3 className="text-xl font-bold text-slate-900">알림</h3>
                        <p className="mt-3 text-slate-500">{successMessage}</p>

                        <button
                            onClick={() => setSuccessMessage(null)}
                            className="mt-6 h-12 w-full rounded-2xl bg-blue-600 font-semibold text-white transition hover:bg-blue-700"
                        >
                            확인
                        </button>
                    </div>
                </div>
            )}

            {isDeleteModalOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 px-4">
                    <div className="w-full max-w-md rounded-3xl bg-white p-7 shadow-xl">
                        <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-red-50 text-2xl">
                            🗑️
                        </div>

                        <h3 className="text-center text-xl font-bold text-slate-900">
                            회원 탈퇴
                        </h3>

                        <p className="mt-3 text-center leading-6 text-slate-500">
                            정말로 회원 탈퇴하시겠습니까?
                            <br />
                            계정과 학습 데이터는 삭제되며 되돌릴 수 없습니다.
                        </p>

                        <div className="mt-7 flex gap-3">
                            <button
                                onClick={() => setIsDeleteModalOpen(false)}
                                className="h-12 flex-1 rounded-2xl border border-slate-200 font-semibold text-slate-600 transition hover:bg-slate-50"
                            >
                                취소
                            </button>

                            <button
                                onClick={handleDeleteAccount}
                                className="h-12 flex-1 rounded-2xl bg-red-500 font-semibold text-white transition hover:bg-red-600"
                            >
                                탈퇴하기
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </main>
    );
}

function AccountAction({
    icon,
    title,
    description,
    danger = false,
    onClick,
}: {
    icon: React.ReactNode;
    title: string;
    description: string;
    danger?: boolean;
    onClick?: () => void;
}) {
    return (
        <button
            onClick={onClick}
            className="flex w-full items-center justify-between rounded-2xl p-3 text-left transition hover:bg-slate-50"
        >
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