from pydantic import BaseModel, ConfigDict
from typing import Literal

class QuestionCreateIn(BaseModel):
    category: Literal["bscs", "bsit", "bsis", "btvted"]
    text: str

class OptionCreateIn(BaseModel):
    text: str
    is_correct: bool = False

class QuestionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    category: str
    text: str

class OptionOut(BaseModel):
    id: int
    question_id: int
    text: str

class AttemptStartOut(BaseModel):
    attempt_id: int

class SubmitAnswerIn(BaseModel):
    question_id: int
    selected_option_id: int

class SubmitQuizIn(BaseModel):
    answers: list[SubmitAnswerIn]

class SubmitQuizOut(BaseModel):
    attempt_id: int
    score: int
    total: int
    recommendation: dict