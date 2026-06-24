// "오답노트 생성 완료!" 상단 문구
type ResultHeroProps = {
  examTitle: string;
  wrongCount: number;
};

export default function ResultHero({ examTitle, wrongCount }: ResultHeroProps) {
  const isPerfect = wrongCount === 0;

  return (
    <section className="text-center">
      <div className="mx-auto mb-5 flex h-24 w-24 items-center justify-center rounded-3xl bg-blue-100/80 shadow-inner">
        {isPerfect ? <PerfectScoreAnimation /> : <WrongNoteBookAnimation />}
      </div>

      <h1 className="text-4xl font-extrabold text-slate-900">
        {isPerfect ? (
          <>
            <span className="text-blue-600">전체 정답</span> 축하해요!
          </>
        ) : (
          <>
            <span className="text-blue-600">오답노트</span> 생성 완료!
          </>
        )}
      </h1>

      <p className="mt-4 text-lg font-medium text-slate-600">
        {isPerfect
          ? "틀린 문제가 없어 오답노트가 생성되지 않았습니다."
          : `총 ${wrongCount}개의 오답이 오답노트에 자동 저장되었습니다.`}
      </p>

      <div className="mx-auto mt-5 inline-flex rounded-full bg-blue-50 px-6 py-2 text-sm font-bold text-slate-700">
        {examTitle} 풀이 결과
      </div>
    </section>
  );
}

