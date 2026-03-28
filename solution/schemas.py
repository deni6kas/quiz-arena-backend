"""
Pydantic-схемы для валидации запросов и ответов.
"""

from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1)

    model_config = ConfigDict(from_attributes=True)


class CategoryRead(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class QuizCreate(BaseModel):
    title: str = Field(min_length=1)
    category_id: int
    time_limit: int = Field(ge=30)

    model_config = ConfigDict(from_attributes=True)


class QuizRead(BaseModel):
    id: int
    title: str
    category_id: int
    time_limit: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class QuizDetail(QuizRead):
    questions_count: int


class QuestionCreate(BaseModel):
    text: str = Field(min_length=1)
    options: List[str] = Field(min_items=2, max_items=6)
    correct_index: int = Field(ge=0)

    model_config = ConfigDict(from_attributes=True)


class QuestionRead(BaseModel):
    id: int
    quiz_id: int
    text: str
    options: List[str]

    model_config = ConfigDict(from_attributes=True)


class QuestionFull(QuestionRead):
    correct_index: int


class PlayerCreate(BaseModel):
    nickname: str = Field(min_length=1)
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class PlayerRead(BaseModel):
    id: int
    nickname: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class AttemptStart(BaseModel):
    player_id: int

    model_config = ConfigDict(from_attributes=True)


class AttemptStarted(BaseModel):
    attempt_id: int
    started_at: datetime
    time_limit: int

    model_config = ConfigDict(from_attributes=True)


class AnswerItem(BaseModel):
    question_id: int
    answer: int

    model_config = ConfigDict(from_attributes=True)


class AttemptSubmit(BaseModel):
    answers: List[AnswerItem] = Field(min_items=1)

    model_config = ConfigDict(from_attributes=True)


class AttemptResult(BaseModel):
    score: int
    max_score: int
    percent: float
    finished_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LeaderboardEntry(BaseModel):
    nickname: str
    score: int
    max_score: int
    time_seconds: int

    model_config = ConfigDict(from_attributes=True)


class BestQuiz(BaseModel):
    quiz_title: str
    score: int
    max_score: int
    percent: float

    model_config = ConfigDict(from_attributes=True)


class PlayerStats(BaseModel):
    player: PlayerRead
    total_attempts: int
    avg_score_percent: float
    best_quiz: BestQuiz | None

    model_config = ConfigDict(from_attributes=True)


class ImportRequest(BaseModel):
    amount: int = Field(ge=1, le=20)

    model_config = ConfigDict(from_attributes=True)
