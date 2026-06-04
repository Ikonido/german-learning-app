# Deutsch Lernen — Тренажёр немецкого языка

Полноценное full-stack приложение для изучения немецкого языка.

**Основные возможности:**
- Интерактивные карточки с тремя типами заданий (`direct_translation`, `reverse_translation`, `fill_blank`)
- Мини-игра **«Соединить пары»** (Matching Pairs)
- Система прогресса на основе упрощённого Spaced Repetition (SM-2)
- Поддержка существительных (с родом и множественным числом) и глаголов (3 основные формы + haben/sein)
- Готовый SPA-фронтенд на React + TypeScript + Tailwind

## Стек

**Backend**
- Python 3.12+ + FastAPI
- SQLAlchemy 2.0 (синхронный)
- SQLite (по умолчанию) / PostgreSQL
- Pydantic v2 + Alembic
- JWT (python-jose + passlib)

**Frontend**
- React 18 + TypeScript
- Vite + Tailwind CSS
- Проксирование `/vocab/*` на бэкенд

## Быстрый старт (Windows + SQLite) — рекомендуется

Самый простой способ запустить и бэкенд, и фронтенд одной командой:

```powershell
# 1. Создай виртуальное окружение и установи зависимости
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

cd frontend
npm install
cd ..

# 2. Инициализируй базу данных SQLite и наполни её данными
python -c "from app.db.session import engine, Base; Base.metadata.create_all(engine)"
python scripts/seed_expanded.py

# 3. Запусти проект (бэкенд + фронтенд + браузер)
.\run_project.bat
```

**Что делает `run_project.bat`:**
- Запускает FastAPI (`uvicorn`) в отдельном окне
- Запускает Vite dev-сервер фронтенда в отдельном окне
- Через 3 секунды открывает браузер на `http://localhost:5173`

**Доступные адреса:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- Swagger UI (документация): http://localhost:8000/docs

По умолчанию используется файл `german_app.db` (SQLite).

## Ручная разработка

```powershell
.venv\Scripts\activate

# Инициализация БД (если ещё не сделали)
python -c "from app.db.session import engine, Base; Base.metadata.create_all(engine)"

# Наполнение (рекомендуется)
python scripts/seed_expanded.py

# Запуск только бэкенда
uvicorn app.main:app --reload

# В другом терминале — фронтенд
cd frontend
npm run dev
```

## Альтернатива: PostgreSQL + Docker

```bash
cp .env.example .env
# В .env укажи DATABASE_URL=postgresql://...

docker compose up --build -d
docker compose exec api alembic upgrade head
docker compose exec api python scripts/seed_expanded.py
```

## Структура проекта

```
.
├── app/                      # Backend (FastAPI)
│   ├── api/v1/               # Роутеры (auth, vocab)
│   ├── core/                 # Конфигурация и безопасность
│   ├── crud/                 # Логика работы с БД
│   ├── db/                   # SQLAlchemy сессия
│   ├── models/               # Модели (Word, NounDetail, VerbDetail, UserProgress...)
│   ├── schemas/              # Pydantic-схемы
│   └── main.py
├── frontend/                 # React + Vite + Tailwind SPA
│   ├── src/
│   │   ├── components/       # Flashcard, MatchingGame и др.
│   │   └── App.tsx
│   ├── vite.config.ts        # Прокси /vocab → бэкенд
│   └── ...
├── scripts/
│   ├── seed.py               # Базовый сидер
│   └── seed_expanded.py      # 120+ слов A1–A2 с примерами предложений (рекомендуется)
├── alembic/                  # Миграции БД
├── run_project.bat           # Быстрый запуск всего проекта на Windows
├── docker-compose.yml
├── requirements.txt
├── .env.example              # DATABASE_URL=sqlite:///./german_app.db (по умолчанию)
├── german_app.db             # SQLite БД (создаётся автоматически)
└── README.md
```

## База данных

### Основные таблицы

- `words` — `german`, `translation`, `word_type` (noun/verb), `level`, `category`, `example_sentence`
- `noun_details` — `gender` (der/die/das), `plural`
- `verb_details` — `praeteritum`, `perfekt`, `auxiliary` (haben/sein)
- `users` + `user_progress` — Spaced Repetition (ease_factor, interval_days, repetitions, next_review_date и т.д.)

