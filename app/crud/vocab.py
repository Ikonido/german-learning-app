import random
from datetime import date, datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session, joinedload

from app.models.enums import WordType, Gender, Auxiliary
from app.models.vocabulary import Word, NounDetail, VerbDetail
from app.models.progress import UserProgress
from app.schemas.vocab import CheckAnswerRequest, CheckAnswerResponse, WordRead


def get_word_by_id(db: Session, word_id: int) -> Word | None:
    return (
        db.query(Word)
        .options(joinedload(Word.noun_detail), joinedload(Word.verb_detail))
        .filter(Word.id == word_id)
        .first()
    )


def get_random_word(
    db: Session,
    word_type: WordType | None = None,
    level: str | None = None,
    user_id: int | None = None,
    exclude_known: bool = True,
) -> Word | None:
    """
    Returns a random word, optionally filtered.
    If user_id provided, tries to prioritize due reviews or new words.
    """
    query = db.query(Word).options(
        joinedload(Word.noun_detail),
        joinedload(Word.verb_detail),
    )

    if word_type:
        query = query.filter(Word.word_type == word_type)
    if level:
        query = query.filter(Word.level == level)

    if user_id and exclude_known:
        # Exclude words user already knows very well (repetitions >= 5 and next_review in future)
        from app.models.progress import UserProgress
        subq = (
            db.query(UserProgress.word_id)
            .filter(
                UserProgress.user_id == user_id,
                UserProgress.repetitions >= 5,
                UserProgress.next_review_date > date.today()
            )
            .subquery()
        )
        query = query.filter(~Word.id.in_(subq))

    words = query.all()
    if not words:
        return None
    return random.choice(words)


def get_or_create_progress(db: Session, user_id: int, word_id: int) -> UserProgress:
    progress = (
        db.query(UserProgress)
        .filter(UserProgress.user_id == user_id, UserProgress.word_id == word_id)
        .first()
    )
    if progress:
        return progress

    progress = UserProgress(
        user_id=user_id,
        word_id=word_id,
        ease_factor=2.5,
        interval_days=0,
        repetitions=0,
        next_review_date=date.today(),
    )
    db.add(progress)
    db.commit()
    db.refresh(progress)
    return progress


def update_progress_after_review(
    db: Session, progress: UserProgress, is_correct: bool
) -> UserProgress:
    """
    Simple SM-2 inspired spaced repetition update.
    """
    now = datetime.now(timezone.utc)
    progress.last_reviewed_at = now
    progress.next_review_date = date.today()

    if is_correct:
        progress.correct_count += 1
        progress.repetitions += 1

        if progress.repetitions == 1:
            progress.interval_days = 1
        elif progress.repetitions == 2:
            progress.interval_days = 6
        else:
            progress.interval_days = int(progress.interval_days * progress.ease_factor)

        # Ease bonus on success
        progress.ease_factor = min(2.5, progress.ease_factor + 0.1)
    else:
        progress.incorrect_count += 1
        progress.repetitions = 0
        progress.interval_days = 0
        progress.ease_factor = max(1.3, progress.ease_factor - 0.2)

    # Set next review
    if progress.interval_days > 0:
        progress.next_review_date = date.today() + timedelta(days=progress.interval_days)

    db.add(progress)
    db.commit()
    db.refresh(progress)
    return progress


def build_correct_answer_display(word: Word) -> str:
    """Human friendly correct form for German."""
    if word.word_type == WordType.NOUN and word.noun_detail:
        d = word.noun_detail
        article = d.gender.value
        plural_part = f" (мн: {d.plural})" if d.plural else ""
        return f"{article} {word.german}{plural_part}"
    elif word.word_type == WordType.VERB and word.verb_detail:
        v = word.verb_detail
        return f"{word.german} — Präteritum: {v.praeteritum}, Perfekt: {v.auxiliary.value} {v.perfekt}"
    return word.german


def check_translation(
    db: Session, word_id: int, user_answer: str, user_id: int | None = None
) -> CheckAnswerResponse:
    """
    Check user's answer against the word.
    For nouns we accept "der Tisch", "Tisch", "die Tische" etc.
    """
    word = get_word_by_id(db, word_id)
    if not word:
        raise ValueError("Word not found")

    user_answer_clean = user_answer.strip().lower()
    correct_display = build_correct_answer_display(word)

    is_correct = False

    if word.word_type == WordType.NOUN and word.noun_detail:
        d = word.noun_detail
        candidates = [
            word.german.lower(),
            f"{d.gender.value} {word.german}".lower(),
            f"{d.gender.value}{word.german}".lower(),
        ]
        if d.plural:
            candidates.extend([
                d.plural.lower(),
                f"die {d.plural}".lower(),
            ])
        is_correct = user_answer_clean in candidates

    elif word.word_type == WordType.VERB and word.verb_detail:
        v = word.verb_detail
        candidates = [
            word.german.lower(),
            v.praeteritum.lower(),
            v.perfekt.lower(),
            f"{v.auxiliary.value} {v.perfekt}".lower(),
            f"{v.auxiliary.value}{v.perfekt}".lower(),
        ]
        is_correct = user_answer_clean in [c.strip() for c in candidates]

    else:
        # Fallback: exact match on base or translation (but we check German answer)
        is_correct = user_answer_clean == word.german.lower()

    # Update progress if user is authenticated
    if user_id is not None:
        progress = get_or_create_progress(db, user_id, word.id)
        update_progress_after_review(db, progress, is_correct)

    message = "Отлично!" if is_correct else f"Правильно: {correct_display}"

    return CheckAnswerResponse(
        correct=is_correct,
        correct_answer=correct_display,
        translation=word.translation,
        message=message,
        word_id=word.id,
        word_type=word.word_type,
    )
