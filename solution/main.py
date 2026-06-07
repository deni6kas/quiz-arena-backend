"""
FastAPI-приложение Quiz Arena.
"""

from datetime import datetime
import random

import httpx
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from solution.models import Attempt, Category, Player, Question, Quiz
from solution.schemas import (
    AttemptResult,
    AttemptStarted,
    AttemptSubmit,
    AttemptStart,
    CategoryCreate,
    CategoryRead,
    ImportRequest,
    LeaderboardEntry,
    PlayerCreate,
    PlayerRead,
    PlayerStats,
    QuestionCreate,
    QuestionRead,
    QuizCreate,
    QuizDetail,
    QuizRead,
)

from solution import models  # noqa: F401
from solution.database import Base, engine, get_session  # noqa: F401

app = FastAPI(title="Quiz Arena API")
Base.metadata.create_all(bind=engine)


# ── Categories ────────────────────────────────────────────────────────────────


@app.post("/categories", response_model=CategoryRead, status_code=201)
def create_category(
    category: CategoryCreate,
    session: Session = Depends(get_session),
):
    category_obj = Category(name=category.name)
    session.add(category_obj)
    try:
        session.commit()
        session.refresh(category_obj)
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)

    return category_obj


@app.get("/categories", response_model=list[CategoryRead], status_code=200)
def list_categories(session: Session = Depends(get_session)):
    result = session.execute(select(Category))
    return result.scalars().all()


# ── Quizzes ───────────────────────────────────────────────────────────────────

@app.post("/quizzes", response_model=QuizRead, status_code=201)
def create_quiz(
    quiz: QuizCreate,
    session: Session = Depends(get_session),
):
    if session.get(Category, quiz.category_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    quiz_obj = Quiz(
        title=quiz.title,
        category_id=quiz.category_id,
        time_limit=quiz.time_limit,
        created_at=datetime.utcnow(),
    )
    session.add(quiz_obj)
    try:
        session.commit()
        session.refresh(quiz_obj)
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)
    return quiz_obj


@app.get("/quizzes", response_model=list[QuizRead], status_code=200)
def list_quizzes(
    category_id: int | None = None,
    session: Session = Depends(get_session),
):
    stmt = select(Quiz)
    if category_id is not None:
        stmt = stmt.where(Quiz.category_id == category_id)
    result = session.execute(stmt)
    return result.scalars().all()


@app.get("/quizzes/{quiz_id}", response_model=QuizDetail, status_code=200)
def get_quiz(quiz_id: int, session: Session = Depends(get_session)):
    quiz_obj = session.get(Quiz, quiz_id)
    if quiz_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    questions_count = session.scalar(
        select(func.count())
        .select_from(Question)
        .where(Question.quiz_id == quiz_id)
    )
    return QuizDetail(
        id=quiz_obj.id,
        title=quiz_obj.title,
        category_id=quiz_obj.category_id,
        time_limit=quiz_obj.time_limit,
        created_at=quiz_obj.created_at,
        questions_count=questions_count or 0,
    )


@app.delete("/quizzes/{quiz_id}", status_code=204)
def delete_quiz(quiz_id: int, session: Session = Depends(get_session)):
    quiz_obj = session.get(Quiz, quiz_id)
    if quiz_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    session.delete(quiz_obj)
    session.commit()


# ── Questions ─────────────────────────────────────────────────────────────────


@app.post(
    "/quizzes/{quiz_id}/questions",
    response_model=QuestionRead,
    status_code=201,
)
def create_question(
    quiz_id: int,
    question: QuestionCreate,
    session: Session = Depends(get_session),
):
    if session.get(Quiz, quiz_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    question_obj = Question(
        quiz_id=quiz_id,
        text=question.text,
        options=question.options,
        correct_index=question.correct_index,
    )
    session.add(question_obj)
    try:
        session.commit()
        session.refresh(question_obj)
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)

    return question_obj


@app.get(
    "/quizzes/{quiz_id}/questions",
    response_model=list[QuestionRead],
    status_code=200,
)
def list_questions(quiz_id: int, session: Session = Depends(get_session)):
    if session.get(Quiz, quiz_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    result = session.execute(
        select(Question).where(Question.quiz_id == quiz_id)
    )
    return result.scalars().all()


# ── Players ───────────────────────────────────────────────────────────────────


@app.post("/players", response_model=PlayerRead, status_code=201)
def create_player(
    player: PlayerCreate,
    session: Session = Depends(get_session),
):
    player_obj = Player(
        nickname=player.nickname,
        email=player.email,
    )
    session.add(player_obj)
    try:
        session.commit()
        session.refresh(player_obj)
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)

    return player_obj


@app.get("/players/{player_id}", response_model=PlayerRead, status_code=200)
def get_player(player_id: int, session: Session = Depends(get_session)):
    player_obj = session.get(Player, player_id)
    if player_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return player_obj


# ── Game Flow ─────────────────────────────────────────────────────────────────


