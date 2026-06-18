"use client";

import { useState } from "react";
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
};

export default function Sidebar({ isOpen, onClose }: SidebarProps) {
  const [isWrongNoteOpen, setIsWrongNoteOpen] = useState(false);
  const [isExamOpen, setIsExamOpen] = useState(false);

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
              className="flex items-center justify-between rounded-2xl bg-blue-50 px-5 py-4 text-blue-600 shadow-sm transition hover:bg-blue-600 hover:text-white hover:shadow-md"
            >
              <span className="flex items-center gap-4">
                <Home size={28} />
                홈
              </span>
              <ChevronRight size={24} />
            </Link>
          </div>

          <div>
            <Link
              href="/mypage"
              onClick={onClose}
              className="flex items-center gap-4 rounded-2xl px-5 py-4 transition hover:bg-blue-50 hover:text-blue-600 hover:shadow-md"
            >
              <UserRound size={28} />
              마이페이지
            </Link>

            <div className="ml-[68px] mt-3 flex flex-col gap-4 text-base font-medium text-slate-700">
              <Link href="/mypage" onClick={onClose} className="hover:text-blue-600">
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
                  className={`transition-transform ${
                    isWrongNoteOpen ? "rotate-90" : ""
                  }`}
                />
              </button>

              {isWrongNoteOpen && (
                <div className="ml-4 flex flex-col gap-3 text-sm text-slate-600">
                  <Link
                    href="/wrong-note/ai-helper"
                    onClick={onClose}
                    className="hover:text-blue-600"
                  >
                    AI 학습 도우미
                  </Link>

                  <Link
                    href="/wrong-note/review"
                    onClick={onClose}
                    className="hover:text-blue-600"
                  >
                    복습
                  </Link>
                </div>
              )}

              <Link
                href="/settings/account"
                onClick={onClose}
                className="hover:text-blue-600"
              >
                계정 관리
              </Link>
            </div>
          </div>

          <div>
            <Link
              href="/exams"
              onClick={onClose}
              className="flex items-center gap-4 rounded-2xl px-5 py-4 transition hover:bg-blue-50 hover:text-blue-600 hover:shadow-md"
            >
              <ClipboardList size={28} />
              기출문제
            </Link>

            <div className="ml-[68px] mt-3 flex flex-col gap-4 text-base font-medium text-slate-700">
              <button
                type="button"
                onClick={() => setIsExamOpen(!isExamOpen)}
                className="flex items-center justify-between text-left hover:text-blue-600"
              >
                <span>회차별 풀기</span>
                <ChevronRight
                  size={18}
                  className={`transition-transform ${
                    isExamOpen ? "rotate-90" : ""
                  }`}
                />
              </button>

              {isExamOpen && (
                <div className="ml-4 flex flex-col gap-3 text-sm text-slate-600">
                  <Link href="/exams/full" onClick={onClose} className="hover:text-blue-600">
                    전체 회차 풀기
                  </Link>

                  <Link href="/exams/single" onClick={onClose} className="hover:text-blue-600">
                    한 문제씩 풀기
                  </Link>
                </div>
              )}
            </div>
          </div>
        </nav>
      </aside>
    </>
  );
}