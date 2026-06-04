import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import Flashcard from "./components/Flashcard";
import MatchingGame from "./components/MatchingGame";
import type { CheckAnswerResponse, Word } from "./types";

type TrainerMode = "cards" | "matching";

const FALLBACK_TRANSLATIONS = [
  "дом",
  "стол",
  "книга",
  "вода",
  "идти",
  "делать",
  "говорить",
  "учиться",
  "машина",
  "школа",
  "ребенок",
  "улица",
];

const modes: Array<{ id: TrainerMode; label: string; description: string }> = [
  {
    id: "cards",
    label: "Карточки",
    description: "Перевод, пропуски и быстрые варианты",
  },
  {
    id: "matching",
    label: "Соединить пары",
    description: "Найди немецко-русские пары",
  },
];

function getPrimaryTranslation(translation: string): string {
  return translation
    .split(/[;,]/)
    .map((part) => part.replace(/\(.*?\)/g, "").trim())
    .find(Boolean) ?? translation.trim();
}

function appendUniqueWords(base: Word[], incoming: Word[]): Word[] {
  const map = new Map<number, Word>();

  for (const word of [...base, ...incoming]) {
    map.set(word.id, word);
  }

  return Array.from(map.values()).slice(-40);
}

function shuffle<T>(items: T[]): T[] {
  return [...items].sort(() => Math.random() - 0.5);
}

function buildChoiceOptions(word: Word, pool: Word[]): string[] {
  const correct = getPrimaryTranslation(word.translation);
  const used = new Set([correct.toLowerCase()]);

  const distractors = pool
    .filter((candidate) => candidate.id !== word.id)
    .map((candidate) => getPrimaryTranslation(candidate.translation))
    .filter((translation) => {
      const key = translation.toLowerCase();
      if (!translation || used.has(key)) {
        return false;
      }

      used.add(key);
      return true;
    });

  for (const fallback of FALLBACK_TRANSLATIONS) {
    if (distractors.length >= 3) {
      break;
    }

    const key = fallback.toLowerCase();
    if (!used.has(key)) {
      used.add(key);
      distractors.push(fallback);
    }
  }

  return shuffle([correct, ...distractors.slice(0, 3)]);
}

async function fetchRandomWord(): Promise<Word> {
  const response = await fetch("/vocab/random");

  if (!response.ok) {
    throw new Error("Не удалось загрузить слово");
  }

  return response.json();
}

async function fetchDistractorPool(count = 8): Promise<Word[]> {
  const results = await Promise.allSettled(Array.from({ length: count }, () => fetchRandomWord()));

  return results.flatMap((result) => (result.status === "fulfilled" ? [result.value] : []));
}

