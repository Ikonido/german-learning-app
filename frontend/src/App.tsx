import { useCallback, useEffect, useState } from "react";
import Flashcard from "./components/Flashcard";
import type { CheckAnswerResponse, Word } from "./types";

// When using Vite proxy (recommended for dev), leave empty so calls go to /vocab/*
// In production or when running frontend separately, set VITE_API_URL=http://your-backend
const API_URL = import.meta.env.VITE_API_URL || '';

export default function App() {
  const [word, setWord] = useState<Word | null>(null);
  const [feedback, setFeedback] = useState<CheckAnswerResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isChecking, setIsChecking] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadRandomWord = useCallback(async () => {
    setIsLoading(true);
    setFeedback(null);
    setError(null);

    try {
      const response = await fetch(`${API_URL}/vocab/random`);

      if (!response.ok) {
        throw new Error("Не удалось загрузить слово");
      }

      const data: Word = await response.json();
      setWord(data);
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

  const checkAnswer = async (answer: string) => {
    if (!word) {
      return;
    }

    setIsChecking(true);
    setError(null);

    try {
      const response = await fetch(`${API_URL}/vocab/${word.id}/check`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ answer }),
      });

      if (!response.ok) {
        throw new Error("Не удалось проверить ответ");
      }

      const data: CheckAnswerResponse = await response.json();
      setFeedback(data);
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Неизвестная ошибка");
    } finally {
      setIsChecking(false);
    }
  };

  return (
    <main className="min-h-screen bg-slate-100 px-4 py-8 text-slate-950 sm:px-6 lg:px-8">
      <div className="mx-auto mb-8 max-w-2xl">
        <p className="text-sm font-semibold uppercase tracking-wide text-slate-500">
          Deutsch Trainer
        </p>
        <h1 className="mt-2 text-3xl font-bold sm:text-4xl">Карточки немецких слов</h1>
      </div>

      {isLoading && (
        <div className="mx-auto max-w-2xl rounded-lg border border-slate-200 bg-white p-6 text-center shadow-sm">
          Загружаем слово...
        </div>
      )}

      {!isLoading && error && (
        <div className="mx-auto max-w-2xl rounded-lg border border-rose-200 bg-rose-50 p-6 text-rose-950 shadow-sm">
          <p className="font-semibold">Ошибка</p>
          <p className="mt-2">{error}</p>
          <button
            type="button"
            onClick={() => void loadRandomWord()}
            className="mt-4 rounded-md bg-rose-950 px-5 py-3 font-semibold text-white transition hover:bg-rose-800"
          >
            Повторить
          </button>
        </div>
      )}

      {!isLoading && !error && word && (
        <Flashcard
          word={word}
          feedback={feedback}
          isChecking={isChecking}
          onCheck={checkAnswer}
          onNext={loadRandomWord}
        />
      )}
    </main>
  );
}