function WrongNoteBookAnimation() {
  return (
    <>
      <div className="book-wrap">
        <div className="book-shadow" />

        <div className="book">
          <div className="left-cover" />
          <div className="right-cover" />

          <div className="left-pages" />
          <div className="right-pages" />

          <div className="flip-page page-1" />
          <div className="flip-page page-2" />
          <div className="flip-page page-3" />
          <div className="flip-page page-4" />

          <div className="final-cover" />
          <div className="book-line" />
          <div className="book-side" />
        </div>

        <div className="pencil">
          <div className="pencil-eraser" />
          <div className="pencil-body" />
          <div className="pencil-tip" />
        </div>
      </div>

      <style jsx>{`
        .book-wrap {
          position: relative;
          width: 64px;
          height: 64px;
          perspective: 800px;
        }

        .book-shadow {
          position: absolute;
          bottom: 4px;
          left: 50%;
          width: 50px;
          height: 10px;
          border-radius: 999px;
          background: rgba(15, 23, 42, 0.16);
          filter: blur(5px);
          transform: translateX(-50%);
        }

        .book {
          position: absolute;
          left: 5px;
          top: 18px;
          width: 54px;
          height: 36px;
          transform-style: preserve-3d;
          animation: bookSettle 1.25s ease-in-out forwards;
        }

        .left-pages,
        .right-pages {
          position: absolute;
          top: 1px;
          width: 27px;
          height: 34px;
          background: linear-gradient(135deg, #ffffff 0%, #eef6ff 100%);
          border: 1px solid #dbeafe;
          box-shadow: 0 8px 14px rgba(37, 99, 235, 0.16);
        }

        .left-pages {
          left: 0;
          border-radius: 9px 3px 6px 9px;
          transform: rotateZ(-8deg);
          transform-origin: right center;
        }

        .right-pages {
          right: 0;
          border-radius: 3px 9px 9px 6px;
          transform: rotateZ(8deg);
          transform-origin: left center;
        }

        .left-cover,
        .right-cover {
          position: absolute;
          top: 0;
          width: 28px;
          height: 36px;
          background: linear-gradient(135deg, #60a5fa 0%, #2563eb 75%);
          box-shadow:
            0 10px 16px rgba(37, 99, 235, 0.25),
            inset 3px 0 5px rgba(255, 255, 255, 0.22);
          z-index: 1;
        }

        .left-cover {
          left: 0;
          border-radius: 10px 3px 6px 10px;
          transform-origin: right center;
          transform: rotateY(55deg) rotateZ(-8deg);
          animation: leftCoverClose 1.05s ease-in-out forwards;
          animation-delay: 0.35s;
        }

        .right-cover {
          right: 0;
          border-radius: 3px 10px 10px 6px;
          transform-origin: left center;
          transform: rotateY(-55deg) rotateZ(8deg);
          animation: rightCoverClose 1.05s ease-in-out forwards;
          animation-delay: 0.35s;
        }

        .flip-page {
          position: absolute;
          right: 2px;
          top: 1px;
          width: 27px;
          height: 33px;
          border-radius: 3px 8px 8px 4px;
          background: linear-gradient(135deg, #ffffff 0%, #eaf2ff 100%);
          border: 1px solid #dbeafe;
          box-shadow: 0 8px 14px rgba(37, 99, 235, 0.18);
          transform-origin: left center;
          z-index: 3;
          animation: flipPage 0.34s ease-in-out forwards;
        }

        .page-1 {
          animation-delay: 0.02s;
        }

        .page-2 {
          animation-delay: 0.14s;
        }

        .page-3 {
          animation-delay: 0.26s;
        }

        .page-4 {
          animation-delay: 0.38s;
        }

        .final-cover {
          position: absolute;
          left: 5px;
          top: 0;
          width: 44px;
          height: 38px;
          border-radius: 10px;
          background: linear-gradient(135deg, #60a5fa 0%, #2563eb 70%);
          box-shadow:
            0 12px 18px rgba(37, 99, 235, 0.32),
            inset 4px 0 6px rgba(255, 255, 255, 0.28),
            inset -3px -3px 5px rgba(30, 64, 175, 0.35);
          opacity: 0;
          transform: rotate(-7deg) scale(0.95);
          animation: finalCoverShow 0.35s ease-out forwards;
          animation-delay: 1.12s;
          z-index: 5;
        }

        .book-side {
          position: absolute;
          left: 9px;
          bottom: 1px;
          width: 36px;
          height: 7px;
          border-radius: 999px;
          background: rgba(255, 255, 255, 0.75);
          opacity: 0;
          animation: finalCoverShow 0.35s ease-out forwards;
          animation-delay: 1.12s;
          z-index: 6;
        }

        .book-line {
          position: absolute;
          left: 15px;
          top: 7px;
          width: 3px;
          height: 25px;
          border-radius: 999px;
          background: rgba(255, 255, 255, 0.35);
          opacity: 0;
          animation: finalCoverShow 0.35s ease-out forwards;
          animation-delay: 1.12s;
          z-index: 6;
        }

        .pencil {
          position: absolute;
          right: -2px;
          top: 8px;
          width: 12px;
          height: 48px;
          opacity: 0;
          transform: translateX(40px) rotate(35deg);
          filter: drop-shadow(0 8px 10px rgba(245, 158, 11, 0.3));
          animation: pencilSlide 0.7s ease-out forwards;
          animation-delay: 1.45s;
          z-index: 8;
        }

        .pencil-eraser {
          height: 9px;
          border-radius: 8px 8px 2px 2px;
          background: linear-gradient(135deg, #fb7185, #f43f5e);
        }

        .pencil-body {
          height: 31px;
          background: linear-gradient(90deg, #facc15 0%, #fde047 45%, #f59e0b 100%);
          border-radius: 2px;
        }

        .pencil-tip {
          width: 0;
          height: 0;
          border-left: 6px solid transparent;
          border-right: 6px solid transparent;
          border-top: 9px solid #1e293b;
        }

        @keyframes flipPage {
          0% {
            opacity: 1;
            transform: rotateY(0deg) rotateZ(8deg);
          }

          65% {
            opacity: 1;
            transform: rotateY(-120deg) rotateZ(-4deg);
          }

          100% {
            opacity: 0;
            transform: rotateY(-180deg) rotateZ(-8deg);
          }
        }

        @keyframes leftCoverClose {
          0% {
            transform: rotateY(55deg) rotateZ(-8deg);
          }

          100% {
            transform: rotateY(0deg) rotateZ(-7deg);
          }
        }

        @keyframes rightCoverClose {
          0% {
            transform: rotateY(-55deg) rotateZ(8deg);
          }

          100% {
            transform: rotateY(0deg) rotateZ(-7deg);
          }
        }

        @keyframes bookSettle {
          0% {
            transform: scale(1);
          }

          80% {
            transform: scale(1);
          }

          100% {
            transform: scale(1.02);
          }
        }

        @keyframes finalCoverShow {
          0% {
            opacity: 0;
          }

          100% {
            opacity: 1;
          }
        }

        @keyframes pencilSlide {
          0% {
            opacity: 0;
            transform: translateX(40px) rotate(35deg);
          }

          75% {
            opacity: 1;
            transform: translateX(-3px) rotate(35deg);
          }

          100% {
            opacity: 1;
            transform: translateX(0) rotate(35deg);
          }
        }
      `}</style>
    </>
  );
}

