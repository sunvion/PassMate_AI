"use client";

import Header from "@/components/Header";
import Sidebar from "@/components/Sidebar";
import {
    askWrongNoteAI,
    getWrongNotebookDetail,
    WrongNotebookDetail,
    WrongNoteChatMessage,
    WrongNoteQuestion,
} from "@/lib/wrongNoteApi";
import { Bot, Loader2, RotateCcw, Send } from "lucide-react";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

function getExamTypeLabel(examType: string) {
    switch (examType) {
        case "CS_GENERAL":
            return "국가직";
        case "CS_LOCAL":
            return "지방직";
        case "DRIVERS_LICENSE_1":
        case "DRIVERS_LICENSE_2":
            return "운전면허 필기";
        default:
            return examType;
    }
}

function isDriverLicense(examType: string) {
    return examType.startsWith("DRIVERS_LICENSE");
}

function getWrongNoteTitle(note: WrongNotebookDetail) {
    const examLabel = getExamTypeLabel(note.exam_type);

    if (isDriverLicense(note.exam_type)) {
        return `${examLabel} 오답노트`;
    }

    return `${note.year} ${examLabel} ${note.subject} 오답노트`;
}

export default function WrongNotebookDetailPage() {
    const router = useRouter();
    const params = useParams<{ wrongNotebookId: string }>();
    const wrongNotebookId = Number(params.wrongNotebookId);

    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const [notebook, setNotebook] = useState<WrongNotebookDetail | null>(null);
    const [selectedQuestion, setSelectedQuestion] =
        useState<WrongNoteQuestion | null>(null);

    const [isLoading, setIsLoading] = useState(true);
    const [isAiLoading, setIsAiLoading] = useState(false);
    const [chatInput, setChatInput] = useState("");

    // 문제별 AI 대화 저장
    const [chatHistory, setChatHistory] = useState<
        Record<number, WrongNoteChatMessage[]>
    >({});

    const chatMessages = selectedQuestion
        ? chatHistory[selectedQuestion.question_id] ?? []
        : [];

    useEffect(() => {
        async function fetchDetail() {
            if (!wrongNotebookId) return;

            try {
                const data = await getWrongNotebookDetail(wrongNotebookId);
                const items = data.items ?? [];

                setNotebook({ ...data, items });
                setSelectedQuestion(items[0] ?? null);
            } catch (error) {
                console.error(error);
                alert("오답노트 상세를 불러오지 못했습니다.");
            } finally {
                setIsLoading(false);
            }
        }

        fetchDetail();
    }, [wrongNotebookId]);

    const handleSelectQuestion = (question: WrongNoteQuestion) => {
        setSelectedQuestion(question);
        setChatInput("");
    };

    const handleResetChat = () => {
        if (!selectedQuestion) return;

        setChatHistory((prev) => ({
            ...prev,
            [selectedQuestion.question_id]: [],
        }));

        setChatInput("");
    };

    const handleSendMessage = async () => {
        if (!selectedQuestion || !chatInput.trim()) return;

        const questionId = selectedQuestion.question_id;
        const message = chatInput.trim();

        const userMessage: WrongNoteChatMessage = {
            role: "user",
            content: message,
        };

        setChatHistory((prev) => ({
            ...prev,
            [questionId]: [...(prev[questionId] ?? []), userMessage],
        }));

        setChatInput("");

        try {
            setIsAiLoading(true);

            const result = await askWrongNoteAI({
                questionId,
                message,
            });

            const aiMessage: WrongNoteChatMessage = {
                role: "assistant",
                content: result.answer,
            };

            setChatHistory((prev) => ({
                ...prev,
                [questionId]: [...(prev[questionId] ?? []), aiMessage],
            }));
        } catch (error) {
            console.error(error);

            setChatHistory((prev) => ({
                ...prev,
                [questionId]: [
                    ...(prev[questionId] ?? []),
                    {
                        role: "assistant",
                        content: "AI 답변을 불러오지 못했습니다. 잠시 후 다시 시도해주세요.",
                    },
                ],
            }));
        } finally {
            setIsAiLoading(false);
        }
    };

    return (
        <main className="min-h-screen bg-slate-50">
            <Header onMenuClick={() => setIsMenuOpen(true)} onLoginClick={() => { }} />
            <Sidebar isOpen={isMenuOpen} onClose={() => setIsMenuOpen(false)} />

            <section className="mx-auto max-w-6xl px-8 pt-28 pb-10">
                {isLoading ? (
                    <div className="flex h-[600px] items-center justify-center rounded-2xl border border-slate-200 bg-white text-slate-500">
                        <Loader2 className="mr-2 animate-spin" size={20} />
                        오답노트를 불러오는 중...
                    </div>
                ) : !notebook ? (
                    <div className="rounded-2xl border border-slate-200 bg-white py-20 text-center">
                        <p className="text-lg font-bold text-slate-700">
                            오답노트를 찾을 수 없습니다.
                        </p>
                    </div>
                ) : (
                    <>
                        <div className="mb-8 flex items-start justify-between">
                            <div>
                                <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-slate-500">
                                    <span>마이페이지</span>
                                    <span>›</span>
                                    <span>오답노트</span>
                                    <span>›</span>
                                    <span className="text-slate-900">상세</span>
                                </div>

                                <h1 className="text-3xl font-bold text-slate-900">
                                    {getWrongNoteTitle(notebook)}
                                </h1>

                                <p className="mt-2 text-slate-500">
                                    틀린 문제와 미풀이 문제를 확인하고 AI에게 바로 질문해보세요.
                                </p>
                            </div>

                            <button
                                type="button"
                                onClick={() => router.push("/wrong-note")}
                                className="rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-600 transition hover:border-blue-500 hover:text-blue-600"
                            >
                                ← 오답노트 목록
                            </button>
                        </div>

                        <div className="space-y-5">
                            {/* 문제 목록: 위 가로 스크롤 */}
                            <section className="rounded-2xl border border-slate-200 bg-white p-5">
                                <div className="mb-4 flex items-center justify-between">
                                    <h2 className="font-bold text-slate-900">
                                        문제 목록 ({notebook.items.length})
                                    </h2>
                                    <p className="text-xs text-slate-400">
                                        문제를 클릭하면 아래 상세 영역이 바뀝니다.
                                    </p>
                                </div>

                                <div className="flex gap-3 overflow-x-auto pb-2">
                                    {notebook.items.map((question, index) => {
                                        const isSelected =
                                            selectedQuestion?.question_id === question.question_id;

                                        return (
                                            <button
                                                key={question.question_id}
                                                type="button"
                                                onClick={() => handleSelectQuestion(question)}
                                                className={`min-w-[220px] rounded-2xl border p-4 text-left transition ${isSelected
                                                    ? "border-blue-500 bg-blue-50"
                                                    : "border-slate-200 bg-white hover:border-blue-300"
                                                    }`}
                                            >
                                                <div className="mb-3 flex items-center justify-between">
                                                    <span className="text-sm font-bold text-slate-900">
                                                        문제 {index + 1}
                                                    </span>

                                                    <span
                                                        className={`rounded-md px-2 py-1 text-xs font-bold ${question.status === "unsolved"
                                                            ? "bg-orange-50 text-orange-500"
                                                            : "bg-red-50 text-red-500"
                                                            }`}
                                                    >
                                                        {question.status === "unsolved" ? "미풀이" : "오답"}
                                                    </span>
                                                </div>

                                                <p className="line-clamp-2 text-xs leading-5 text-slate-600">
                                                    {question.question}
                                                </p>
                                            </button>
                                        );
                                    })}
                                </div>
                            </section>

                            <div className="grid grid-cols-12 gap-5">
                                {/* 문제 상세: 넓게 */}
                                <section className="col-span-8 rounded-2xl border border-slate-200 bg-white p-7">
                                    <h2 className="mb-6 font-bold text-slate-900">문제 상세</h2>

                                    {!selectedQuestion ? (
                                        <p className="py-28 text-center text-slate-400">
                                            문제를 선택해주세요.
                                        </p>
                                    ) : (
                                        <div>
                                            {/* 문제 이미지 */}
                                            {selectedQuestion.image_url ? (
                                                <div className="mb-6 rounded-2xl border border-slate-200 bg-slate-50 p-4">
                                                    <img
                                                        src={selectedQuestion.image_url}
                                                        alt="문제 이미지"
                                                        className="w-full rounded-xl border border-slate-200 bg-white"
                                                    />
                                                </div>
                                            ) : (
                                                // 이미지가 없는 문제만 텍스트 출력
                                                <p className="mb-6 whitespace-pre-line text-lg font-bold leading-9 text-slate-900">
                                                    Q. {selectedQuestion.question}
                                                </p>
                                            )}

                                            <div className="space-y-3">
                                                {Object.entries(selectedQuestion.options).map(
                                                    ([key, value]) => {
                                                        const choiceNumber = Number(key);
                                                        const isMyAnswer =
                                                            selectedQuestion.selected_option.includes(
                                                                choiceNumber
                                                            );
                                                        const isCorrect =
                                                            selectedQuestion.correct_answer.includes(
                                                                choiceNumber
                                                            );

                                                        return (
                                                            <div
                                                                key={choiceNumber}
                                                                className={`rounded-xl border px-5 py-4 text-sm leading-7 ${isCorrect
                                                                    ? "border-emerald-200 bg-emerald-50 text-emerald-700"
                                                                    : isMyAnswer
                                                                        ? "border-red-200 bg-red-50 text-red-600"
                                                                        : "border-slate-200 bg-white text-slate-700"
                                                                    }`}
                                                            >
                                                                <span className="font-bold">{choiceNumber}.</span>{" "}
                                                                {value}
                                                            </div>
                                                        );
                                                    }
                                                )}
                                            </div>

                                            <div className="mt-6 grid grid-cols-2 gap-3">
                                                <div className="rounded-2xl border border-red-100 bg-red-50 p-5 text-sm">
                                                    <p className="mb-1 font-bold text-red-500">
                                                        내가 선택한 답
                                                    </p>
                                                    <p className="font-semibold text-red-700">
                                                        {selectedQuestion.selected_option.length > 0
                                                            ? selectedQuestion.selected_option.join(", ")
                                                            : "미선택"}
                                                    </p>
                                                </div>

                                                <div className="rounded-2xl border border-emerald-100 bg-emerald-50 p-5 text-sm">
                                                    <p className="mb-1 font-bold text-emerald-600">정답</p>
                                                    <p className="font-semibold text-emerald-700">
                                                        {selectedQuestion.correct_answer.join(", ")}
                                                    </p>
                                                </div>
                                            </div>
                                        </div>
                                    )}
                                </section>

                                {/* AI 튜터 */}
                                <section className="col-span-4 rounded-2xl border border-slate-200 bg-white p-5">
                                    <div className="mb-5 flex items-center justify-between">
                                        <div className="flex items-center gap-2">
                                            <Bot className="text-blue-600" size={22} />
                                            <h2 className="font-bold text-slate-900">AI 튜터</h2>
                                        </div>

                                        <button
                                            type="button"
                                            onClick={handleResetChat}
                                            disabled={!selectedQuestion}
                                            className="flex items-center gap-1 rounded-xl border border-slate-200 px-3 py-2 text-xs font-semibold text-slate-600 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
                                        >
                                            <RotateCcw size={14} />새 대화
                                        </button>
                                    </div>

                                    <div className="flex h-[680px] flex-col">
                                        <div className="flex-1 space-y-3 overflow-y-auto rounded-2xl bg-slate-50 p-4">
                                            <div className="mr-10 rounded-2xl bg-white p-4 text-sm leading-6 text-slate-600 shadow-sm">
                                                안녕하세요! 😊
                                                <br />이 문제에 대해 궁금한 점을 물어보세요.
                                            </div>

                                            {chatMessages.map((message, index) => (
                                                <div
                                                    key={index}
                                                    className={`rounded-2xl p-4 text-sm leading-6 ${message.role === "user"
                                                        ? "ml-10 bg-blue-600 text-white"
                                                        : "mr-10 bg-white text-slate-700 shadow-sm"
                                                        }`}
                                                >
                                                    {message.content}
                                                </div>
                                            ))}

                                            {isAiLoading && (
                                                <div className="mr-10 rounded-2xl bg-white p-4 text-sm text-slate-400 shadow-sm">
                                                    AI가 답변을 작성 중입니다...
                                                </div>
                                            )}
                                        </div>

                                        <div className="mt-4 flex gap-2">
                                            <input
                                                value={chatInput}
                                                onChange={(e) => setChatInput(e.target.value)}
                                                onKeyDown={(e) => {
                                                    if (e.key === "Enter") {
                                                        handleSendMessage();
                                                    }
                                                }}
                                                disabled={!selectedQuestion || isAiLoading}
                                                placeholder="질문을 입력하세요..."
                                                className="min-w-0 flex-1 rounded-xl border border-slate-200 px-4 py-3 text-sm outline-none focus:border-blue-500"
                                            />

                                            <button
                                                type="button"
                                                onClick={handleSendMessage}
                                                disabled={!selectedQuestion || isAiLoading}
                                                className="rounded-xl bg-blue-600 px-5 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
                                            >
                                                <Send size={17} />
                                            </button>
                                        </div>
                                    </div>
                                </section>
                            </div>
                        </div>
                    </>
                )}
            </section>
        </main>
    );
}