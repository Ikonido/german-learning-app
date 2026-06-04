from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.models.enums import Gender, Auxiliary, WordType


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
    pass


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
    pass


class VerbWordRead(WordBase):
    id: int
    word_type: Literal["verb"] = "verb"
    verb_detail: VerbDetailRead | None = None


# --- Union response for random word ---
class WordRead(BaseModel):
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

    class Config:
        from_attributes = True


# --- Progress ---
class ProgressRead(BaseModel):
    id: int
    word_id: int
    ease_factor: float
    interval_days: int
    repetitions: int
    next_review_date: date | None = None
    last_reviewed_at: datetime | None = None
    correct_count: int
    incorrect_count: int

    class Config:
        from_attributes = True


class WordWithProgress(WordRead):
    progress: ProgressRead | None = None


# --- Check answer ---
class CheckAnswerRequest(BaseModel):
    answer: str = Field(..., min_length=1, description="User's answer, e.g. 'der Tisch' or 'gegangen'")


class CheckAnswerResponse(BaseModel):
    correct: bool
    correct_answer: str
    translation: str
    message: str
    word_id: int
    word_type: WordType
    # For future: points_earned, streak etc
