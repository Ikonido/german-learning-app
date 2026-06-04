from datetime import datetime
from sqlalchemy import String, Text, DateTime, Enum, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.enums import WordType, Gender, Auxiliary


class Word(Base):
    __tablename__ = "words"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    german: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    translation: Mapped[str] = mapped_column(Text, nullable=False)  # Russian translation
    word_type: Mapped[WordType] = mapped_column(Enum(WordType), nullable=False, index=True)

    # Common optional fields
    level: Mapped[str | None] = mapped_column(String(10), nullable=True, index=True)  # A1, A2, B1...
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    example_sentence: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # One-to-one details
    noun_detail: Mapped["NounDetail"] = relationship(
        "NounDetail", back_populates="word", uselist=False, cascade="all, delete-orphan"
    )
    verb_detail: Mapped["VerbDetail"] = relationship(
        "VerbDetail", back_populates="word", uselist=False, cascade="all, delete-orphan"
    )

    # Progress
    progress_entries: Mapped[list["UserProgress"]] = relationship(
        "UserProgress", back_populates="word", cascade="all, delete-orphan"
    )


class NounDetail(Base):
    __tablename__ = "noun_details"

    id: Mapped[int] = mapped_column(primary_key=True)
    word_id: Mapped[int] = mapped_column(
        ForeignKey("words.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )

    gender: Mapped[Gender] = mapped_column(Enum(Gender), nullable=False)
    plural: Mapped[str | None] = mapped_column(String(255), nullable=True)  # e.g. "Tische"

    word: Mapped["Word"] = relationship("Word", back_populates="noun_detail")


class VerbDetail(Base):
    __tablename__ = "verb_details"

    id: Mapped[int] = mapped_column(primary_key=True)
    word_id: Mapped[int] = mapped_column(
        ForeignKey("words.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )

    praeteritum: Mapped[str] = mapped_column(String(255), nullable=False)   # ging
    perfekt: Mapped[str] = mapped_column(String(255), nullable=False)       # gegangen
    auxiliary: Mapped[Auxiliary] = mapped_column(Enum(Auxiliary), nullable=False)

    # Optional future fields: separable, reflexive, etc.
    word: Mapped["Word"] = relationship("Word", back_populates="verb_detail")
