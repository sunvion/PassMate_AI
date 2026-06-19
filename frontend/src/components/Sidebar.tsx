"use client";

import { useState } from "react";
import type { MouseEvent } from "react";
import { usePathname } from "next/navigation";
import Link from "next/link";
import {
  Home,
  UserRound,
  ClipboardList,
  ChevronRight,
} from "lucide-react";

type SidebarProps = {
  isOpen: boolean;
  onClose: () => void;
  isLoggedIn?: boolean; // 상위 컴포넌트에서 전달하는 로그인 여부 프롭스 반영
};

export default function Sidebar({ isOpen, onClose, isLoggedIn = false, }: SidebarProps) {
  const pathname = usePathname();

  const [isWrongNoteOpen, setIsWrongNoteOpen] = useState(false);

  const activeMenuClass = "bg-blue-50 text-blue-600 shadow-sm";
  const defaultMenuClass = "text-slate-900 hover:bg-blue-50 hover:text-blue-600 shadow-sm";

  const isHomeActive = pathname === "/";
  const isMypageActive = pathname.startsWith("/mypage") || pathname.startsWith("/setting");
  const isExamActive = pathname.startsWith("/exams"); // 최신 경로인 /exams 기반 매칭 유지

  const isDev = process.env.NODE_ENV === "development";
  const canAccess = isLoggedIn || isDev;

  // 비로그인 유저가 접근할 때 메인 로그인 섹션으로 가이드하는 인터셉터 함수 (상대방 코드 수용)
  const handleProtectedClick = (e: MouseEvent<HTMLAnchorElement>) => {
    if (canAccess) {
      onClose();
      return;
    }

    e.preventDefault();

    // 메인화면의 로그인 유도 영역으로 부드럽게 스크롤
    document.getElementById("start-section")?.scrollIntoView({
      behavior: "smooth",
    });

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
        className={`fixed left-4 top-20 z-40 h-[calc(100vh-6rem)] w-[90vw] max-w-[320px] overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-2xl transition-transform duration-300 ${isOpen ? "translate-x-0" : "-translate-x-[120%]"
          }`}
      >
        <nav className="mt-4 flex flex-col gap-4 px-3 text-lg font-semibold">
          <div>
            <Link
              href="/"
              onClick={onClose}
              className={`flex items-center justify-between rounded-2xl px-5 py-4 transition 
                ${isHomeActive ? activeMenuClass : defaultMenuClass}`}
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
              className={`flex items-center gap-4 rounded-2xl px-5 py-4 transition 
                ${isMypageActive ? activeMenuClass : defaultMenuClass}`}
            >
              <UserRound size={28} />
              마이페이지
            </Link>

            <div className="ml-[68px] mt-3 flex flex-col gap-4 text-base font-medium text-slate-700">
              <Link
                href="/mypage"
                onClick={handleProtectedClick}
                className={`${pathname === "/mypage" ? "font-bold text-blue-600" : "hover:text-blue-600"}`}
              >
                학습 통계
              </Link>

              <button
                type="button"
                onClick={() => setIsWrongNoteOpen(!isWrongNoteOpen)}
                className="flex items-center justify-between text-left hover:text-blue-600"
              >
                <span>오답노트</span>
                <ChevronRight
                  size={18}
                  className={`transition-transform ${isWrongNoteOpen ? "rotate-90" : ""
                    }`}
                />
              </button>

              {isWrongNoteOpen && (
                <div className="ml-4 flex flex-col gap-3 text-sm text-slate-600">
                  <Link
                    href="/mypage"
                    onClick={handleProtectedClick}
                    className="hover:text-blue-600"
                  >
                    AI 학습 도우미
                  </Link>

                  <Link
                    href="/wrong-note/review"
                    onClick={handleProtectedClick}
                    className="hover:text-blue-600"
                  >
                    복습
                  </Link>
                </div>
              )}

              <Link
                href="/setting"
                onClick={handleProtectedClick}
                className={`${pathname.startsWith("/setting")
                  ? "font-bold text-blue-600"
                  : "hover:text-blue-600"
                  }`}
              >
                계정 관리
              </Link>
            </div>
          </div>

          <div>
            <Link
              href="/exams"
              onClick={handleProtectedClick}
              className={`flex items-center gap-4 rounded-2xl px-5 py-4 transition 
                ${isExamActive ? activeMenuClass : defaultMenuClass}`}
            >
              <ClipboardList size={28} />
              기출문제
            </Link>

            <div className="ml-[68px] mt-3 flex flex-col gap-4 text-base font-medium text-slate-700">
              <Link
                href="/exams/full"
                onClick={handleProtectedClick}
                className={`${pathname === "/exams/full"
                    ? "font-bold text-blue-600"
                    : "hover:text-blue-600"
                  }`}
              >
                전체 회차 풀기
              </Link>

              <Link
                href="/exams/single"
                onClick={handleProtectedClick}
                className={`${pathname === "/exams/single"
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