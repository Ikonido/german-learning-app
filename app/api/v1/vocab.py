from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_current_user_optional
import random

from app.crud.vocab import (
    check_translation,
    get_matching_words,
    get_or_create_progress,
    get_random_word_with_task,
    get_word_by_id,
    update_progress_after_review,
)
from app.db.session import get_db
from app.models.enums import WordType
from app.models.user import User
from app.schemas.vocab import (
    CheckAnswerRequest,
    CheckAnswerResponse,
    MatchingCheckRequest,
    MatchingCheckResponse,
    MatchingGameResponse,
    MatchingTranslation,
    MatchingWord,
    WordRead,
    WordWithProgress,
    WordWithTask,
)

router = APIRouter(prefix="/vocab", tags=["vocabulary"])


@router.get("/random", response_model=WordWithTask)
def get_random_vocab_word(
    word_type: WordType | None = Query(None, description="Filter by word type: noun or verb"),
    level: str | None = Query(None, description="Filter by level e.g. A1, A2, B1"),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    """
    Get a random word for practice.
    The backend now randomly assigns a task_type:
      - direct_translation: translate German → Russian
      - reverse_translation: translate Russian → German
      - fill_blank: fill the word into the example_sentence (shown with ___)
    If authenticated, will try to return due reviews / new words first.
    """
    user_id = current_user.id if current_user else None

    word, task_type, blank_sentence = get_random_word_with_task(
        db=db,
        word_type=word_type,
        level=level,
        user_id=user_id,
        exclude_known=True,
    )

    if not word:
        # Fallback without user filter
        word, task_type, blank_sentence = get_random_word_with_task(
            db=db, word_type=word_type, level=level, user_id=None, exclude_known=False
        )

    if not word:
        raise HTTPException(status_code=404, detail="No words found in database")

    # Attach progress if user logged in
    progress = None
    if current_user:
        from app.models.progress import UserProgress
        progress = (
            db.query(UserProgress)
            .filter(UserProgress.user_id == current_user.id, UserProgress.word_id == word.id)
            .first()
        )

    # Build response
    word_data = WordRead.model_validate(word)
    base_response = WordWithProgress(**word_data.model_dump(), progress=progress)
    return WordWithTask(
        **base_response.model_dump(),
        task_type=task_type,
        blank_sentence=blank_sentence,
    )


@router.get("/matching", response_model=MatchingGameResponse)
def get_matching_pairs(
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    """
    Matching Pairs game ("Соединить ответы").

    Returns 5 words (preferring those the user has already started learning via progress).
    German words and their translations are returned in two separate lists,
    each independently shuffled on the backend.
    The client uses the `id` to match correct pairs.
    """
    user_id = current_user.id if current_user else None

    words = get_matching_words(db=db, count=5, user_id=user_id)

    if len(words) == 0:
        raise HTTPException(status_code=404, detail="No words found in database")

    # Build the two sides
    german_side: list[MatchingWord] = [
        MatchingWord(id=w.id, word_text=w.german) for w in words
    ]
    russian_side: list[MatchingTranslation] = [
        MatchingTranslation(id=w.id, translation_text=w.translation) for w in words
    ]

    # Shuffle independently so orders don't match
    random.shuffle(german_side)
    random.shuffle(russian_side)

    return MatchingGameResponse(
        german_words=german_side,
        russian_translations=russian_side,
        count=len(german_side),
    )


@router.post("/matching/check", response_model=MatchingCheckResponse)
def check_matching_pairs(
    payload: MatchingCheckRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    """
    Check / submit results of a Matching Pairs game round.

    The client sends the list of word IDs that were correctly matched.
    For each such ID we:
      - ensure UserProgress exists
      - treat it as a correct review (update SRS stats)
      - award simple XP (e.g. 10 points per correct pair)

    This is a suggested implementation. You can extend it with:
    - batch updates
    - bonus for perfect rounds / speed
    - separate "matching_streak" counter
    - etc.
    """
    user_id = current_user.id if current_user else None

    matched_ids = payload.matched_ids
    # We trust the client for which pairs were correct in this round (MVP).
    # In production you might want to receive full pairs and re-validate on server.
    correct_count = len(matched_ids)
    xp_per_pair = 10
    total_xp = 0

    if user_id is not None and correct_count > 0:
        for wid in matched_ids:
            try:
                progress = get_or_create_progress(db, user_id, wid)
                # Successful match in the game = quality 4 (good choice, not "perfect free recall")
                update_progress_after_review(db, progress, quality=4)
                total_xp += xp_per_pair
            except Exception:
                # bad id or db issue — ignore for this pair
                continue

    message = (
        f"Отлично! Ты правильно соединил {correct_count} пар(ы)."
        if correct_count > 0
        else "Нет правильных соединений для засчитывания."
    )

    return MatchingCheckResponse(
        correct_count=correct_count,
        message=message,
        xp_earned=total_xp,
    )


@router.post("/{word_id}/check", response_model=CheckAnswerResponse)
def check_word_translation(
    word_id: int,
    payload: CheckAnswerRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    """
    Check user's answer for a word (noun gender+word or verb forms).
    If user is logged in, automatically updates spaced repetition progress.
    """
    user_id = current_user.id if current_user else None

    try:
        result = check_translation(
            db=db,
            word_id=word_id,
            user_answer=payload.answer,
            task_type=payload.task_type,
            user_id=user_id,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{word_id}", response_model=WordRead)
def get_word_detail(word_id: int, db: Session = Depends(get_db)):
    word = get_word_by_id(db, word_id)
    if not word:
        raise HTTPException(status_code=404, detail="Word not found")
    return word


# --- Progress endpoints ---
@router.get("/progress/stats")
def get_progress_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Basic user stats."""
    from app.models.progress import UserProgress
    from sqlalchemy import func

    stats = (
        db.query(
            func.count(UserProgress.id).label("total_words_tracked"),
            func.sum(UserProgress.correct_count).label("total_correct"),
            func.sum(UserProgress.incorrect_count).label("total_incorrect"),
        )
        .filter(UserProgress.user_id == current_user.id)
        .first()
    )

    due_today = (
        db.query(UserProgress)
        .filter(
            UserProgress.user_id == current_user.id,
            UserProgress.next_review_date <= date.today(),
        )
        .count()
    )

    return {
        "total_tracked": stats.total_words_tracked or 0,
        "total_correct_answers": stats.total_correct or 0,
        "total_incorrect_answers": stats.total_incorrect or 0,
        "due_for_review_today": due_today,
    }
