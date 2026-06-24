export type SubjectAccuracy = {
  subject: string;
  total: number;
  correct: number;
  accuracy: number;
};

export type ExamResult = {
  examTitle: string;
  examType: string;
  round: string;
  totalCount: number;
  correctCount: number;
  wrongCount: number;
  score: number;
  accuracy: number;
  submittedAt: string;
  elapsedTime: string;
  averageTime: string;
  subjectStats: SubjectAccuracy[];
};