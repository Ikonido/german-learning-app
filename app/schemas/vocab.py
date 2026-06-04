from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import Gender, Auxiliary, WordType


TaskType = Literal["direct_translation", "reverse_translation", "fill_blank"]


# --- Shared ---
class WordBase(BaseModel):
    german: str
    translation: str
    level: str | None = None
    category: str | None = None
    example_sentence: str | None = None


# --- Noun ---
class NounDetailBase(BaseModel):
    gender: Gender
    plural: str | None = None


class NounDetailRead(NounDetailBase):
    model_config = ConfigDict(from_attributes=True)


class NounWordRead(WordBase):
    id: int
    word_type: Literal["noun"] = "noun"
    noun_detail: NounDetailRead | None = None


# --- Verb ---
class VerbDetailBase(BaseModel):
    praeteritum: str
    perfekt: str
    auxiliary: Auxiliary


class VerbDetailRead(VerbDetailBase):
    model_config = ConfigDict(from_attributes=True)


class VerbWordRead(WordBase):
    id: int
    word_type: Literal["verb"] = "verb"
    verb_detail: VerbDetailRead | None = None


# --- Union response for random word ---
class WordRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    german: str
    translation: str
    word_type: WordType
    level: str | None = None
    category: str | None = None
    example_sentence: str | None = None

    # Populated conditionally
    noun_detail: NounDetailRead | None = None
    verb_detail: VerbDetailRead | None = None


# --- Progress ---
class ProgressRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    word_id: int
    ease_factor: float
    interval_days: int
    repetitions: int
    next_review_date: date | None = None
    last_reviewed_at: datetime | None = None
    correct_count: int
    incorrect_count: int


class WordWithProgress(WordRead):
    progress: ProgressRead | None = None


class WordWithTask(WordWithProgress):
    """Response for /random that now includes a randomly assigned task type."""
    task_type: TaskType
    blank_sentence: str | None = None  # only for fill_blank tasks


# --- Check answer ---
class CheckAnswerRequest(BaseModel):
    answer: str = Field(..., min_length=1, description="User's answer, e.g. 'der Tisch' or 'gegangen' or Russian translation")
    task_type: TaskType | None = Field(
        None,
        description="Type of exercise the user received: direct_translation, reverse_translation or fill_blank"
    )


class CheckAnswerResponse(BaseModel):
    correct: bool
    correct_answer: str
    translation: str
    message: str
    word_id: int
    word_type: WordType
    task_type: TaskType | None = None
    # For future: points_earned, streak etc


# --- Matching Pairs Game (Соединить ответы) ---
class MatchingWord(BaseModel):
    """German side item for matching game."""
    id: int
    word_text: str


class MatchingTranslation(BaseModel):
    """Russian translation side item for matching game."""
    id: int
    translation_text: str


class MatchingGameResponse(BaseModel):
    """Response for GET /vocab/matching.

    Both lists are independently shuffled on the backend.
    The 'id' fields are used by the client to determine correct pairs.
    """
    german_words: list[MatchingWord]
    russian_translations: list[MatchingTranslation]
    count: int = 5


class MatchingCheckRequest(BaseModel):
    """Client sends the list of word IDs that were successfully paired in the matching game."""
    matched_ids: list[int] = Field(
        ...,
        min_length=1,
        description="IDs of words the user correctly matched in this round"
    )
    # Future: time_spent_seconds, mistakes_count, etc.


class MatchingCheckResponse(BaseModel):
    correct_count: int
    message: str
    # Simple XP / points for gamification. Real implementation can be more sophisticated.
    xp_earned: int = 0
    # Optionally return updated progress summaries for the matched words
