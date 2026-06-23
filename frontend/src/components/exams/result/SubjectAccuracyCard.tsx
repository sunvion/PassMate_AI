// 단원별/과목별 정답률 막대
import type { SubjectAccuracy } from "@/types/examResult";

type SubjectAccuracyCardProps = {
  subjectStats: SubjectAccuracy[];
};

export default function SubjectAccuracyCard({
  subjectStats,
}: SubjectAccuracyCardProps) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
      <h2 className="mb-8 text-xl font-bold text-slate-900">단원별 정답률</h2>

      <div className="space-y-6">
        {subjectStats.map((item) => (
          <div key={item.subject} className="grid grid-cols-[160px_1fr_50px] items-center gap-5">
            <p className="font-semibold text-slate-800">{item.subject}</p>

            <div className="h-3 rounded-full bg-slate-200">
              <div
                className={`h-3 rounded-full ${
                  item.accuracy < 50 ? "bg-rose-500" : "bg-blue-600"
                }`}
                style={{ width: `${item.accuracy}%` }}
              />
            </div>

            <p className="text-right font-bold text-slate-800">
              {item.accuracy}%
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}