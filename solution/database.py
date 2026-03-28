"""
Подключение к PostgreSQL через SQLAlchemy ORM.

Этот файл готов к использованию менять не обязательно.

DATABASE_URL берётся из переменной окружения (в CI выставлена автоматически).
Локально подключение к базе quiz_arena без пароля:
    postgresql+psycopg2:///quiz_arena

Если нужен пароль:
    postgresql+psycopg2://postgres:postgres@localhost:5432/quiz_arena
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2:///quiz_arena",
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


def get_session():
    """FastAPI Dependency: выдаёт SQLAlchemy-сессию."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
