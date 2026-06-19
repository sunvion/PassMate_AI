"use client";

import Image from "next/image";

interface LoginModalProps {
  onClose: () => void;
}

export default function LoginModal({ onClose }: LoginModalProps) {
  
  // 🔥 [변경] 보안 에러를 유발하는 팝업 대신 직접 구글 로그인 주소로 이동시킵니다.
  const handleGoogleLogin = () => {
    const GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth";
    
    // 구글 콘솔 및 백엔드 .env와 완벽히 일치해야 하는 자격 증명 파라미터들
    const params = {
      // ⚠️ 여기에 본인의 구글 클라이언트 ID 문자열을 직접 넣으시거나 환경변수를 사용하세요.
      client_id: process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || "본인의_구글_클라이언트_ID_입력",
      redirect_uri: "http://localhost:8000/api/v1/auth/callback/google",
      response_type: "code",
      scope: "openid email profile",
      access_type: "offline",
      prompt: "consent"
    };

    const queryString = new URLSearchParams(params).toString();
    
    // 브라우저 화면 자체를 구글 로그인 페이지로 깔끔하게 리디렉션
    window.location.href = `${GOOGLE_AUTH_URL}?${queryString}`;
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center px-4">
      {/* 배경 블러 및 닫기 클릭 레이어 */}
      <div
        className="absolute inset-0 bg-black/45 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* 모달 본문 컨테이너 */}
      <div className="relative z-[101] w-full max-w-md rounded-3xl bg-white p-8 shadow-2xl">
        {/* 닫기 버튼 */}
        <button
          type="button"
          onClick={onClose}
          className="absolute right-5 top-5 text-xl text-slate-400 hover:text-slate-700"
        >
          ×
        </button>

        {/* 헤더 섹션 */}
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

        {/* 🔥 리디렉션 핸들러를 바인딩한 최종 안정화 버튼 */}
        <button 
          type="button"
          onClick={(e) => {
            e.preventDefault();
            handleGoogleLogin(); // 직접 연동 함수 호출
          }}
          className="relative flex w-full items-center rounded-xl border border-slate-300 bg-white px-6 py-4 font-bold text-slate-800 shadow-sm transition hover:bg-slate-50"
        >
          <div className="pointer-events-none flex items-center select-none">
            <Image
              src="/images/google_logo.png"
              alt="Google 로고"
              width={36}
              height={36}
              priority
            />
          </div>

          <span className="absolute left-1/2 -translate-x-1/2 pointer-events-none select-none">
            Google로 계속하기
          </span>
        </button>

        {/* 특징 안내 섹션 */}
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

        {/* 보안 안내 섹션 */}
        <div className="mt-8 rounded-2xl bg-blue-50 p-5">
          <p className="font-bold text-slate-800">안심하고 사용하세요</p>
          <p className="mt-2 text-sm leading-6 text-slate-600">
            개인정보는 안전하게 보호되며,
            <br />
            Google 계정 정보는 로그인 용도로만 사용됩니다.
          </p>
        </div>

        {/* 이용약관 동의 안내 */}
        <p className="mt-8 text-center text-xs leading-5 text-slate-400">
          계속하면 서비스 이용약관 및 개인정보 처리방침에
          <br />
          동의하는 것으로 간주됩니다.
        </p>
      </div>
    </div>
  );
}