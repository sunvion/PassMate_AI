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