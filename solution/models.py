"""
SQLAlchemy-модели для базы quiz_arena.

Таблицы:
  - categories   категории квизов
  - quizzes      квизы (FK -> categories)
  - questions    вопросы (FK -> quizzes, CASCADE)
  - players      игроки
  - attempts     попытки прохождения (FK -> players, quizzes)

TODO: опишите модели.
      Используйте DeclarativeBase из database.py.
      Не забудьте про UNIQUE, FK, CHECK-ограничения и каскадное удаление.
"""

from solution.database import Base  # noqa: F401

# TODO: импорты из sqlalchemy (Column, Integer, String, ForeignKey, JSON, DateTime, ...)

# TODO: модель Category
#   id    SERIAL PRIMARY KEY
#   name  VARCHAR UNIQUE NOT NULL

# TODO: модель Quiz
#   id           SERIAL PRIMARY KEY
#   title        VARCHAR NOT NULL
#   category_id  INTEGER FK -> categories (NOT NULL)
#   time_limit   INTEGER NOT NULL (>= 30, секунды)
#   created_at   TIMESTAMP DEFAULT now()

# TODO: модель Question
#   id             SERIAL PRIMARY KEY
#   quiz_id        INTEGER FK -> quizzes ON DELETE CASCADE
#   text           VARCHAR NOT NULL
#   options        JSON NOT NULL (список из 2-6 строк)
#   correct_index  INTEGER NOT NULL (>= 0)

# TODO: модель Player
#   id        SERIAL PRIMARY KEY
#   nickname  VARCHAR UNIQUE NOT NULL
#   email     VARCHAR UNIQUE NOT NULL

# TODO: модель Attempt
#   id           SERIAL PRIMARY KEY
#   player_id    INTEGER FK -> players (NOT NULL)
#   quiz_id      INTEGER FK -> quizzes ON DELETE CASCADE
#   score        INTEGER (NULL пока не завершена)
#   max_score    INTEGER (NULL пока не завершена)
#   started_at   TIMESTAMP NOT NULL DEFAULT now()
#   finished_at  TIMESTAMP (NULL пока не завершена)
