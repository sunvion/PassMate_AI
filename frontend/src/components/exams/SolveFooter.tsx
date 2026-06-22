type SolveFooterProps = {
  currentIndex: number;
  totalCount: number;
  onPrev: () => void;
  onNext: () => void;
};

export default function SolveFooter({
  currentIndex,
  totalCount,
  onPrev,
  onNext,
}: SolveFooterProps) {
  return (
    <div className="mt-6 flex items-center justify-between">
      <button
        onClick={onPrev}
        disabled={currentIndex === 0}
        className="rounded-xl border border-slate-300 px-8 py-4 font-semibold text-slate-700 disabled:cursor-not-allowed disabled:opacity-40"
      >
        이전 문제
      </button>

      <button
        onClick={onNext}
        disabled={currentIndex === totalCount - 1}
        className="rounded-xl bg-blue-600 px-10 py-4 font-semibold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-40"
      >
        다음 문제
      </button>
    </div>
  );
}