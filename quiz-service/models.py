from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Integer,
    String,
    Text,
    Boolean,
    ForeignKey,
    UniqueConstraint,
    DateTime,
)
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import Mapped, mapped_column

from shared.database import Base


class Question(Base):
    __tablename__ = "question"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)

    # mcq = normal multiple choice
    # fill_blank_choice = clickable word-button answer
    # drag_drop = drag and drop mappings
    question_type: Mapped[str] = mapped_column(String(30), default="mcq", nullable=False)

    points: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    time_limit_seconds: Mapped[int] = mapped_column(Integer, default=40, nullable=False)

    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    blank_placeholder: Mapped[str | None] = mapped_column(String(100), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class AnswerOption(Base):
    __tablename__ = "answer_option"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("question.id"), index=True, nullable=False
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class DragDropItem(Base):
    __tablename__ = "drag_drop_item"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("question.id"), index=True, nullable=False
    )

    # draggable item
    item_key: Mapped[str] = mapped_column(String(100), nullable=False)
    item_text: Mapped[str] = mapped_column(String(255), nullable=False)

    # correct target slot
    target_key: Mapped[str | None] = mapped_column(String(100), nullable=True)
    target_label: Mapped[str | None] = mapped_column(String(255), nullable=True)

    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    __table_args__ = (
        UniqueConstraint("question_id", "item_key", name="uq_drag_item_key_per_question"),
    )


class QuizAttempt(Base):
    __tablename__ = "quiz_attempt"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)

    status: Mapped[str] = mapped_column(String(20), default="in_progress", nullable=False)
    score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class AttemptQuestion(Base):
    __tablename__ = "attempt_question"
    __table_args__ = (
        UniqueConstraint("attempt_id", "question_id", name="uq_attempt_question"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    attempt_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("quiz_attempt.id"), index=True, nullable=False
    )
    question_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("question.id"), index=True, nullable=False
    )
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class AttemptAnswer(Base):
    __tablename__ = "attempt_answer"
    __table_args__ = (
        UniqueConstraint("attempt_id", "question_id", name="uq_attempt_answer"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    attempt_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("quiz_attempt.id"), index=True, nullable=False
    )
    question_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("question.id"), index=True, nullable=False
    )

    # answered | missed | unanswered
    answer_state: Mapped[str] = mapped_column(String(20), default="unanswered", nullable=False)

    # generic answer payload:
    # mcq/fill_blank_choice -> {"selected_option_id": 12}
    # drag_drop -> {"mappings": [{"item_key":"cpu","target_key":"slot_1"}]}
    answer_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    is_correct: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    points_earned: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    answered_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)