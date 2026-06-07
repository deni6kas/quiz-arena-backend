# Quiz Arena API

Backend implementation of an online quiz platform.

The project implements a FastAPI-based backend for managing quiz categories, quizzes, questions, players, and quiz attempts.
It supports the full quiz flow: creating quizzes, submitting answers, scoring attempts, and generating leaderboards and player statistics.

Key features:
- category management for quiz organization
- quiz creation, retrieval, filtering, and deletion
- question management with validation for options and correct answers
- player registration and profile retrieval
- quiz attempts with score calculation and time limit enforcement
- leaderboard and player performance statistics
- importing multiple-choice questions from an external API

Tech stack:
- Python 3.12+
- FastAPI for REST endpoints
- SQLAlchemy ORM for database models
- Pydantic for request validation and response schemas
- PostgreSQL as the target database

## My implementation

Implemented by me in `solution/`:
- `solution/models.py` — SQLAlchemy models for categories, quizzes, questions, players, and attempts
- `solution/schemas.py` — Pydantic schemas for request validation and response serialization
- `solution/main.py` — FastAPI application and API endpoints

## Provided by assignment authors

The following files and folders were provided as scaffolding and were not changed as part of the implementation:
- `test/` — automated tests used for validation
- `.github/workflows/ci.yml` — CI configuration
- `Makefile` — common run/test commands
- `pyproject.toml`, `requirements.txt` — project dependencies and metadata
- `README.md` — original assignment instructions

`solution/database.py` was provided as boilerplate for PostgreSQL connection and session management.

## Run locally

1. Create virtual environment and install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. Start PostgreSQL and create database `quiz_arena`.

3. Run the app:

```bash
uvicorn solution.main:app --reload
```

4. Run tests:

```bash
pytest test -s
```

## What this project does

The API supports:
- creating and listing categories
- creating, listing, retrieving, and deleting quizzes
- adding and listing quiz questions
- creating players and retrieving player profiles
- starting quiz attempts and submitting answers
- leaderboard and player statistics
- importing quiz questions from an external API

## Notes

- The code in `solution/models.py`, `solution/schemas.py`, and `solution/main.py` is my implementation.
- The repository includes original assignment scaffolding and tests from the exam template.
