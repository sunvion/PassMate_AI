type SolveHeaderProps = {
  title: string;
  currentNumber: number;
  totalCount: number;
  answeredCount: number;
  progressPercent: number;
  onSubmit: () => void;
};

function formatExamTitle(title: string) {
  return title
    .replace("CS_GENERAL", "컴퓨터일반")
    .replace("DRIVERS_LICENSE_1", "운전면허 1종")
    .replace("DRIVERS_LICENSE_2", "운전면허 2종");
}

export default function SolveHeader({
  title,
  currentNumber,
  totalCount,
  answeredCount,
  progressPercent,
  onSubmit,
}: SolveHeaderProps) {
  return (
    <div className="sticky top-16 z-40 border-b border-slate-200 bg-white shadow-sm">
      <div className="mx-auto flex h-24 w-full max-w-6xl items-center justify-between px-8">
        <h1 className="text-2xl font-bold text-slate-900">
          {formatExamTitle(title)}
        </h1>

        <div className="flex flex-1 items-center justify-center gap-5 px-10">
          <span className="text-sm font-medium text-slate-700">
            풀이 진행도 {answeredCount} / {totalCount}
          </span>

          <div className="h-2 w-80 rounded-full bg-slate-200">
            <div
              className="h-2 rounded-full bg-blue-600"
              style={{ width: `${progressPercent}%` }}
            />
          </div>

          <span className="text-sm font-semibold text-slate-700">
            {progressPercent}%
          </span>
        </div>

        <button
          type="button"
          onClick={onSubmit}
          className="rounded-xl border border-blue-500 px-8 py-3 font-semibold text-blue-600 hover:bg-blue-50"
        >
          제출하기
        </button>
      </div>
    </div>
  );
}