## API (основные эндпоинты)

### Аутентификация

- `POST /auth/register`
- `POST /auth/login` → возвращает JWT
- `GET  /auth/me` (требует Bearer токен)

### Практика (карточки)

**GET /vocab/random**

Возвращает слово + автоматически выбранный `task_type`:

- `direct_translation` — переведи немецкое слово на русский
- `reverse_translation` — переведи русский перевод на немецкий
- `fill_blank` — подставь слово в предложение (`blank_sentence` уже содержит `___`)

В ответе также приходит `blank_sentence` (только для `fill_blank`) и текущий `progress` пользователя (если авторизован).

**POST /vocab/{id}/check**

Проверка ответа. Обязательно передавай `task_type`, который пришёл из `/random`.

#### Пример для `direct_translation` (ответ на русском)

```http
POST /vocab/42/check
Content-Type: application/json

{
  "answer": "дом",
  "task_type": "direct_translation"
}
```

#### Пример для `reverse_translation` (ответ на немецком)

```http
POST /vocab/42/check
Content-Type: application/json

{
  "answer": "das Haus",
  "task_type": "reverse_translation"
}
```

**Ответ** (в обоих случаях):

```json
{
  "correct": true,
  "correct_answer": "das Haus (мн: die Häuser)",
  "translation": "дом",
  "message": "Отлично!",
  "word_id": 42,
  "word_type": "noun",
  "task_type": "reverse_translation"
}
```

Если пользователь авторизован — автоматически обновляется `UserProgress` (SRS).

### Мини-игра «Соединить пары» (Matching Pairs)

**GET /vocab/matching**

Возвращает 5 слов. Два независимо перемешанных массива:

- `german_words` — немецкие варианты (`{id, word_text}`)
- `russian_translations` — русские переводы (`{id, translation_text}`)

Пользователь соединяет пары по `id`. Сервер никогда не возвращает их в одинаковом порядке.

**Пример ответа:**

```json
{
  "german_words": [
    { "id": 5, "word_text": "Tisch" },
    { "id": 12, "word_text": "gehen" }
  ],
  "russian_translations": [
    { "id": 12, "translation_text": "идти, ходить" },
    { "id": 5, "translation_text": "стол" }
  ],
  "count": 5
}
```

**POST /vocab/matching/check**

После того как игрок закончил раунд, отправляем список успешно соединённых ID.

```http
POST /vocab/matching/check
Content-Type: application/json

{
  "matched_ids": [5, 12, 7, 33, 19]
}
```

**Ответ:**

```json
{
  "correct_count": 5,
  "message": "Отлично! Ты правильно соединил 5 пар(ы).",
  "xp_earned": 50
}
```

- Для авторизованных пользователей по каждому `id` обновляется `UserProgress` (как успешное повторение).
- Начисляются простые очки XP (по 10 за пару).

## Наполнение базы данных

Рекомендуется использовать расширенный сидер:

```powershell
python scripts/seed_expanded.py
```

Он:
- Очищает старые данные
- Добавляет 120+ слов A1–A2
- Распределяет по категориям: Мебель, Еда, Семья, Движение, Время
- Заполняет `example_sentence` у каждого слова (необходимо для `fill_blank`)

## Как добавить новое слово вручную

```python
from app.db.session import SessionLocal
from app.models import Word, NounDetail, WordType, Gender

db = SessionLocal()

w = Word(
    german="Lampe",
    translation="лампа",
    word_type=WordType.NOUN,
    level="A1",
    category="Мебель",
    example_sentence="Die Lampe leuchtet im Zimmer."
)
db.add(w)
db.flush()

db.add(NounDetail(word_id=w.id, gender=Gender.DIE, plural="Lampen"))
db.commit()
```

## Разработка

- Бэкенд: `uvicorn app.main:app --reload`
- Фронтенд: `cd frontend && npm run dev`
- Тесты: `pytest`
- Миграции: `alembic revision --autogenerate -m "..."` → `alembic upgrade head`

## Полезные ссылки

- [FastAPI](https://fastapi.tiangolo.com)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/)
- Spaced Repetition (SM-2 алгоритм)

---

Удачи в изучении немецкого! Der, die, das — мы справимся. 🇩🇪
