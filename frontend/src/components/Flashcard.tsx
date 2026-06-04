import { useCallback, useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";
import type { CheckAnswerResponse, Gender, NounDetails, VerbDetails, Word } from "../types";

interface FlashcardProps {
  word: Word;
  feedback: CheckAnswerResponse | null;
  choiceOptions: string[];
  isChecking?: boolean;
  onCheck: (answer: string) => Promise<void> | void;
  onNext: () => Promise<void> | void;
}

const genderStyles: Record<Gender, string> = {
  der: "border-blue-400 bg-blue-50/70",
  die: "border-rose-400 bg-rose-50/70",
  das: "border-emerald-400 bg-emerald-50/70",
};

const taskCopy = {
  direct_translation: {
    eyebrow: "Выбери перевод",
    title: "Что значит это слово?",
    inputLabel: "",
    placeholder: "",
  },
  reverse_translation: {
    eyebrow: "Переведи на немецкий",
    title: "Введи немецкое слово",
    inputLabel: "Немецкий ответ",
    placeholder: "Например: der Tisch или Tisch",
  },
  fill_blank: {
    eyebrow: "Заполни пропуск",
    title: "Какое слово пропущено?",
    inputLabel: "Пропущенное слово",
    placeholder: "Введите слово, которое подходит по смыслу",
  },
} as const;

function getNounDetails(word: Word): NounDetails | null {
  return word.noun_detail ?? word.noun_details ?? null;
}

function getVerbDetails(word: Word): VerbDetails | null {
  return word.verb_detail ?? word.verb_details ?? null;
}

function getPrimaryTranslation(translation: string): string {
  return translation
    .split(/[;,]/)
    .map((part) => part.replace(/\(.*?\)/g, "").trim())
    .find(Boolean) ?? translation.trim();
}

function renderBlankSentence(sentence: string) {
  const parts = sentence.split("___");

  if (parts.length === 1) {
    return sentence;
  }

  return parts.map((part, index) => (
    <span key={`${part}-${index}`}>
      {part}
      {index < parts.length - 1 && (
        <span className="mx-1 inline-flex min-w-24 justify-center rounded-md border-b-4 border-emerald-400 bg-emerald-50 px-4 py-1 text-emerald-700">
          ___
        </span>
      )}
    </span>
  ));
}

export default function Flashcard({
  word,
  feedback,
  choiceOptions,
  isChecking = false,
  onCheck,
  onNext,
}: FlashcardProps) {
  const [answer, setAnswer] = useState("");
  const [selectedChoice, setSelectedChoice] = useState<string | null>(null);

  const nounDetails = useMemo(() => getNounDetails(word), [word]);
  const verbDetails = useMemo(() => getVerbDetails(word), [word]);
  const isMultipleChoice = word.task_type === "direct_translation";
  const correctChoice = useMemo(() => getPrimaryTranslation(word.translation), [word.translation]);
  const copy = taskCopy[word.task_type];

  useEffect(() => {
    setAnswer("");
    setSelectedChoice(null);
  }, [word.id, word.task_type]);

  const cardTone = useMemo(() => {
    if (word.word_type === "noun" && nounDetails?.gender) {
      return genderStyles[nounDetails.gender];
    }

    return "border-slate-200 bg-white";
  }, [nounDetails?.gender, word.word_type]);

  const prompt = useMemo(() => {
    if (word.task_type === "fill_blank") {
      const sentence =
        (word.blank_sentence?.includes("___") && word.blank_sentence) ||
        (word.example_sentence?.includes(word.german) &&
          word.example_sentence.replace(word.german, "___")) ||
        (word.blank_sentence && `${word.blank_sentence} ___`) ||
        (word.example_sentence && `${word.example_sentence} ___`) ||
        `___ (${word.translation})`;

      return (
        <div>
          <p className="mx-auto max-w-xl text-3xl font-black leading-tight text-slate-950 sm:text-4xl">
            {renderBlankSentence(sentence)}
          </p>
          <p className="mt-4 text-sm font-semibold text-slate-500">
            Значение пропущенного слова: {word.translation}
          </p>
        </div>
      );
    }

    if (word.task_type === "reverse_translation") {
      return (
        <div>
          <h2 className="text-5xl font-black leading-none text-slate-950 sm:text-6xl">
            {getPrimaryTranslation(word.translation)}
          </h2>
          {getPrimaryTranslation(word.translation) !== word.translation && (
            <p className="mt-3 text-base font-medium text-slate-500">{word.translation}</p>
          )}
        </div>
      );
    }

    return (
      <h2 className="text-6xl font-black leading-none text-slate-950 sm:text-7xl">
        {word.german}
      </h2>
    );
  }, [word]);

  const handleSubmit = useCallback(
    async (event: FormEvent<HTMLFormElement>) => {
      event.preventDefault();

      const trimmedAnswer = answer.trim();
      if (!trimmedAnswer || isChecking || feedback) {
        return;
      }

      await onCheck(trimmedAnswer);
    },
    [answer, feedback, isChecking, onCheck],
  );

  const handleChoiceClick = useCallback(
    async (choice: string) => {
      if (feedback || isChecking) {
        return;
      }

      setSelectedChoice(choice);
      await onCheck(choice);
    },
    [feedback, isChecking, onCheck],
  );

  const handleNext = useCallback(async () => {
    setAnswer("");
    setSelectedChoice(null);
    await onNext();
  }, [onNext]);

  const getChoiceClassName = useCallback(
    (choice: string) => {
      const base =
        "min-h-16 rounded-lg border-2 px-4 py-3 text-left text-lg font-bold shadow-sm transition duration-200";

      if (!feedback) {
        return `${base} border-slate-200 bg-white text-slate-900 hover:-translate-y-0.5 hover:border-emerald-300 hover:bg-emerald-50 hover:shadow-md`;
      }

      if (choice === selectedChoice && feedback.correct) {
        return `${base} border-emerald-500 bg-emerald-100 text-emerald-950 shadow-emerald-100`;
      }

      if (choice === selectedChoice && !feedback.correct) {
        return `${base} border-rose-500 bg-rose-100 text-rose-950 shadow-rose-100`;
      }

      if (choice === correctChoice) {
        return `${base} border-emerald-400 bg-emerald-50 text-emerald-950`;
      }

      return `${base} border-slate-200 bg-slate-50 text-slate-400`;
    },
    [correctChoice, feedback, selectedChoice],
  );

  return (
    <article
      className={`mx-auto w-full max-w-3xl rounded-2xl border-2 p-5 shadow-xl shadow-slate-200/70 sm:p-8 ${cardTone}`}
    >
      <div className="mb-8 flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap gap-2">
          {word.category && (
            <span className="rounded-full bg-white px-3 py-1 text-sm font-bold text-slate-700 shadow-sm">
              {word.category}
            </span>
          )}

          {word.level && (
            <span className="rounded-full bg-slate-950 px-3 py-1 text-sm font-black text-white shadow-sm">
              {word.level}
            </span>
          )}

          {word.word_type === "noun" && nounDetails?.gender && (
            <span className="rounded-full bg-white px-3 py-1 text-sm font-black text-slate-950 shadow-sm">
              {nounDetails.gender}
            </span>
          )}
        </div>

        <span className="rounded-full bg-white/80 px-3 py-1 text-sm font-bold text-slate-500 shadow-sm">
          {copy.eyebrow}
        </span>
      </div>

      <section className="mb-8 text-center">
        <p className="mb-4 text-sm font-black uppercase tracking-wider text-slate-500">{copy.title}</p>
        {prompt}
      </section>

      {isMultipleChoice ? (
        <div className="grid gap-3 sm:grid-cols-2">
          {choiceOptions.map((choice) => (
            <button
              key={choice}
              type="button"
              onClick={() => void handleChoiceClick(choice)}
              disabled={isChecking || Boolean(feedback)}
              className={getChoiceClassName(choice)}
            >
              {choice}
            </button>
          ))}
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4">
          <label className="block">
            <span className="mb-2 block text-sm font-bold text-slate-700">{copy.inputLabel}</span>
            <input
              value={answer}
              onChange={(event) => setAnswer(event.target.value)}
              disabled={isChecking || Boolean(feedback)}
              placeholder={copy.placeholder}
              className="w-full rounded-xl border-2 border-slate-200 bg-white px-5 py-4 text-lg font-semibold text-slate-950 outline-none transition focus:border-emerald-400 focus:ring-4 focus:ring-emerald-100 disabled:cursor-not-allowed disabled:bg-slate-100"
            />
          </label>

          <button
            type="submit"
            disabled={isChecking || Boolean(feedback) || !answer.trim()}
            className="w-full rounded-xl bg-emerald-500 px-5 py-4 text-lg font-black text-white shadow-lg shadow-emerald-200 transition hover:-translate-y-0.5 hover:bg-emerald-600 disabled:translate-y-0 disabled:cursor-not-allowed disabled:bg-slate-300 disabled:shadow-none"
          >
            {isChecking ? "Проверяем..." : "Проверить"}
          </button>
        </form>
      )}

      {feedback && (
        <section
          className={`mt-6 rounded-2xl border-2 p-5 ${
            feedback.correct
              ? "border-emerald-300 bg-emerald-50 text-emerald-950"
              : "border-rose-300 bg-rose-50 text-rose-950"
          }`}
        >
          <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <h3 className="text-2xl font-black">
                {feedback.correct ? "Отлично!" : "Почти. Запоминаем правильный вариант"}
              </h3>
              <p className="mt-2 font-semibold">{feedback.message}</p>
            </div>

            <button
              type="button"
              onClick={() => void handleNext()}
              className="rounded-xl bg-slate-950 px-5 py-3 font-black text-white shadow-lg shadow-slate-200 transition hover:-translate-y-0.5 hover:bg-slate-800"
            >
              Следующее слово
            </button>
          </div>

          <dl className="mt-5 grid gap-3 sm:grid-cols-2">
            <div className="rounded-xl bg-white p-4 shadow-sm">
              <dt className="text-sm font-bold text-slate-500">Правильный ответ</dt>
              <dd className="mt-1 text-lg font-black text-slate-950">{feedback.correct_answer}</dd>
            </div>

            <div className="rounded-xl bg-white p-4 shadow-sm">
              <dt className="text-sm font-bold text-slate-500">Перевод</dt>
              <dd className="mt-1 text-lg font-black text-slate-950">{feedback.translation}</dd>
            </div>
          </dl>

          {word.word_type === "verb" && verbDetails && (
            <div className="mt-4 rounded-xl bg-white p-4 shadow-sm">
              <h4 className="font-black text-slate-950">Три формы глагола</h4>
              <div className="mt-3 grid gap-3 sm:grid-cols-3">
                <div>
                  <p className="text-sm font-bold text-slate-500">Infinitiv</p>
                  <p className="text-lg font-black text-slate-950">{word.german}</p>
                </div>
                <div>
                  <p className="text-sm font-bold text-slate-500">Präteritum</p>
                  <p className="text-lg font-black text-slate-950">{verbDetails.praeteritum}</p>
                </div>
                <div>
                  <p className="text-sm font-bold text-slate-500">Perfekt</p>
                  <p className="text-lg font-black text-slate-950">
                    {verbDetails.auxiliary} {verbDetails.perfekt}
                  </p>
                </div>
              </div>
            </div>
          )}

          {word.word_type === "noun" && nounDetails && (
            <div className="mt-4 rounded-xl bg-white p-4 shadow-sm">
              <h4 className="font-black text-slate-950">Существительное</h4>
              <div className="mt-3 grid gap-3 sm:grid-cols-2">
                <div>
                  <p className="text-sm font-bold text-slate-500">Артикль</p>
                  <p className="text-lg font-black text-slate-950">{nounDetails.gender}</p>
                </div>
                <div>
                  <p className="text-sm font-bold text-slate-500">Множественное число</p>
                  <p className="text-lg font-black text-slate-950">
                    {nounDetails.plural ?? "нет данных"}
                  </p>
                </div>
              </div>
            </div>
          )}
        </section>
      )}
    </article>
  );
}
