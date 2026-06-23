import { Question } from "@/types/exam";

type QuestionCardProps = {
  question: Question;
  selectedChoice?: number;
  onSelectChoice: (questionId: number, choiceNumber: number) => void;
};

export default function QuestionCard({
  question,
  selectedChoice,
  onSelectChoice,
}: QuestionCardProps) {
  const choices = question.choices ?? [];

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-8">
      <h2 className="mb-5 text-xl font-bold text-blue-600">
        문제 {question.number}.
      </h2>

      <p className="whitespace-pre-line text-xl font-semibold leading-relaxed text-slate-900">
        {question.text}
      </p>

      {question.imageUrl && (
        <div className="mt-7 rounded-xl border border-slate-200 bg-white p-4">
          <img
            src={question.imageUrl}
            alt={`${question.number}번 문제 이미지`}
            className="mx-auto max-h-80 w-full object-contain"
          />
        </div>
      )}

      <div className="mt-7 space-y-4">
        {choices.length === 0 ? (
          <p className="rounded-xl bg-red-50 p-4 text-sm text-red-600">
            선택지 데이터가 없습니다.
          </p>
        ) : (
          choices.map((choice) => {
            const isSelected = selectedChoice === choice.number;

            return (
              <button
                key={choice.id}
                onClick={() => onSelectChoice(question.id, choice.number)}
                className={`w-full rounded-xl border p-5 text-left transition ${isSelected
                    ? "border-blue-500 bg-blue-50"
                    : "border-slate-200 bg-white hover:border-blue-300 hover:bg-slate-50"
                  }`}
              >
                <div className="flex items-start gap-4">
                  <span
                    className={`mt-1 flex h-5 w-5 items-center justify-center rounded-full border ${isSelected
                        ? "border-blue-600 bg-blue-600"
                        : "border-slate-400"
                      }`}
                  >
                    {isSelected && (
                      <span className="h-2 w-2 rounded-full bg-white" />
                    )}
                  </span>

                  <div className="flex-1">
                    <div className="flex gap-3 text-base font-medium text-slate-900">
                      <span>{choice.number}</span>
                      {choice.text && <span>{choice.text}</span>}
                    </div>

                    {choice.imageUrl && (
                      <div className="mt-4 rounded-xl border border-slate-200 bg-white p-3">
                        <img
                          src={choice.imageUrl}
                          alt={`${choice.number}번 선택지 이미지`}
                          className="mx-auto max-h-52 w-full object-contain"
                        />
                      </div>
                    )}
                  </div>
                </div>
              </button>
            );
          })
        )}
      </div>
    </section>
  );
}