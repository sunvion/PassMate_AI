import { getExamQuestions } from "@/lib/examApi";

export type SingleStudyUnit = {
  id: string;
  name: string;
  questionCount: number;
  accuracy: number;
  wrongCount: number;
  examType: string;
  examName: string;
  subject: string;
  years: string[];
  icon:
    | "computer"
    | "os"
    | "database"
    | "network"
    | "data"
    | "code"
    | "software"
    | "term"
    | "traffic"
    | "safety";
  color: "blue" | "green" | "purple" | "orange" | "cyan" | "indigo" | "yellow";
};

export type SingleStudySubject = {
  id: string;
  name: string;
  examType: string;
  examName: string;
  years: string[];
  totalQuestionCount: number;
  units: SingleStudyUnit[];
};

export type SingleStudyExam = {
  id: string;
  name: string;
  examType: string;
  subjects: SingleStudySubject[];
};

const EXAM_CONFIG = [
  {
    id: "cs-general",
    name: "국가직 9급",
    examType: "CS_GENERAL",
    subjects: ["컴퓨터일반"],
    years: ["2026", "2025", "2024", "2023", "2022", "2021"],
  },
  {
    id: "cs-local",
    name: "지방직 9급",
    examType: "CS_LOCAL",
    subjects: ["컴퓨터일반"],
    years: ["2025", "2024", "2023", "2022", "2021"],
  },
  {
    id: "driver-license-1",
    name: "운전면허 1종",
    examType: "DRIVERS_LICENSE_1",
    subjects: ["운전면허 학과"],
    years: ["2026"],
  },
];

function getQuestionList(response: any) {
  if (Array.isArray(response)) return response;
  if (Array.isArray(response.questions)) return response.questions;
  if (Array.isArray(response.data)) return response.data;
  return [];
}

function getUnitName(question: any) {
  return (
    question.chapter ||
    question.unit ||
    question.category ||
    question.subject ||
    "전체 문제"
  );
}

function getIconAndColor(unitName: string): Pick<SingleStudyUnit, "icon" | "color"> {
  if (unitName.includes("구조")) return { icon: "computer", color: "blue" };
  if (unitName.includes("운영체제")) return { icon: "os", color: "green" };
  if (unitName.includes("데이터베이스")) return { icon: "database", color: "purple" };
  if (unitName.includes("네트워크")) return { icon: "network", color: "orange" };
  if (unitName.includes("자료")) return { icon: "data", color: "cyan" };
  if (unitName.includes("프로그래밍")) return { icon: "code", color: "indigo" };
  if (unitName.includes("소프트웨어")) return { icon: "software", color: "blue" };
  if (unitName.includes("교통")) return { icon: "traffic", color: "yellow" };
  if (unitName.includes("안전")) return { icon: "safety", color: "green" };

  return { icon: "term", color: "yellow" };
}

export async function getSingleStudyExams(): Promise<SingleStudyExam[]> {
  const exams: SingleStudyExam[] = [];

  for (const exam of EXAM_CONFIG) {
    const subjects: SingleStudySubject[] = [];

    for (const subject of exam.subjects) {
      const responses = await Promise.allSettled(
        exam.years.map((year) =>
          getExamQuestions({
            examType: exam.examType,
            subject,
            year,
            limit: 1000,
          })
        )
      );

      const questions = responses.flatMap((response) => {
        if (response.status !== "fulfilled") return [];
        return getQuestionList(response.value);
      });

      if (questions.length === 0) continue;

      const unitMap = new Map<string, any[]>();

      questions.forEach((question: any) => {
        const unitName = getUnitName(question);
        const prev = unitMap.get(unitName) ?? [];
        unitMap.set(unitName, [...prev, question]);
      });

      const units: SingleStudyUnit[] = Array.from(unitMap.entries()).map(
        ([unitName, unitQuestions], index) => {
          const { icon, color } = getIconAndColor(unitName);

          return {
            id: `${exam.examType}-${subject}-${unitName}-${index}`,
            name: unitName,
            questionCount: unitQuestions.length,
            accuracy: 0,
            wrongCount: 0,
            examType: exam.examType,
            examName: exam.name,
            subject,
            years: exam.years,
            icon,
            color,
          };
        }
      );

      subjects.push({
        id: `${exam.examType}-${subject}`,
        name: subject,
        examType: exam.examType,
        examName: exam.name,
        years: exam.years,
        totalQuestionCount: questions.length,
        units,
      });
    }

    if (subjects.length > 0) {
      exams.push({
        id: exam.id,
        name: exam.name,
        examType: exam.examType,
        subjects,
      });
    }
  }

  return exams;
}