@app.post(
    "/quizzes/{quiz_id}/start",
    response_model=AttemptStarted,
    status_code=201,
)
def start_attempt(
    quiz_id: int,
    attempt: AttemptStart,
    session: Session = Depends(get_session),
):
    quiz_obj = session.get(Quiz, quiz_id)
    if quiz_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if session.get(Player, attempt.player_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    attempt_obj = Attempt(
        player_id=attempt.player_id,
        quiz_id=quiz_id,
        started_at=datetime.utcnow(),
    )
    session.add(attempt_obj)
    session.commit()
    session.refresh(attempt_obj)

    return AttemptStarted(
        attempt_id=attempt_obj.id,
        started_at=attempt_obj.started_at,
        time_limit=quiz_obj.time_limit,
    )


@app.post(
    "/attempts/{attempt_id}/submit",
    response_model=AttemptResult,
    status_code=200,
)
def submit_attempt(
    attempt_id: int,
    submission: AttemptSubmit,
    session: Session = Depends(get_session),
):
    attempt_obj = session.get(Attempt, attempt_id)
    if attempt_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if attempt_obj.finished_at is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already submitted")

    quiz_obj = session.get(Quiz, attempt_obj.quiz_id)
    if quiz_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    elapsed = datetime.utcnow() - attempt_obj.started_at
    if elapsed.total_seconds() > quiz_obj.time_limit:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Time is up")

    questions = session.execute(
        select(Question).where(Question.quiz_id == quiz_obj.id)
    ).scalars().all()
    questions_by_id = {question.id: question for question in questions}
    max_score = len(questions)
    score = 0
    answered_ids: set[int] = set()

    for answer in submission.answers:
        if answer.question_id in answered_ids:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        answered_ids.add(answer.question_id)

        question_obj = questions_by_id.get(answer.question_id)
        if question_obj is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

        if answer.answer == question_obj.correct_index:
            score += 1

    attempt_obj.score = score
    attempt_obj.max_score = max_score
    attempt_obj.finished_at = datetime.utcnow()
    session.commit()
    session.refresh(attempt_obj)

    percent = 0.0
    if max_score > 0:
        percent = score / max_score * 100.0

    return AttemptResult(
        score=score,
        max_score=max_score,
        percent=percent,
        finished_at=attempt_obj.finished_at,
    )


# ── Leaderboard & Stats ──────────────────────────────────────────────────────


@app.get(
    "/quizzes/{quiz_id}/leaderboard",
    response_model=list[LeaderboardEntry],
    status_code=200,
)
def get_leaderboard(
    quiz_id: int,
    limit: int = 10,
    session: Session = Depends(get_session),
):
    if session.get(Quiz, quiz_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    rows = session.execute(
        select(Attempt, Player)
        .join(Player, Attempt.player_id == Player.id)
        .where(
            Attempt.quiz_id == quiz_id,
            Attempt.finished_at.is_not(None),
        )
    ).all()

    entries = []
    for attempt_obj, player_obj in rows:
        time_seconds = int((attempt_obj.finished_at - attempt_obj.started_at).total_seconds())
        entries.append(
            LeaderboardEntry(
                nickname=player_obj.nickname,
                score=attempt_obj.score,
                max_score=attempt_obj.max_score,
                time_seconds=time_seconds,
            )
        )

    entries.sort(key=lambda entry: (-entry.score, entry.time_seconds))
    return entries[:limit]


@app.get(
    "/players/{player_id}/stats",
    response_model=PlayerStats,
    status_code=200,
)
def get_player_stats(player_id: int, session: Session = Depends(get_session)):
    player_obj = session.get(Player, player_id)
    if player_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    rows = session.execute(
        select(Attempt, Quiz)
        .join(Quiz, Attempt.quiz_id == Quiz.id)
        .where(
            Attempt.player_id == player_id,
            Attempt.finished_at.is_not(None),
        )
    ).all()

    attempts = []
    for attempt_obj, quiz_obj in rows:
        percent = 0.0
        if attempt_obj.max_score and attempt_obj.max_score > 0:
            percent = attempt_obj.score / attempt_obj.max_score * 100.0
        attempts.append((attempt_obj, quiz_obj, percent))

    total_attempts = len(attempts)
    avg_score_percent = 0.0
    best_quiz = None
    if total_attempts > 0:
        avg_score_percent = sum(percent for _, _, percent in attempts) / total_attempts
        best_attempt = max(
            attempts,
            key=lambda item: (item[2], item[0].finished_at or datetime.min),
        )
        best_quiz = BestQuiz(
            quiz_title=best_attempt[1].title,
            score=best_attempt[0].score,
            max_score=best_attempt[0].max_score,
            percent=best_attempt[2],
        )

    return PlayerStats(
        player=player_obj,
        total_attempts=total_attempts,
        avg_score_percent=avg_score_percent,
        best_quiz=best_quiz,
    )


# ── Import (внешний API) ──────────────────────────────────────────────────────


@app.post(
    "/quizzes/{quiz_id}/import",
    response_model=list[QuestionRead],
    status_code=201,
)
async def import_questions(
    quiz_id: int,
    request: ImportRequest,
    session: Session = Depends(get_session),
):
    quiz_obj = session.get(Quiz, quiz_id)
    if quiz_obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://opentdb.com/api.php",
            params={"amount": request.amount, "type": "multiple"},
            timeout=10,
        )

    if response.status_code != 200:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY)

    try:
        payload = response.json()
    except ValueError:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY)

    if payload.get("response_code") != 0 or "results" not in payload:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY)

    questions = []
    for item in payload["results"]:
        options = list(item["incorrect_answers"])
        correct_answer = item["correct_answer"]
        options.append(correct_answer)
        random.shuffle(options)
        correct_index = options.index(correct_answer)

        question_obj = Question(
            quiz_id=quiz_id,
            text=item["question"],
            options=options,
            correct_index=correct_index,
        )
        session.add(question_obj)
        questions.append(question_obj)

    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY)

    for question_obj in questions:
        session.refresh(question_obj)

    return questions
