# Deutsch Lernen — Backend

Фундамент backend'а для приложения изучения немецкого языка.  
Оптимизированная структура базы данных под специфику немецкого: существительные (род + множественное число) и глаголы (3 основные формы + вспомогательный глагол).

## Стек

- **Python 3.12+** + **FastAPI**
- **SQLAlchemy 2.0** (синхронный режим для простоты)
- **PostgreSQL 16+**
- **Alembic** для миграций
- **Pydantic v2**
- JWT аутентификация (python-jose + passlib bcrypt)

Почему именно этот стек:
- Отличная типизация и валидация (Pydantic + SQLAlchemy модели).
- Легко расширять (добавлять прилагательные, предлоги, spaced repetition улучшения).
- Alembic даёт полный контроль над схемой.
- Простой Docker-стек для быстрого старта.

## Структура проекта

```
.
├── alembic/                  # Миграции БД
├── app/
│   ├── api/v1/               # Роутеры (auth, vocab)
│   ├── core/                 # Конфиг, security (JWT, хеши)
│   ├── crud/                 # Бизнес-логика работы с БД
│   ├── db/                   # Session + Base
│   ├── models/               # SQLAlchemy модели (User, Word, NounDetail, VerbDetail, UserProgress)
│   ├── schemas/              # Pydantic схемы (вход/выход API)
│   └── main.py
├── scripts/
│   └── seed.py               # Наполнение начальными словами
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── alembic.ini
└── README.md
```

## База данных (ключевые таблицы)

### `words`
- `german` — базовая форма (Tisch, gehen)
- `translation` — перевод (на русский)
- `word_type` — noun / verb
- `level`, `category`, `example_sentence`

### `noun_details` (1:1 к words)
- `gender` — **der | die | das** (Enum)
- `plural` — форма множественного числа (Tische, Kinder)

### `verb_details` (1:1 к words)
- `praeteritum`
- `perfekt`
- `auxiliary` — **haben | sein** (Enum)

### `users` + `user_progress`
Прогресс использует упрощённый алгоритм **Spaced Repetition (SM-2)**:
- `ease_factor`, `interval_days`, `repetitions`
- `next_review_date`
- `correct_count` / `incorrect_count`

Это позволяет в будущем легко добавлять Anki-подобное повторение.

## API (основные эндпоинты)

### Auth
- `POST /auth/register`
- `POST /auth/login` → JWT
- `GET  /auth/me`

### Vocabulary
- `GET /vocab/random?word_type=noun&level=A1` — случайное слово (с прогрессом пользователя, если авторизован)
- `POST /vocab/{id}/check` — проверка ответа пользователя
  - Тело: `{ "answer": "der Tisch" }` или `{ "answer": "gegangen" }`
  - Возвращает `correct`, правильный ответ с артиклем/формами, обновляет прогресс автоматически
- `GET /vocab/{id}`
- `GET /vocab/progress/stats` — статистика пользователя (due today, accuracy и т.д.)

## Быстрый старт (Docker — рекомендуется)

```bash
# 1. Скопируй env
cp .env.example .env

# 2. Подними БД + API
docker compose up --build -d

# 3. Примени миграции
docker compose exec api alembic upgrade head

# 4. Засейди данные (существительные + глаголы A1)
docker compose exec api python scripts/seed.py

# 5. Готово!
# API: http://localhost:8000
# Документация: http://localhost:8000/docs
```

## Локальная разработка (без Docker)

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# или source .venv/bin/activate

pip install -r requirements.txt

# .env с DATABASE_URL на локальный postgres

alembic upgrade head
python scripts/seed.py

uvicorn app.main:app --reload
```

## Как добавить новые слова

Самый простой способ — через Python shell или новый скрипт:

```python
from app.db.session import SessionLocal
from app.models import Word, NounDetail, WordType, Gender

db = SessionLocal()
w = Word(german="Lampe", translation="лампа", word_type=WordType.NOUN, level="A1")
db.add(w); db.flush()
db.add(NounDetail(word_id=w.id, gender=Gender.DIE, plural="Lampen"))
db.commit()
```

Или используй `POST` в будущем (добавить админ-эндпоинт).

## Будущие улучшения (рекомендации)

- Отдельный админ/seed API или CSV импорт
- Полноценный SM-2 + fuzzy matching ответов
- Поддержка прилагательных, артиклей, предлогов с управлением
- Статистика по темам / уровням
- Пользовательские списки слов (коллекции)
- Экспорт в Anki CSV

## Полезные ссылки

- FastAPI docs: https://fastapi.tiangolo.com
- SQLAlchemy 2.0: https://docs.sqlalchemy.org/en/20/
- Spaced repetition: алгоритм SM-2

---

Удачи с проектом! Немецкий — отличный язык. Der, die, das — это вызов, но мы его победим.
