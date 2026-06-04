import { useMemo, useState } from "react";
import type { FormEvent } from "react";
import type { CheckAnswerResponse, Gender, NounDetails, VerbDetails, Word } from "../types";

interface FlashcardProps {
  word: Word;
  feedback: CheckAnswerResponse | null;
  isChecking?: boolean;
  onCheck: (answer: string) => Promise<void> | void;
  onNext: () => Promise<void> | void;
}

const genderStyles: Record<Gender, string> = {
  der: "border-blue-500 bg-blue-50",
  die: "border-rose-500 bg-rose-50",
  das: "border-emerald-500 bg-emerald-50",
};

const genderLabels: Record<Gender, string> = {
  der: "der",
  die: "die",
  das: "das",
};

function getNounDetails(word: Word): NounDetails | null {
  return word.noun_detail ?? word.noun_details ?? null;
}

function getVerbDetails(word: Word): VerbDetails | null {
  return word.verb_detail ?? word.verb_details ?? null;
}

export default function Flashcard({
  word,
  feedback,
  isChecking = false,
  onCheck,
  onNext,
}: FlashcardProps) {
  const [answer, setAnswer] = useState("");
  const nounDetails = getNounDetails(word);
  const verbDetails = getVerbDetails(word);

  const cardTone = useMemo(() => {
    if (word.word_type === "noun" && nounDetails?.gender) {
      return genderStyles[nounDetails.gender];
    }

    return "border-slate-200 bg-white";
  }, [nounDetails?.gender, word.word_type]);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const trimmedAnswer = answer.trim();
    if (!trimmedAnswer || isChecking || feedback) {
      return;
    }

    await onCheck(trimmedAnswer);
  };

  const handleNext = async () => {
    setAnswer("");
    await onNext();
  };

  return (
    <article className={`mx-auto w-full max-w-2xl rounded-lg border-2 p-6 shadow-sm ${cardTone}`}>
      <div className="mb-6 flex flex-wrap items-center gap-2">
        {word.category && (
          <span className="rounded-full bg-white/80 px-3 py-1 text-sm font-medium text-slate-700 shadow-sm">
            {word.category}
          </span>
        )}

        {word.level && (
          <span className="rounded-full bg-slate-900 px-3 py-1 text-sm font-semibold text-white shadow-sm">
            {word.level}
          </span>
        )}

        {word.word_type === "noun" && nounDetails?.gender && (
          <span className="rounded-full bg-white px-3 py-1 text-sm font-semibold text-slate-900 shadow-sm">
            {genderLabels[nounDetails.gender]}
          </span>
        )}
      </div>

      <div className="mb-8 text-center">
        <p className="mb-2 text-sm font-medium uppercase tracking-wide text-slate-500">
          Переведите слово
        </p>
        <h1 className="text-5xl font-bold text-slate-950 sm:text-6xl">{word.german}</h1>

        {word.example_sentence && (
          <p className="mt-5 rounded-md bg-white/70 px-4 py-3 text-left text-base text-slate-700">
            {word.example_sentence}
          </p>
        )}
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <label className="block">
          <span className="mb-2 block text-sm font-medium text-slate-700">Ваш ответ</span>
          <input
            value={answer}
            onChange={(event) => setAnswer(event.target.value)}
            disabled={isChecking || Boolean(feedback)}
            placeholder="Например: стол, der Tisch, gegangen..."
            className="w-full rounded-md border border-slate-300 bg-white px-4 py-3 text-lg text-slate-950 outline-none transition focus:border-slate-900 focus:ring-4 focus:ring-slate-200 disabled:cursor-not-allowed disabled:bg-slate-100"
          />
        </label>

        <button
          type="submit"
          disabled={isChecking || Boolean(feedback) || !answer.trim()}
          className="w-full rounded-md bg-slate-950 px-5 py-3 font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-400"
        >
          {isChecking ? "Проверяем..." : "Проверить"}
        </button>
      </form>

      {feedback && (
        <section
          className={`mt-6 rounded-lg border p-5 ${
            feedback.correct
              ? "border-emerald-200 bg-emerald-50 text-emerald-950"
              : "border-rose-200 bg-rose-50 text-rose-950"
          }`}
        >
          <h2 className="text-xl font-bold">{feedback.correct ? "Правильно!" : "Пока неверно"}</h2>
          <p className="mt-2">{feedback.message}</p>

          <dl className="mt-4 grid gap-3 sm:grid-cols-2">
            <div className="rounded-md bg-white/80 p-3">
              <dt className="text-sm font-medium text-slate-500">Правильный ответ</dt>
              <dd className="mt-1 font-semibold text-slate-950">{feedback.correct_answer}</dd>
            </div>

            <div className="rounded-md bg-white/80 p-3">
              <dt className="text-sm font-medium text-slate-500">Перевод</dt>
              <dd className="mt-1 font-semibold text-slate-950">{feedback.translation}</dd>
            </div>
          </dl>

          {word.word_type === "verb" && verbDetails && (
            <div className="mt-4 rounded-md bg-white/80 p-4">
              <h3 className="font-semibold text-slate-950">Три формы глагола</h3>
              <div className="mt-3 grid gap-3 sm:grid-cols-3">
                <div>
                  <p className="text-sm text-slate-500">Infinitiv</p>
                  <p className="font-semibold text-slate-950">{word.german}</p>
                </div>
                <div>
                  <p className="text-sm text-slate-500">Präteritum</p>
                  <p className="font-semibold text-slate-950">{verbDetails.praeteritum}</p>
                </div>
                <div>
                  <p className="text-sm text-slate-500">Perfekt</p>
                  <p className="font-semibold text-slate-950">
                    {verbDetails.auxiliary} {verbDetails.perfekt}
                  </p>
                </div>
              </div>
            </div>
          )}

          {word.word_type === "noun" && nounDetails && (
            <div className="mt-4 rounded-md bg-white/80 p-4">
              <h3 className="font-semibold text-slate-950">Существительное</h3>
              <div className="mt-3 grid gap-3 sm:grid-cols-2">
                <div>
                  <p className="text-sm text-slate-500">Артикль</p>
                  <p className="font-semibold text-slate-950">{nounDetails.gender}</p>
                </div>
                <div>
                  <p className="text-sm text-slate-500">Множественное число</p>
                  <p className="font-semibold text-slate-950">{nounDetails.plural ?? "нет данных"}</p>
                </div>
              </div>
            </div>
          )}

          <button
            type="button"
            onClick={handleNext}
            className="mt-5 w-full rounded-md bg-white px-5 py-3 font-semibold text-slate-950 shadow-sm transition hover:bg-slate-50"
          >
            Следующее слово
          </button>
        </section>
      )}
    </article>
  );
}
