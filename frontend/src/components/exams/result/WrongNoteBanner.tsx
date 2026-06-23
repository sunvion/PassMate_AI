// "AI가 분석한 오답노트가 준비됐어요!" 배너
import { useRouter } from "next/navigation";

type WrongNoteBannerProps = {
  wrongCount: number;
};

export default function WrongNoteBanner({ wrongCount }: WrongNoteBannerProps) {
  const router = useRouter();

  return (
    <section className="flex items-center justify-between rounded-2xl border border-blue-100 bg-blue-50 p-8">
      <div>
        <p className="mb-2 text-4xl">📘</p>
        <h2 className="text-2xl font-extrabold text-slate-900">
          AI가 분석한 오답노트가 준비됐어요!
        </h2>
        <p className="mt-3 text-slate-600">
          틀린 문제를 다시 확인하고 개념을 복습해 보세요.
        </p>
        <p className="mt-4 inline-flex rounded-full bg-white px-4 py-2 text-sm font-bold text-blue-600">
          총 {wrongCount}문제 저장
        </p>
      </div>

      <button
        onClick={() => router.push("/wrong-note")}
        className="rounded-xl bg-blue-600 px-8 py-4 font-bold text-white transition hover:bg-blue-700"
      >
        오답노트 바로가기
      </button>
    </section>
  );
}