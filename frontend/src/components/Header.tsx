"use client";

import { useEffect, useState } from "react";
import Image from "next/image";
import Link from "next/link";

type HeaderProps = {
  onMenuClick: () => void;
  onLoginClick: () => void;
};

export default function Header({ onMenuClick, onLoginClick }: HeaderProps) {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [nickname, setNickname] = useState<string | null>(null);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);

  useEffect(() => {
    const fetchUser = async () => {
      const token = localStorage.getItem("token");

      if (!token) {
        setIsLoggedIn(false);
        setNickname(null);
        return;
      }

      try {
        const response = await fetch("http://localhost:8000/api/v1/users/me", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error("유저 정보 조회 실패");
        }

        const data = await response.json();

        setIsLoggedIn(true);
        setNickname(data.nickname);
        localStorage.setItem("nickname", data.nickname);
        localStorage.setItem("user", JSON.stringify(data));
      } catch (error) {
        console.error("헤더 유저 정보 조회 실패:", error);

        localStorage.removeItem("token");
        localStorage.removeItem("nickname");
        localStorage.removeItem("user");

        setIsLoggedIn(false);
        setNickname(null);
      }
    };

    fetchUser();

    window.addEventListener("user-updated", fetchUser);

    return () => {
      window.removeEventListener("user-updated", fetchUser);
    };
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("nickname");
    localStorage.removeItem("user");

    setIsLoggedIn(false);
    setNickname(null);
    setIsUserMenuOpen(false);

    window.location.href = "/";
  };

  const displayName = nickname || "사용자";

  return (
    <header className="fixed left-0 top-0 z-[999] flex h-16 w-full items-center justify-between border-b border-slate-200 bg-white px-8 text-slate-900 shadow-sm">
      <div className="flex items-center gap-4 md:gap-8">
        <button onClick={onMenuClick} className="text-2xl">
          ☰
        </button>

        <Link href="/">
          <div className="flex items-center gap-3 text-xl font-extrabold text-slate-950">
            <Image
              src="/images/PM_icon.png"
              alt="PassMate AI 로고"
              width={45}
              height={45}
              className="h-auto w-auto rounded-lg"
              priority
            />
            <span className="hidden md:block font-extrabold text-slate-950">
              PassMate AI
            </span>
          </div>
        </Link>
      </div>

      {!isLoggedIn ? (
        <button
          onClick={onLoginClick}
          className="rounded-lg bg-blue-600 px-5 py-2 text-sm font-semibold text-white shadow hover:bg-blue-700"
        >
          로그인
        </button>
      ) : (
        <div className="relative">
          <button
            type="button"
            onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
            className="rounded-lg bg-blue-50 px-5 py-2 text-sm font-semibold text-blue-600 shadow-sm hover:bg-blue-100"
          >
            안녕하세요, {displayName}님
          </button>

          {isUserMenuOpen && (
            <div className="absolute right-0 mt-3 w-60 rounded-2xl border border-slate-200 bg-white p-4 shadow-xl">
              <div className="flex items-center gap-3 text-xl font-bold text-slate-900">{displayName}</div>
              <p className="mt-1 truncate text-sm text-slate-500">
                Google 계정으로 로그인 중
              </p>

              <div className="my-3 h-px bg-slate-100" />

              <Link
                href="/setting"
                className="block rounded-xl px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50"
                onClick={() => setIsUserMenuOpen(false)}
              >
                계정 관리
              </Link>

              <button
                type="button"
                onClick={handleLogout}
                className="w-full rounded-xl px-3 py-2 text-left text-sm font-semibold text-red-500 hover:bg-red-50"
              >
                로그아웃
              </button>
            </div>
          )}
        </div>
      )}
    </header>
  );
}