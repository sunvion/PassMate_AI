import { Question, SelectedAnswers } from "@/types/exam";

type QuestionNavigatorProps = {
  questions: Question[];
  currentIndex: number;
  answers: SelectedAnswers;
  onMove: (index: number) => void;
};

export default function QuestionNavigator({
  questions,
  currentIndex,
  answers,
  onMove,
}: QuestionNavigatorProps) {
  return (
    <aside className="rounded-2xl border border-slate-200 bg-white p-6">
      <h3 className="mb-6 text-lg font-bold text-slate-900">문제 목록</h3>

      <div className="grid grid-cols-5 gap-3">
        {questions.map((question, index) => {
          const isCurrent = currentIndex === index;
          const isAnswered = answers[question.id] !== undefined;

          return (
            <button
              key={question.id}
              onClick={() => onMove(index)}
              className={`h-12 rounded-xl border text-sm font-semibold transition ${isCurrent
                  ? "border-blue-600 bg-blue-600 text-white"
                  : isAnswered
                    ? "border-blue-500 bg-white text-blue-600"
                    : "border-slate-200 bg-slate-100 text-slate-400 hover:border-blue-300"
                }`}
            >
              {question.number}
            </button>
          );
        })}
      </div>

      <div className="mt-10 space-y-4 rounded-xl border border-slate-200 p-5 text-sm text-slate-700">
        <div className="flex items-center gap-3">
          <span className="h-4 w-4 rounded bg-blue-600" />
          현재 문제
        </div>
        <div className="flex items-center gap-3">
          <span className="h-4 w-4 rounded border border-blue-500" />
          답을 선택한 문제
        </div>
        <div className="flex items-center gap-3">
          <span className="h-4 w-4 rounded bg-slate-200" />
          아직 풀지 않은 문제
        </div>
      </div>
    </aside>
  );
}