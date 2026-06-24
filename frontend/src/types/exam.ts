export type Choice = {
  id: number;
  number: number;
  text?: string | null;
  imageUrl?: string | null;
};

export type Question = {
  id: number;
  number: number;
  text: string;
  imageUrl?: string | null;
  explanation?: string | null;
  answer: number[];
  choices: Choice[];
};

export type ExamQuestionsResponse = {
  examId: number;
  title: string;
  questions: Question[];
};

export type SelectedAnswers = {
  [questionId: number]: number;
};