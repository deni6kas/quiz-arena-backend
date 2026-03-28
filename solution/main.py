"""
FastAPI-приложение Quiz Arena.

TODO: реализуйте все эндпоинты.
      Каждый эндпоинт заглушка с raise HTTPException(501).
      Замените их на рабочую логику.

Подсказки:
  - Используйте Depends(get_session) для получения сессии БД
  - Ловите IntegrityError от SQLAlchemy и возвращайте 409/400
  - Для импорта вопросов используйте httpx.AsyncClient
  - Сервер НЕ должен возвращать 500 ловите все исключения БД
"""

from fastapi import Depends, FastAPI, HTTPException, status
# ВАЖНО: импортируйте models, чтобы SQLAlchemy узнал о ваших таблицах.
# Без этого импорта Base.metadata будет пустой и create_all ничего не создаст.
from solution import models  # noqa: F401
from solution.database import Base, engine, get_session  # noqa: F401
from sqlalchemy.orm import Session

app = FastAPI(title="Quiz Arena API")

# Создаём таблицы при старте (если ещё не существуют).
# Раскомментируйте после того, как опишете модели в models.py:
# Base.metadata.create_all(bind=engine)


# ── Categories ────────────────────────────────────────────────────────────────


@app.post("/categories", status_code=201)
def create_category(session: Session = Depends(get_session)):
    """POST /categories -> 201, CategoryRead"""
    # TODO: создать категорию {"name": "..."}
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@app.get("/categories", status_code=200)
def list_categories(session: Session = Depends(get_session)):
    """GET /categories -> 200, list[CategoryRead]"""
    # TODO: вернуть список всех категорий
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


# ── Quizzes ───────────────────────────────────────────────────────────────────


@app.post("/quizzes", status_code=201)
def create_quiz(session: Session = Depends(get_session)):
    """POST /quizzes -> 201, QuizRead"""
    # TODO: создать квиз {"title", "category_id", "time_limit"}
    # time_limit >= 30 (валидация через Pydantic)
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@app.get("/quizzes", status_code=200)
def list_quizzes(category_id: int | None = None, session: Session = Depends(get_session)):
    """GET /quizzes -> 200, list[QuizRead]
    Query param: category_id (опционально) фильтрация по категории.
    """
    # TODO: вернуть список квизов, при наличии category_id фильтровать
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@app.get("/quizzes/{quiz_id}", status_code=200)
def get_quiz(quiz_id: int, session: Session = Depends(get_session)):
    """GET /quizzes/{id} -> 200, QuizDetail (с questions_count)"""
    # TODO: вернуть квиз по id, включая questions_count
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@app.delete("/quizzes/{quiz_id}", status_code=204)
def delete_quiz(quiz_id: int, session: Session = Depends(get_session)):
    """DELETE /quizzes/{id} -> 204 (каскадно удаляет вопросы и попытки)"""
    # TODO: удалить квиз, вопросы удаляются каскадно
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


# ── Questions ─────────────────────────────────────────────────────────────────


@app.post("/quizzes/{quiz_id}/questions", status_code=201)
def create_question(quiz_id: int, session: Session = Depends(get_session)):
    """POST /quizzes/{id}/questions -> 201
    Body: {"text", "options": [...], "correct_index": N}
    """
    # TODO: добавить вопрос к квизу
    # Валидация: options список из 2-6 строк, correct_index >= 0
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@app.get("/quizzes/{quiz_id}/questions", status_code=200)
def list_questions(quiz_id: int, session: Session = Depends(get_session)):
    """GET /quizzes/{id}/questions -> 200, list[QuestionRead]
    ВАЖНО: correct_index НЕ возвращается! Не раскрываем ответы.
    """
    # TODO: вернуть список вопросов квиза БЕЗ correct_index
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


# ── Players ───────────────────────────────────────────────────────────────────


@app.post("/players", status_code=201)
def create_player(session: Session = Depends(get_session)):
    """POST /players -> 201, PlayerRead"""
    # TODO: зарегистрировать игрока {"nickname", "email"}
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@app.get("/players/{player_id}", status_code=200)
def get_player(player_id: int, session: Session = Depends(get_session)):
    """GET /players/{id} -> 200, PlayerRead"""
    # TODO: вернуть игрока по id
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


# ── Game Flow ─────────────────────────────────────────────────────────────────


@app.post("/quizzes/{quiz_id}/start", status_code=201)
def start_attempt(quiz_id: int, session: Session = Depends(get_session)):
    """POST /quizzes/{id}/start -> 201
    Body: {"player_id": N}
    Response: {"attempt_id", "started_at", "time_limit"}
    """
    # TODO: создать попытку прохождения
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@app.post("/attempts/{attempt_id}/submit", status_code=200)
def submit_attempt(attempt_id: int, session: Session = Depends(get_session)):
    """POST /attempts/{id}/submit -> 200
    Body: {"answers": [{"question_id": N, "answer": M}, ...]}
    Response: {"score", "max_score", "percent", "finished_at"}

    Логика:
      1. Проверить, что попытка существует и не завершена (finished_at is NULL)
         - Если finished_at заполнен -> 409 "Already submitted"
      2. Проверить time_limit: если now() - started_at > time_limit -> 400 "Time is up"
      3. Для каждого ответа:
         - Найти вопрос по question_id (должен принадлежать quiz_id попытки)
         - Сравнить answer с correct_index -> если совпадает, +1 к score
      4. Записать score, max_score = кол-во вопросов, finished_at = now()
    """
    # TODO: реализовать подсчёт очков
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


# ── Leaderboard & Stats ──────────────────────────────────────────────────────


@app.get("/quizzes/{quiz_id}/leaderboard", status_code=200)
def get_leaderboard(quiz_id: int, limit: int = 10, session: Session = Depends(get_session)):
    """GET /quizzes/{id}/leaderboard -> 200
    Query: limit (default 10)
    Response: list[LeaderboardEntry]
      - nickname, score, max_score, time_seconds
      - Сортировка: score DESC, при равенстве time_seconds ASC
      - Только завершённые попытки (finished_at IS NOT NULL)
    """
    # TODO: реализовать лидерборд
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@app.get("/players/{player_id}/stats", status_code=200)
def get_player_stats(player_id: int, session: Session = Depends(get_session)):
    """GET /players/{id}/stats -> 200
    Response: {
      "player": PlayerRead,
      "total_attempts": int,
      "avg_score_percent": float,
      "best_quiz": {"quiz_title", "score", "max_score", "percent"} | null
    }
    Считаются только завершённые попытки.
    """
    # TODO: реализовать статистику игрока
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


# ── Import (внешний API) ─────────────────────────────────────────────────────


@app.post("/quizzes/{quiz_id}/import", status_code=201)
async def import_questions(quiz_id: int, session: Session = Depends(get_session)):
    """POST /quizzes/{id}/import -> 201
    Body: {"amount": N}  (1 <= N <= 20)

    1. Отправить GET к https://opentdb.com/api.php?amount=N&type=multiple
    2. Трансформировать: из incorrect_answers + correct_answer собрать options
       (перемешать!), вычислить correct_index
    3. Сохранить вопросы в БД
    4. Вернуть список созданных вопросов
    5. При ошибке внешнего API -> 502
    """
    # TODO: реализовать импорт из Open Trivia DB
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
