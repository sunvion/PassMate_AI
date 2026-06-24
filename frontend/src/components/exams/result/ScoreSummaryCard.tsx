type ScoreSummaryCardProps = {
  score: number;
  totalCount: number;
  correctCount: number;
  wrongCount: number;
  accuracy: number;
};

export default function ScoreSummaryCard({
  score,
  totalCount,
  correctCount,
  wrongCount,
  accuracy,
}: ScoreSummaryCardProps) {
  const safeAccuracy = Math.max(0, Math.min(accuracy, 100));

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
      <h2 className="mb-6 text-xl font-bold text-slate-900">전체 점수</h2>

      <div className="mb-6 flex items-end gap-2">
        <span className="text-6xl font-extrabold text-blue-600">{score}</span>
        <span className="mb-2 text-2xl font-bold text-slate-500">
          점 / 100점
        </span>
      </div>

      <div className="grid grid-cols-2 gap-4 border-t border-slate-200 pt-5">
        <div className="rounded-xl border border-blue-100 bg-blue-50 p-4 text-center">
          <p className="text-sm font-semibold text-slate-500">정답</p>
          <p className="mt-1 text-2xl font-extrabold text-blue-600">
            {correctCount}문제
          </p>
        </div>

        <div className="rounded-xl border border-rose-100 bg-rose-50 p-4 text-center">
          <p className="text-sm font-semibold text-slate-500">오답</p>
          <p className="mt-1 text-2xl font-extrabold text-rose-500">
            {wrongCount}문제
          </p>
        </div>
      </div>

      <div className="mt-8 flex justify-center">
        <div
          className="flex h-36 w-36 items-center justify-center rounded-full"
          style={{
            background: `conic-gradient(#2563eb ${safeAccuracy * 3.6}deg, #e2e8f0 0deg)`,
          }}
        >
          <div className="flex h-24 w-24 items-center justify-center rounded-full bg-white">
            <div className="text-center">
              <p className="text-sm font-bold text-slate-500">정답률</p>
              <p className="text-3xl font-extrabold text-blue-600">
                {safeAccuracy}%
              </p>
            </div>
          </div>
        </div>
      </div>

      <p className="mt-5 text-center text-sm text-slate-500">
        총 {totalCount}문제 기준
      </p>
    </section>
  );
}