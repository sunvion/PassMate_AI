"use client";

import { useEffect, useState } from "react";
import Image from "next/image";
import Link from "next/link";

type HeaderProps = {
  onMenuClick: () => void;
  onLoginClick: () => void;
};

export default function Header({ onMenuClick, onLoginClick }: HeaderProps) {
  const [nickname, setNickname] = useState<string | null>(null);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);

  useEffect(() => {
    const savedNickname = localStorage.getItem("nickname");

    if (savedNickname) {
      setNickname(savedNickname);
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("nickname");
    setNickname(null);
    window.location.href = "/";
  };

  return (
    <header className="fixed left-0 top-0 z-50 flex h-16 w-full items-center justify-between border-b border-slate-200 bg-white/90 px-8 backdrop-blur">
      <div className="flex items-center gap-4 md:gap-8">
        <button onClick={onMenuClick} className="text-2xl">
          ☰
        </button>

        <Link href="/">
          <div className="flex items-center gap-3 font-bold text-xl">
            <Image
              src="/images/PM_icon.png"
              alt="PassMate AI 로고"
              width={45}
              height={45}
              className="h-auto w-auto rounded-lg"
              priority
            />
            <span className="hidden md:block">PassMate AI</span>
          </div>
        </Link>
      </div>

      {!nickname ? (
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
            안녕하세요, {nickname}님
          </button>

          {isUserMenuOpen && (
            <div className="absolute right-0 mt-3 w-60 rounded-2xl border border-slate-200 bg-white p-4 shadow-xl">
              <p className="font-bold text-slate-900">{nickname}</p>
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