function PerfectScoreAnimation() {
  return (
    <>
      <div className="perfect-wrap">
        <div className="burst burst-1" />
        <div className="burst burst-2" />
        <div className="burst burst-3" />
        <div className="burst burst-4" />
        <div className="burst burst-5" />
        <div className="burst burst-6" />

        <div className="medal">
          <div className="medal-shine" />
          <span>✓</span>
        </div>
      </div>

      <style jsx>{`
        .perfect-wrap {
          position: relative;
          width: 64px;
          height: 64px;
        }

        .medal {
          position: absolute;
          left: 9px;
          top: 9px;
          width: 46px;
          height: 46px;
          border-radius: 50%;
          background: linear-gradient(135deg, #60a5fa 0%, #2563eb 70%);
          box-shadow:
            0 12px 18px rgba(37, 99, 235, 0.32),
            inset 4px 4px 8px rgba(255, 255, 255, 0.28);
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          font-size: 28px;
          font-weight: 900;
          transform: scale(0.3);
          animation: medalPop 0.75s cubic-bezier(0.2, 1.4, 0.4, 1) forwards;
        }

        .medal-shine {
          position: absolute;
          left: 10px;
          top: 8px;
          width: 13px;
          height: 8px;
          border-radius: 50%;
          background: rgba(255, 255, 255, 0.55);
          transform: rotate(-25deg);
        }

        .burst {
          position: absolute;
          left: 30px;
          top: 30px;
          width: 7px;
          height: 7px;
          border-radius: 999px;
          background: #facc15;
          opacity: 0;
          animation: burstOut 0.85s ease-out forwards;
          animation-delay: 0.18s;
        }

        .burst-1 {
          --x: 0px;
          --y: -28px;
          background: #60a5fa;
        }

        .burst-2 {
          --x: 24px;
          --y: -16px;
          background: #facc15;
        }

        .burst-3 {
          --x: 25px;
          --y: 14px;
          background: #fb7185;
        }

        .burst-4 {
          --x: 0px;
          --y: 28px;
          background: #38bdf8;
        }

        .burst-5 {
          --x: -25px;
          --y: 14px;
          background: #facc15;
        }

        .burst-6 {
          --x: -24px;
          --y: -16px;
          background: #fb7185;
        }

        @keyframes medalPop {
          0% {
            opacity: 0;
            transform: scale(0.3) rotate(-12deg);
          }

          70% {
            opacity: 1;
            transform: scale(1.12) rotate(4deg);
          }

          100% {
            opacity: 1;
            transform: scale(1) rotate(0deg);
          }
        }

        @keyframes burstOut {
          0% {
            opacity: 0;
            transform: translate(0, 0) scale(0.4);
          }

          40% {
            opacity: 1;
          }

          100% {
            opacity: 0;
            transform: translate(var(--x), var(--y)) scale(1);
          }
        }
      `}</style>
    </>
  );
}