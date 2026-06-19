"use client";

import Image from "next/image";

interface LoginModalProps {
  onClose: () => void;
}

export default function LoginModal({ onClose }: LoginModalProps) {
  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center px-4">
      <div
        className="absolute inset-0 bg-black/45 backdrop-blur-sm"
        onClick={onClose}
      />

      <div className="relative z-[101] w-full max-w-md rounded-3xl bg-white p-8 shadow-2xl">
        <button
          onClick={onClose}
          className="absolute right-5 top-5 text-xl text-slate-400 hover:text-slate-700"
        >
          ×
        </button>

        <div className="mb-6 text-center">
          <h2 className="text-3xl font-extrabold text-slate-900">
            로그인 / 회원가입
          </h2>
          <p className="mt-3 text-sm leading-6 text-slate-500">
            Google 계정으로 간편하게 로그인하고
            <br />
            PassMate AI 학습을 시작하세요.
          </p>
        </div>

        <button className="relative flex w-full items-center rounded-xl border border-slate-300 bg-white px-6 py-4 font-bold text-slate-800 shadow-sm transition hover:bg-slate-50">
          <Image
            src="/images/google_logo.png"
            alt="Google 로고"
            width={36}
            height={36}
          />

          <span className="absolute left-1/2 -translate-x-1/2">
            Google로 계속하기
          </span>
        </button>

        <div className="mt-6 space-y-3 text-sm font-medium text-slate-600">
          <p className="flex items-center gap-3">
            <span className="flex h-6 w-6 items-center justify-center rounded-full bg-blue-100 text-blue-600">
              ✓
            </span>
            Google 계정으로 안전하게 로그인
          </p>

          <p className="flex items-center gap-3">
            <span className="flex h-6 w-6 items-center justify-center rounded-full bg-blue-100 text-blue-600">
              ✓
            </span>
            처음이신가요? 자동으로 회원가입이 진행돼요
          </p>
        </div>

        <div className="mt-8 rounded-2xl bg-blue-50 p-5">
          <p className="font-bold text-slate-800">안심하고 사용하세요</p>

          <p className="mt-2 text-sm leading-6 text-slate-600">
            개인정보는 안전하게 보호되며,
            <br />
            Google 계정 정보는 로그인 용도로만 사용됩니다.
          </p>
        </div>

        <p className="mt-8 text-center text-xs leading-5 text-slate-400">
          계속하면 서비스 이용약관 및 개인정보 처리방침에
          <br />
          동의하는 것으로 간주됩니다.
        </p>
      </div>
    </div>
  );
}