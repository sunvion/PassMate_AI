type SubmitConfirmModalProps = {
  totalCount: number;
  answeredCount: number;
  unansweredNumbers: number[];
  onClose: () => void;
  onSubmitAnyway: () => void;
  onMoveQuestion: (index: number) => void;
};

export default function SubmitConfirmModal({
  totalCount,
  answeredCount,
  unansweredNumbers,
  onClose,
  onSubmitAnyway,
  onMoveQuestion,
}: SubmitConfirmModalProps) {
  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-slate-900/40 px-4">
      <div className="w-full max-w-md rounded-3xl bg-white p-7 shadow-2xl">
        <p className="mb-2 text-sm font-bold text-blue-600">제출 전 확인</p>

        <h2 className="text-2xl font-bold text-slate-900">
          아직 풀지 않은 문제가 있어요
        </h2>

        <p className="mt-2 text-sm text-slate-500">
          {totalCount}문제 중 {answeredCount}문제를 풀었습니다.
        </p>

        <div className="mt-5 rounded-2xl bg-slate-50 p-4">
          <p className="mb-3 text-sm font-bold text-slate-700">미응답 문제</p>

          <div className="flex flex-wrap gap-2">
            {unansweredNumbers.map((number) => (
              <button
                key={number}
                onClick={() => onMoveQuestion(number - 1)}
                className="h-9 w-9 rounded-full border border-blue-200 bg-white text-sm font-bold text-blue-600 hover:bg-blue-50"
              >
                {number}
              </button>
            ))}
          </div>
        </div>

        <p className="mt-4 text-sm text-slate-500">
          제출 후에는 답안을 수정할 수 없습니다.
        </p>

        <div className="mt-6 flex justify-end gap-3">
          <button
            onClick={onClose}
            className="rounded-xl border border-slate-200 px-5 py-3 text-sm font-bold text-slate-600 hover:bg-slate-50"
          >
            계속 풀기
          </button>

          <button
            onClick={onSubmitAnyway}
            className="rounded-xl bg-blue-600 px-5 py-3 text-sm font-bold text-white hover:bg-blue-700"
          >
            제출하기
          </button>
        </div>
      </div>
    </div>
  );
}