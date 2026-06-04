from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_current_user_optional
from app.crud.vocab import (
    check_translation,
    get_random_word_with_task,
    get_word_by_id,
)
from app.db.session import get_db
from app.models.enums import WordType
from app.models.user import User
from app.schemas.vocab import (
    CheckAnswerRequest,
    CheckAnswerResponse,
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
