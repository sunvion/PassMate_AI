"use client";

import Image from "next/image";
import Link from "next/link";

type HeaderProps = {
  onMenuClick: () => void;
  onLoginClick: () => void;
};

export default function Header({ onMenuClick, onLoginClick }: HeaderProps) {
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
              className="rounded-lg"
              priority
            />
            <span className="hidden md:block">PassMate AI</span>
          </div>
        </Link>
      </div>

      <button
        onClick={onLoginClick}
        className="rounded-lg bg-blue-600 px-5 py-2 text-sm font-semibold text-white shadow hover:bg-blue-700"
      >
        로그인
      </button>
    </header>
  );
}