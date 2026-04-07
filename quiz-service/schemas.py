from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


QuestionType = Literal["mcq", "fill_blank_choice", "drag_drop"]
AttemptStatus = Literal["in_progress", "completed", "cancelled"]
AnswerState = Literal["answered", "missed", "unanswered"]


class QuestionCreateIn(BaseModel):
    category: Literal["bscs", "bsit", "bsis", "btvted"]
    text: str
    question_type: QuestionType = "mcq"
    points: int = Field(default=1, ge=1)
    time_limit_seconds: int = Field(default=40, ge=5, le=300)
    image_url: str | None = None
    blank_placeholder: str | None = None


class OptionCreateIn(BaseModel):
    text: str
    is_correct: bool = False
    display_order: int = 0


class DragDropItemCreateIn(BaseModel):
    item_key: str
    item_text: str
    target_key: str | None = None
    target_label: str | None = None
    display_order: int = 0


class OptionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    question_id: int
    text: str
    display_order: int


class DragDropItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    question_id: int
    item_key: str
    item_text: str
    target_key: str | None
    target_label: str | None
    display_order: int


class QuestionOut(BaseModel):
    id: int
    category: str
    text: str
    question_type: QuestionType
    points: int
    time_limit_seconds: int
    image_url: str | None = None
    blank_placeholder: str | None = None
    options: list[OptionOut] = Field(default_factory=list)
    drag_items: list[DragDropItemOut] = Field(default_factory=list)


class AttemptStartOut(BaseModel):
    attempt_id: int
    status: AttemptStatus


class DragDropMappingIn(BaseModel):
    item_key: str
    target_key: str


class SaveAnswerIn(BaseModel):
    question_id: int
    answer_state: AnswerState = "answered"
    selected_option_id: int | None = None
    mappings: list[DragDropMappingIn] = Field(default_factory=list)


class SavedAnswerOut(BaseModel):
    question_id: int
    answer_state: AnswerState
    selected_option_id: int | None = None
    mappings: list[DragDropMappingIn] = Field(default_factory=list)
    is_correct: bool
    points_earned: int


class AttemptProgressOut(BaseModel):
    attempt_id: int
    status: AttemptStatus
    score: int
    total: int
    saved_answers: list[SavedAnswerOut]


class SubmitQuizIn(BaseModel):
    answers: list[SaveAnswerIn] = Field(default_factory=list)


class SubmitQuizOut(BaseModel):
    attempt_id: int
    status: AttemptStatus
    score: int
    total: int
    recommendation: dict


class CancelQuizOut(BaseModel):
    attempt_id: int
    status: AttemptStatus
    message: str