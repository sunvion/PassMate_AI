import Image from "next/image";

export default function Home() {
  return (
    <div className="flex flex-col flex-1 items-center justify-center bg-zinc-50 font-sans dark:bg-black">
      <main className="flex flex-1 w-full max-w-3xl flex-col items-center justify-between py-32 px-16 bg-white dark:bg-black sm:items-start">
        <Image
          className="dark:invert"
          src="/next.svg"
          alt="Next.js logo"
          width={100}
          height={20}
          priority
        />
        <div className="flex flex-col items-center gap-6 text-center sm:items-start sm:text-left">
          <h1 className="max-w-xs text-3xl font-semibold leading-10 tracking-tight text-black dark:text-zinc-50">
            To get started, edit the page.tsx file.
          </h1>
          <p className="max-w-md text-lg leading-8 text-zinc-600 dark:text-zinc-400">
            Looking for a starting point or more instructions? Head over to{" "}
            <a
              href="https://vercel.com/templates?framework=next.js&utm_source=create-next-app&utm_medium=appdir-template-tw&utm_campaign=create-next-app"
              className="font-medium text-zinc-950 dark:text-zinc-50"
            >
              Templates
            </a>{" "}
            or the{" "}
            <a
              href="https://nextjs.org/learn?utm_source=create-next-app&utm_medium=appdir-template-tw&utm_campaign=create-next-app"
              className="font-medium text-zinc-950 dark:text-zinc-50"
            >
              Learning
            </a>{" "}
            center.
          </p>
        </div>
        <div className="flex flex-col gap-4 text-base font-medium sm:flex-row">
          <a
            className="flex h-12 w-full items-center justify-center gap-2 rounded-full bg-foreground px-5 text-background transition-colors hover:bg-[#383838] dark:hover:bg-[#ccc] md:w-[158px]"
            href="https://vercel.com/new?utm_source=create-next-app&utm_medium=appdir-template-tw&utm_campaign=create-next-app"
            target="_blank"
            rel="noopener noreferrer"
          >
            <Image
              className="dark:invert"
              src="/vercel.svg"
              alt="Vercel logomark"
              width={16}
              height={16}
            />
            Deploy Now
          </a>
          <a
            className="flex h-12 w-full items-center justify-center rounded-full border border-solid border-black/[.08] px-5 transition-colors hover:border-transparent hover:bg-black/[.04] dark:border-white/[.145] dark:hover:bg-[#1a1a1a] md:w-[158px]"
            href="https://nextjs.org/docs?utm_source=create-next-app&utm_medium=appdir-template-tw&utm_campaign=create-next-app"
            target="_blank"
            rel="noopener noreferrer"
          >
            Documentation
          </a>
        </div>
<<<<<<< HEAD
      </main>
=======
      </section>

      {/* 2. 핵심 기능 섹션 */}
      <section className="flex min-h-screen flex-col items-center justify-center px-10">
        <span className="mb-4 rounded-full bg-blue-100 px-4 py-2 text-sm font-bold text-blue-600">
          핵심 기능
        </span>

        <h2 className="mb-12 text-4xl font-extrabold">
          AI가 분석하고, 합격까지 함께합니다
        </h2>

        <div className="grid w-full max-w-6xl grid-cols-3 gap-8">
          <FeatureCard
            icon="📘"
            title="자동 오답노트"
            desc="틀린 문제를 자동으로 저장하고 기출 연도별로 정리해줍니다."
          />
          <FeatureCard
            icon="🤖"
            title="AI 질문 & 해설"
            desc="이해되지 않는 문제는 AI에게 질문하고 해설을 받아볼 수 있습니다."
          />
          <FeatureCard
            icon="📊"
            title="약점 유형 분석"
            desc="자주 틀리는 단원과 유형을 분석해 학습 우선순위를 제안합니다."
          />
        </div>
      </section>

      {/* 3. 학습 흐름 섹션 */}
      <section className="flex min-h-screen flex-col items-center justify-center bg-blue-50 px-10">
        <span className="mb-4 rounded-full bg-blue-100 px-4 py-2 text-sm font-bold text-blue-600">
          학습 흐름
        </span>

        <h2 className="mb-16 text-4xl font-extrabold">
          PassMate AI와 함께하는 학습 과정
        </h2>

        <div className="grid w-full max-w-6xl grid-cols-5 gap-6 text-center">
          <StepCard number="1" icon="📝" title="기출문제 풀이" />
          <StepCard number="2" icon="✅" title="채점 및 결과 확인" />
          <StepCard number="3" icon="📘" title="오답 자동 저장" />
          <StepCard number="4" icon="🤖" title="AI 해설 질문" />
          <StepCard number="5" icon="📈" title="약점 유형 복습" />
        </div>
      </section>

      {isLoginOpen && (
        <LoginModal onClose={() => setIsLoginOpen(false)} />
      )}
    </main>
  );
}

function FeatureCard({
  icon,
  title,
  desc,
}: {
  icon: string;
  title: string;
  desc: string;
}) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-8 shadow-md transition hover:-translate-y-1 hover:shadow-xl">
      <div className="mb-6 text-6xl">{icon}</div>
      <h3 className="mb-3 text-xl font-bold">{title}</h3>
      <p className="leading-7 text-slate-600">{desc}</p>
>>>>>>> eff510979fffe13537d7e2ab6295319339ebe1c2
    </div>
  );
}
