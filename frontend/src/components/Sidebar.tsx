"use client";

import { useEffect, useState } from "react";
import type { MouseEvent } from "react";
import { usePathname } from "next/navigation";
import Link from "next/link";
import {
  Home,
  UserRound,
  ClipboardList,
} from "lucide-react";

type SidebarProps = {
  isOpen: boolean;
  onClose: () => void;
};

export default function Sidebar({ isOpen, onClose }: SidebarProps) {
  const pathname = usePathname();

  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    const checkLogin = () => {
      const token = localStorage.getItem("token");
      setIsLoggedIn(!!token);
    };

    checkLogin();

    window.addEventListener("focus", checkLogin);
    window.addEventListener("storage", checkLogin);

    return () => {
      window.removeEventListener("focus", checkLogin);
      window.removeEventListener("storage", checkLogin);
    };
  }, []);

  const activeMenuClass = "bg-blue-50 text-blue-600 shadow-sm";
  const defaultMenuClass =
    "text-slate-900 hover:bg-blue-50 hover:text-blue-600 shadow-sm";

  const isHomeActive = pathname === "/";
  const isMypageActive =
    pathname.startsWith("/mypage") ||
    pathname.startsWith("/setting") ||
    pathname.startsWith("/wrong-note");

  const isExamActive =
    pathname.startsWith("/exam") || pathname.startsWith("/exams");

  const handleProtectedClick = (e: MouseEvent<HTMLAnchorElement>) => {
    const token = localStorage.getItem("token");

    if (token) {
      onClose();
      return;
    }

    e.preventDefault();
    window.location.href = "/#start-section";
    onClose();
  };

  return (
    <>
      {isOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/40"
          onClick={onClose}
        />
      )}

      <aside
        className={`fixed left-4 top-20 z-40 h-[calc(100vh-6rem)] w-[90vw] max-w-[320px] overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-2xl transition-transform duration-300 ${
          isOpen ? "translate-x-0" : "-translate-x-[120%]"
        }`}
      >
        <nav className="mt-4 flex flex-col gap-4 px-3 text-lg font-semibold">
          <div>
            <Link
              href="/"
              onClick={onClose}
              className={`flex items-center justify-between rounded-2xl px-5 py-4 transition ${
                isHomeActive ? activeMenuClass : defaultMenuClass
              }`}
            >
              <span className="flex items-center gap-4">
                <Home size={28} />
                홈
              </span>
            </Link>
          </div>

          <div>
            <Link
              href="/mypage"
              onClick={handleProtectedClick}
              className={`flex items-center gap-4 rounded-2xl px-5 py-4 transition ${
                isMypageActive ? activeMenuClass : defaultMenuClass
              }`}
            >
              <UserRound size={28} />
              마이페이지
            </Link>

            <div className="ml-[68px] mt-3 flex flex-col gap-4 text-base font-medium text-slate-700">
              <Link
                href="/mypage"
                onClick={handleProtectedClick}
                className={`${
                  pathname === "/mypage"
                    ? "font-bold text-blue-600"
                    : "hover:text-blue-600"
                }`}
              >
                학습 통계
              </Link>

              <Link
                href="/wrong-note"
                onClick={handleProtectedClick}
                className={`${
                  pathname.startsWith("/wrong-note")
                    ? "font-bold text-blue-600"
                    : "hover:text-blue-600"
                }`}
              >
                오답노트
              </Link>

              <Link
                href="/setting"
                onClick={handleProtectedClick}
                className={`${
                  pathname.startsWith("/setting")
                    ? "font-bold text-blue-600"
                    : "hover:text-blue-600"
                }`}
              >
                계정 관리
              </Link>
            </div>
          </div>

          <div>
            <div
              className={`flex cursor-default items-center gap-4 rounded-2xl px-5 py-4 transition ${
                isExamActive ? activeMenuClass : defaultMenuClass
              }`}
            >
              <ClipboardList size={28} />
              기출문제
            </div>

            <div className="ml-[68px] mt-3 flex flex-col gap-4 text-base font-medium text-slate-700">
              <Link
                href="/exam/full"
                onClick={handleProtectedClick}
                className={`${
                  pathname === "/exam/full"
                    ? "font-bold text-blue-600"
                    : "hover:text-blue-600"
                }`}
              >
                전체 회차 풀기
              </Link>

              <Link
                href="/exam/single"
                onClick={handleProtectedClick}
                className={`${
                  pathname === "/exam/single"
                    ? "font-bold text-blue-600"
                    : "hover:text-blue-600"
                }`}
              >
                한 문제씩 풀기
              </Link>
            </div>
          </div>
        </nav>
      </aside>
    </>
  );
}