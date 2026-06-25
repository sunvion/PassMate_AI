import { CheckCircle2, XCircle } from "lucide-react";
import { Question } from "@/types/exam";

type QuestionCardProps = {
  question: Question;
  selectedChoice?: number;
  examType: string;
  onSelectChoice: (questionId: number, choiceNumber: number) => void;

  // 한 문제씩 풀기에서만 사용
  isChecked?: boolean;
  correctAnswer?: number[];
};

export default function QuestionCard({
  question,
  selectedChoice,
  examType,
  onSelectChoice,
  isChecked = false,
  correctAnswer,
}: QuestionCardProps) {
  const choices = question.choices ?? [];
  const isDriverLicense = examType.startsWith("DRIVERS_LICENSE");

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-8">
      <h2 className="mb-5 text-xl font-bold text-blue-600">
        문제 {question.number}.
      </h2>

      {isDriverLicense && question.text && (
        <p className="whitespace-pre-line rounded-xl bg-slate-50 p-5 text-lg font-semibold leading-relaxed text-slate-900">
          {question.text}
        </p>
      )}

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
            const isCorrect = correctAnswer?.includes(choice.number) ?? false;
            const isWrongSelected = isChecked && isSelected && !isCorrect;

            let buttonClass =
              "border-slate-200 bg-white hover:border-blue-300 hover:bg-slate-50";

            let circleClass = "border-slate-400 bg-white";

            if (!isChecked && isSelected) {
              buttonClass = "border-blue-500 bg-blue-50";
              circleClass = "border-blue-600 bg-blue-600";
            }

            if (isChecked && isCorrect) {
              buttonClass = "border-emerald-400 bg-emerald-50";
              circleClass = "border-emerald-500 bg-emerald-500";
            }

            if (isWrongSelected) {
              buttonClass = "border-rose-400 bg-rose-50";
              circleClass = "border-rose-500 bg-rose-500";
            }

            return (
              <button
                key={choice.id}
                onClick={() => onSelectChoice(question.id, choice.number)}
                disabled={isChecked}
                className={`w-full rounded-xl border p-5 text-left transition ${buttonClass}`}
              >
                <div className="flex items-start gap-4">
                  <span
                    className={`mt-1 flex h-5 w-5 items-center justify-center rounded-full border ${circleClass}`}
                  >
                    {!isChecked && isSelected && (
                      <span className="h-2 w-2 rounded-full bg-white" />
                    )}

                    {isChecked && isCorrect && (
                      <CheckCircle2 className="h-4 w-4 text-white" />
                    )}

                    {isWrongSelected && (
                      <XCircle className="h-4 w-4 text-white" />
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