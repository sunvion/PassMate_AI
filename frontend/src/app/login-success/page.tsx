'use client';

import { useEffect, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';

function LoginSuccessHandler() {
  const searchParams = useSearchParams();
  const router = useRouter();

  useEffect(() => {
    // 백엔드가 URL에 붙여서 보내준 토큰과 닉네임을 추출합니다.
    const token = searchParams.get('token');
    const nickname = searchParams.get('nickname');

    if (token) {
      // 로컬 스토리지에 인증 정보를 저장합니다.
      localStorage.setItem('token', token);
      if (nickname) {
        localStorage.setItem('nickname', decodeURIComponent(nickname));
      }

      // 저장이 완료되면 마이페이지 또는 메인 화면으로 이동시킵니다.
      router.push('/mypage');
    } else {
      // 토큰이 없다면 로그인 실패로 간주하고 메인으로 튕겨냅니다.
      router.push('/');
    }
  }, [searchParams, router]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50">
      <div className="p-6 bg-white rounded-xl shadow-md text-center">
        <p className="text-lg font-semibold text-gray-700 animate-pulse">
          로그인 성공! 사용자 정보를 연동 중입니다...
        </p>
      </div>
    </div>
  );
}

// Next.js App Router에서 useSearchParams를 안전하게 쓰기 위해 Suspense로 감쌉니다.
export default function LoginSuccessPage() {
  return (
    <Suspense fallback={<div>로딩 중...</div>}>
      <LoginSuccessHandler />
    </Suspense>
  );
}