from sqlalchemy import Integer, String, Text, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from shared.database import Base

class Question(Base):
    __tablename__ = "question"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)

class AnswerOption(Base):
    __tablename__ = "answer_option"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("question.id"), index=True, nullable=False
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

class QuizAttempt(Base):
    __tablename__ = "quiz_attempt"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

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

class AttemptAnswer(Base):
    __tablename__ = "attempt_answer"
    __table_args__ = (
        # optional but recommended: one answer per question per attempt
        UniqueConstraint("attempt_id", "question_id", name="uq_attempt_answer"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    attempt_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("quiz_attempt.id"), index=True, nullable=False
    )
    question_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("question.id"), index=True, nullable=False
    )
    selected_option_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("answer_option.id"), nullable=False
    )
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