export default function App() {
  const [activeMode, setActiveMode] = useState<TrainerMode>("cards");
  const [word, setWord] = useState<Word | null>(null);
  const [feedback, setFeedback] = useState<CheckAnswerResponse | null>(null);
  const [choiceOptions, setChoiceOptions] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isChecking, setIsChecking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [streak, setStreak] = useState(0);
  const [answeredCount, setAnsweredCount] = useState(0);

  const wordPoolRef = useRef<Word[]>([]);

  const miniStreakProgress = useMemo(() => {
    if (streak > 0 && streak % 5 === 0) {
      return 100;
    }

    return (streak % 5) * 20;
  }, [streak]);

  const loadRandomWord = useCallback(async () => {
    setIsLoading(true);
    setFeedback(null);
    setError(null);
    setChoiceOptions([]);

    try {
      const nextWord = await fetchRandomWord();
      let nextPool = appendUniqueWords(wordPoolRef.current, [nextWord]);

      if (nextWord.task_type === "direct_translation") {
        const distractors = await fetchDistractorPool();
        nextPool = appendUniqueWords(nextPool, distractors);
      }

      wordPoolRef.current = nextPool;
      setChoiceOptions(
        nextWord.task_type === "direct_translation" ? buildChoiceOptions(nextWord, nextPool) : [],
      );
      setWord(nextWord);
    } catch (caughtError) {
      setWord(null);
      setError(caughtError instanceof Error ? caughtError.message : "Неизвестная ошибка");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadRandomWord();
  }, [loadRandomWord]);

  const checkAnswer = useCallback(
    async (answer: string) => {
      if (!word) {
        return;
      }

      setIsChecking(true);
      setError(null);

      try {
        const response = await fetch(`/vocab/${word.id}/check`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            answer,
            task_type: word.task_type,
          }),
        });

        if (!response.ok) {
          throw new Error("Не удалось проверить ответ");
        }

        const data: CheckAnswerResponse = await response.json();
        setFeedback(data);
        setAnsweredCount((current) => current + 1);
        setStreak((current) => (data.correct ? current + 1 : 0));
      } catch (caughtError) {
        setError(caughtError instanceof Error ? caughtError.message : "Неизвестная ошибка");
      } finally {
        setIsChecking(false);
      }
    },
    [word],
  );

  const finishMatchingGame = useCallback(() => {
    setActiveMode("cards");
  }, []);

  return (
    <main className="min-h-screen bg-[#f6f8fb] px-4 py-6 text-slate-950 sm:px-6 lg:px-8">
      <div className="mx-auto w-full max-w-4xl">
        <header className="mb-6">
          <div className="mb-5 flex items-center justify-between gap-4">
            <div>
              <p className="text-sm font-black uppercase tracking-wider text-emerald-600">
                Deutsch Trainer
              </p>
              <h1 className="mt-1 text-3xl font-black tracking-tight sm:text-4xl">
                Тренажер немецких слов
              </h1>
            </div>

            <div className="rounded-2xl bg-white px-4 py-3 text-right shadow-sm">
              <p className="text-xs font-black uppercase tracking-wide text-slate-400">Streak</p>
              <p className="text-2xl font-black text-slate-950">{streak}</p>
            </div>
          </div>

          <div className="mb-5 grid gap-2 rounded-3xl bg-white p-2 shadow-sm sm:grid-cols-2">
            {modes.map((mode) => {
              const isActive = activeMode === mode.id;

              return (
                <button
                  key={mode.id}
                  type="button"
                  onClick={() => setActiveMode(mode.id)}
                  className={`rounded-2xl px-4 py-3 text-left transition-all duration-200 ${
                    isActive
                      ? "bg-slate-950 text-white shadow-lg shadow-slate-200"
                      : "bg-transparent text-slate-600 hover:bg-slate-50 hover:text-slate-950"
                  }`}
                >
                  <span className="block text-base font-black">{mode.label}</span>
                  <span
                    className={`mt-1 block text-sm font-semibold ${
                      isActive ? "text-slate-300" : "text-slate-400"
                    }`}
                  >
                    {mode.description}
                  </span>
                </button>
              );
            })}
          </div>

          {activeMode === "cards" && (
            <>
              <div className="rounded-full bg-white p-2 shadow-sm">
                <div className="h-4 overflow-hidden rounded-full bg-slate-100">
                  <div
                    className="h-full rounded-full bg-emerald-500 transition-all duration-500 ease-out"
                    style={{ width: `${miniStreakProgress}%` }}
                  />
                </div>
              </div>

              <div className="mt-2 flex justify-between text-sm font-bold text-slate-500">
                <span>{Math.min(streak % 5 || (streak > 0 ? 5 : 0), 5)} / 5 до мини-серии</span>
                <span>Ответов: {answeredCount}</span>
              </div>
            </>
          )}
        </header>

        {activeMode === "matching" ? (
          <MatchingGame onFinish={finishMatchingGame} />
        ) : (
          <>
            {isLoading && (
              <div className="rounded-2xl border border-slate-200 bg-white p-8 text-center text-lg font-bold shadow-xl shadow-slate-200/70">
                Загружаем упражнение...
              </div>
            )}

            {!isLoading && error && (
              <div className="rounded-2xl border-2 border-rose-200 bg-rose-50 p-6 text-rose-950 shadow-xl shadow-rose-100">
                <p className="text-xl font-black">Ошибка</p>
                <p className="mt-2 font-semibold">{error}</p>
                <button
                  type="button"
                  onClick={() => void loadRandomWord()}
                  className="mt-5 rounded-xl bg-rose-600 px-5 py-3 font-black text-white shadow-lg shadow-rose-200 transition hover:-translate-y-0.5 hover:bg-rose-700"
                >
                  Повторить
                </button>
              </div>
            )}

            {!isLoading && !error && word && (
              <Flashcard
                word={word}
                feedback={feedback}
                choiceOptions={choiceOptions}
                isChecking={isChecking}
                onCheck={checkAnswer}
                onNext={loadRandomWord}
              />
            )}
          </>
        )}
      </div>
    </main>
  );
}
