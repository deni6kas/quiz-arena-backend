"""
Pydantic-схемы для валидации запросов и ответов.

TODO: опишите схемы для каждой сущности.
      Как минимум нужны:

      Categories:
        - CategoryCreate  (name: str, min_length=1)
        - CategoryRead    (id, name)

      Quizzes:
        - QuizCreate      (title, category_id, time_limit >= 30)
        - QuizRead        (id, title, category_id, time_limit, created_at)
        - QuizDetail      (QuizRead + questions_count)

      Questions:
        - QuestionCreate  (text, options: list[str] длина 2-6, correct_index >= 0)
        - QuestionRead    (id, quiz_id, text, options БЕЗ correct_index!)
        - QuestionFull    (QuestionRead + correct_index только для внутреннего использования)

      Players:
        - PlayerCreate    (nickname, email)
        - PlayerRead      (id, nickname, email)

      Attempts:
        - AttemptStart    (player_id)
        - AttemptStarted  (attempt_id, started_at, time_limit)
        - AnswerItem      (question_id, answer: int)
        - AttemptSubmit   (answers: list[AnswerItem])
        - AttemptResult   (score, max_score, percent, finished_at)

      Leaderboard:
        - LeaderboardEntry (nickname, score, max_score, time_seconds)

      Stats:
        - BestQuiz        (quiz_title, score, max_score, percent)
        - PlayerStats     (player: PlayerRead, total_attempts, avg_score_percent, best_quiz)

      Import:
        - ImportRequest   (amount: int, 1-20)
"""

from pydantic import BaseModel  # noqa: F401

# TODO: ваши схемы здесь
