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


def get_random_word_with_task(
    db: Session,
    word_type: WordType | None = None,
    level: str | None = None,
    user_id: int | None = None,
    exclude_known: bool = True,
) -> tuple[Word | None, str, str | None]:
    """
    Returns a random word + a randomly chosen task_type for the exercise.
    Also returns precomputed blank_sentence when task_type == 'fill_blank'.
    """
    word = get_random_word(
        db=db,
        word_type=word_type,
        level=level,
        user_id=user_id,
        exclude_known=exclude_known,
    )
    if not word:
        return None, "direct_translation", None

    task_type: str = random.choice(
        ["direct_translation", "reverse_translation", "fill_blank"]
    )

    blank_sentence: str | None = None
    if task_type == "fill_blank" and word.example_sentence:
        # Replace the vocabulary item with blank. The sentence in DB must contain the exact german word.
        blank_sentence = word.example_sentence.replace(word.german, "___")

    return word, task_type, blank_sentence


def get_matching_words(
    db: Session,
    count: int = 5,
    user_id: int | None = None,
) -> list[Word]:
    """
    Returns up to `count` words for the matching pairs game.
    Prefers words that the user has already interacted with (has UserProgress entry),
    falling back to completely random words if not enough progressed words.
    """
    selected: list[Word] = []

    if user_id is not None:
        # Words the user has started learning (has progress record)
        # Uses the relationship defined on the Word model
        progressed = (
            db.query(Word)
            .join(Word.progress_entries)
            .filter(UserProgress.user_id == user_id)
            .all()
        )
        if progressed:
            k = min(count, len(progressed))
            selected = random.sample(progressed, k) if k < len(progressed) else progressed[:]

    # Fill remaining slots with random words (avoiding duplicates)
    if len(selected) < count:
        existing_ids = {w.id for w in selected}
        filler_query = db.query(Word)
        if existing_ids:
            filler_query = filler_query.filter(~Word.id.in_(list(existing_ids)))

        fillers = filler_query.all()
        if fillers:
            needed = count - len(selected)
            additional = random.sample(fillers, min(needed, len(fillers)))
            selected.extend(additional)

    # Final shuffle of the word list (order doesn't matter here, sides will be shuffled in router)
    random.shuffle(selected)
    return selected[:count]


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
    db: Session,
    word_id: int,
    user_answer: str,
    task_type: str | None = None,
    user_id: int | None = None,
) -> CheckAnswerResponse:
    """
    Check user's answer depending on the task_type.
    - direct_translation: user saw German, must type Russian translation
    - reverse_translation: user saw Russian, must type German (with article for nouns)
    - fill_blank: user must type the missing word (usually the german base form)
    """
    word = get_word_by_id(db, word_id)
    if not word:
        raise ValueError("Word not found")

    if task_type not in ("direct_translation", "reverse_translation", "fill_blank"):
        task_type = "direct_translation"  # safe default

    user_answer_clean = user_answer.strip().lower()

    # Helper for Russian translation matching (supports comma separated + parenthetical notes)
    def _get_translation_candidates() -> list[str]:
        import re
        candidates = []
        for part in re.split(r"[,;]", word.translation):
            part_clean = part.strip().lower()
            if part_clean:
                candidates.append(part_clean)
                no_paren = re.sub(r"\(.*?\)", "", part_clean).strip()
                if no_paren and no_paren != part_clean:
                    candidates.append(no_paren)
        return candidates

    translation_candidates = _get_translation_candidates()
    is_correct = False
    correct_answer = ""
    message = ""

    if task_type == "direct_translation":
        # German → Russian
        # Accept any of the translation variants
        is_correct = user_answer_clean in translation_candidates
        correct_answer = word.translation
        message = "Отлично!" if is_correct else f"Правильно: {word.translation}"

    elif task_type == "reverse_translation":
        # Russian → German (use rich German form display)
        correct_display = build_correct_answer_display(word)

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
            is_correct = user_answer_clean in candidates or user_answer_clean in translation_candidates

        elif word.word_type == WordType.VERB and word.verb_detail:
            v = word.verb_detail
            candidates = [
                word.german.lower(),
                v.praeteritum.lower(),
                v.perfekt.lower(),
                f"{v.auxiliary.value} {v.perfekt}".lower(),
                f"{v.auxiliary.value}{v.perfekt}".lower(),
            ]
            is_correct = user_answer_clean in [c.strip() for c in candidates] or user_answer_clean in translation_candidates

        else:
            is_correct = user_answer_clean == word.german.lower() or user_answer_clean in translation_candidates

        correct_answer = correct_display
        message = "Отлично!" if is_correct else f"Правильно: {correct_display}"

    elif task_type == "fill_blank":
        # Fill in the blank — expect the vocabulary word (lemma)
        # For nouns we are lenient and also accept article + noun
        expected = word.german.lower()
        is_correct = user_answer_clean == expected

        if word.word_type == WordType.NOUN and word.noun_detail:
            d = word.noun_detail
            noun_candidates = [
                word.german.lower(),
                f"{d.gender.value} {word.german}".lower(),
            ]
            is_correct = user_answer_clean in noun_candidates

        elif word.word_type == WordType.VERB and word.verb_detail:
            # Accept infinitive or the forms that would fit in sentence
            v = word.verb_detail
            verb_candidates = [
                word.german.lower(),
                v.praeteritum.lower(),
                v.perfekt.lower(),
            ]
            is_correct = user_answer_clean in verb_candidates

        correct_answer = word.german
        message = "Отлично!" if is_correct else f"Правильно: {word.german}"

    # Update SRS progress (same for all task types)
    if user_id is not None:
        progress = get_or_create_progress(db, user_id, word.id)
        update_progress_after_review(db, progress, is_correct)

    return CheckAnswerResponse(
        correct=is_correct,
        correct_answer=correct_answer,
        translation=word.translation,
        message=message,
        word_id=word.id,
        word_type=word.word_type,
        task_type=task_type,  # type: ignore[arg-type]
    )
