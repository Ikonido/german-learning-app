import { useCallback, useEffect, useMemo, useState } from "react";
import type {
  MatchingCheckResponse,
  MatchingGameResponse,
  MatchingTranslation,
  MatchingWord,
} from "../types";

interface MatchingGameProps {
  onFinish: () => void;
}

type Side = "german" | "russian";

interface WrongPair {
  germanId: number;
  russianId: number;
}

async function fetchMatchingGame(): Promise<MatchingGameResponse> {
  const response = await fetch("/vocab/matching");

  if (!response.ok) {
    throw new Error("Не удалось загрузить игру");
  }

  return response.json();
}

async function submitMatchingGame(matchedIds: number[]): Promise<MatchingCheckResponse> {
  const response = await fetch("/vocab/matching/check", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ matched_ids: matchedIds }),
  });

  if (!response.ok) {
    throw new Error("Не удалось завершить игру");
  }

  return response.json();
}

export default function MatchingGame({ onFinish }: MatchingGameProps) {
  const [germanWords, setGermanWords] = useState<MatchingWord[]>([]);
  const [russianTranslations, setRussianTranslations] = useState<MatchingTranslation[]>([]);
  const [selectedGermanId, setSelectedGermanId] = useState<number | null>(null);
  const [successMatches, setSuccessMatches] = useState<number[]>([]);
  const [recentSuccessId, setRecentSuccessId] = useState<number | null>(null);
  const [wrongPair, setWrongPair] = useState<WrongPair | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isFinishing, setIsFinishing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [finishResult, setFinishResult] = useState<MatchingCheckResponse | null>(null);

  const successSet = useMemo(() => new Set(successMatches), [successMatches]);
  const totalCount = germanWords.length;
  const solvedCount = successMatches.length;
  const isComplete = totalCount > 0 && solvedCount === totalCount;
  const progress = totalCount > 0 ? Math.round((solvedCount / totalCount) * 100) : 0;

  const loadGame = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    setFinishResult(null);
    setSelectedGermanId(null);
    setSuccessMatches([]);
    setRecentSuccessId(null);
    setWrongPair(null);

    try {
      const data = await fetchMatchingGame();
      setGermanWords(data.german_words);
      setRussianTranslations(data.russian_translations);
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Неизвестная ошибка");
      setGermanWords([]);
      setRussianTranslations([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadGame();
  }, [loadGame]);

  const selectGerman = useCallback(
    (id: number) => {
      if (successSet.has(id) || wrongPair || isComplete) {
        return;
      }

      setSelectedGermanId((current) => (current === id ? null : id));
    },
    [isComplete, successSet, wrongPair],
  );

  const selectRussian = useCallback(
    (id: number) => {
      if (selectedGermanId === null || successSet.has(id) || wrongPair || isComplete) {
        return;
      }

      if (selectedGermanId === id) {
        setSuccessMatches((current) => (current.includes(id) ? current : [...current, id]));
        setSelectedGermanId(null);
        setRecentSuccessId(id);
        window.setTimeout(() => setRecentSuccessId(null), 900);
        return;
      }

      setWrongPair({ germanId: selectedGermanId, russianId: id });
      window.setTimeout(() => {
        setWrongPair(null);
        setSelectedGermanId(null);
      }, 550);
    },
    [isComplete, selectedGermanId, successSet, wrongPair],
  );

  const finishGame = useCallback(async () => {
    if (!isComplete || isFinishing) {
      return;
    }

    setIsFinishing(true);
    setError(null);

    try {
      const result = await submitMatchingGame(successMatches);
      setFinishResult(result);
      window.setTimeout(onFinish, 900);
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Неизвестная ошибка");
    } finally {
      setIsFinishing(false);
    }
  }, [isComplete, isFinishing, onFinish, successMatches]);

  const getTileClassName = useCallback(
    (id: number, side: Side) => {
      const isMatched = successSet.has(id);
      const isRecentSuccess = recentSuccessId === id;
      const isWrong =
        wrongPair !== null &&
        ((side === "german" && wrongPair.germanId === id) ||
          (side === "russian" && wrongPair.russianId === id));
      const isSelected = side === "german" && selectedGermanId === id;

      const base =
        "min-h-16 rounded-2xl border-2 px-4 py-3 text-left text-lg font-black shadow-sm transition-all duration-200";

      if (isWrong) {
        return `${base} border-rose-500 bg-rose-100 text-rose-950 [animation:matching-shake_0.35s_ease-in-out]`;
      }

      if (isRecentSuccess) {
        return `${base} scale-[1.03] border-emerald-500 bg-emerald-100 text-emerald-950 shadow-lg shadow-emerald-100`;
      }

      if (isMatched) {
        return `${base} cursor-default border-emerald-200 bg-emerald-50 text-emerald-800 opacity-50`;
      }

      if (isSelected) {
        return `${base} border-violet-500 bg-violet-100 text-violet-950 shadow-lg shadow-violet-100`;
      }

      return `${base} border-slate-200 bg-white text-slate-950 hover:-translate-y-0.5 hover:border-emerald-300 hover:bg-emerald-50 hover:shadow-md`;
    },
    [recentSuccessId, selectedGermanId, successSet, wrongPair],
  );

  if (isLoading) {
    return (
      <section className="rounded-3xl border border-slate-200 bg-white p-8 text-center shadow-xl shadow-slate-200/70">
        <p className="text-lg font-black text-slate-950">Загружаем пары...</p>
      </section>
    );
  }

  if (error && germanWords.length === 0) {
    return (
      <section className="rounded-3xl border-2 border-rose-200 bg-rose-50 p-6 text-rose-950 shadow-xl shadow-rose-100">
        <p className="text-xl font-black">Не получилось открыть игру</p>
        <p className="mt-2 font-semibold">{error}</p>
        <button
          type="button"
          onClick={() => void loadGame()}
          className="mt-5 rounded-xl bg-rose-600 px-5 py-3 font-black text-white transition-all duration-200 hover:-translate-y-0.5 hover:bg-rose-700"
        >
          Повторить
        </button>
      </section>
    );
  }

  return (
    <section className="rounded-3xl border-2 border-slate-200 bg-white p-5 shadow-xl shadow-slate-200/70 sm:p-8">
      <style>
        {`@keyframes matching-shake {
          0%, 100% { transform: translateX(0); }
          20% { transform: translateX(-7px); }
          40% { transform: translateX(7px); }
          60% { transform: translateX(-5px); }
          80% { transform: translateX(5px); }
        }`}
      </style>

      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm font-black uppercase tracking-wider text-violet-600">
            Matching Pairs
          </p>
          <h2 className="mt-1 text-3xl font-black tracking-tight text-slate-950">
            Соединить пары
          </h2>
          <p className="mt-2 font-semibold text-slate-500">
            Выбери немецкое слово слева, затем его перевод справа.
          </p>
        </div>

        <div className="rounded-2xl bg-slate-50 px-4 py-3 text-right">
          <p className="text-xs font-black uppercase tracking-wide text-slate-400">Прогресс</p>
          <p className="text-2xl font-black text-slate-950">
            {solvedCount}/{totalCount}
          </p>
        </div>
      </div>

      <div className="mb-6 h-4 overflow-hidden rounded-full bg-slate-100">
        <div
          className="h-full rounded-full bg-emerald-500 transition-all duration-500"
          style={{ width: `${progress}%` }}
        />
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <div className="space-y-3">
          <p className="px-1 text-sm font-black uppercase tracking-wider text-slate-400">
            Deutsch
          </p>
          {germanWords.map((word) => (
            <button
              key={word.id}
              type="button"
              disabled={successSet.has(word.id) || isComplete}
              onClick={() => selectGerman(word.id)}
              className={getTileClassName(word.id, "german")}
            >
              {word.word_text}
            </button>
          ))}
        </div>

        <div className="space-y-3">
          <p className="px-1 text-sm font-black uppercase tracking-wider text-slate-400">
            Русский
          </p>
          {russianTranslations.map((translation) => (
            <button
              key={translation.id}
              type="button"
              disabled={successSet.has(translation.id) || isComplete}
              onClick={() => selectRussian(translation.id)}
              className={getTileClassName(translation.id, "russian")}
            >
              {translation.translation_text}
            </button>
          ))}
        </div>
      </div>

      {isComplete && (
        <div className="mt-6 rounded-3xl border-2 border-emerald-300 bg-emerald-50 p-6 text-emerald-950 shadow-lg shadow-emerald-100">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-2xl font-black">Раунд собран идеально</p>
              <p className="mt-2 font-semibold">
                Все пары найдены. Заверши игру, чтобы отправить результат и получить XP.
              </p>
              {finishResult && (
                <p className="mt-3 rounded-2xl bg-white px-4 py-3 font-black text-slate-950">
                  +{finishResult.xp_earned} XP · {finishResult.message}
                </p>
              )}
            </div>

            <button
              type="button"
              onClick={() => void finishGame()}
              disabled={isFinishing || Boolean(finishResult)}
              className="rounded-2xl bg-slate-950 px-6 py-4 font-black text-white shadow-lg shadow-slate-200 transition-all duration-200 hover:-translate-y-0.5 hover:bg-slate-800 disabled:translate-y-0 disabled:cursor-not-allowed disabled:bg-slate-400"
            >
              {isFinishing ? "Завершаем..." : finishResult ? "Готово" : "Завершить игру"}
            </button>
          </div>
        </div>
      )}

      {error && germanWords.length > 0 && (
        <p className="mt-4 rounded-2xl bg-rose-50 px-4 py-3 font-bold text-rose-700">{error}</p>
      )}
    </section>
  );
}
