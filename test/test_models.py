"""
Тесты Задачи 1: Модели (15 баллов).

Проверяют, что SQLAlchemy-модели и Pydantic-схемы корректно описаны:
  - Сущности создаются через API с правильной структурой ответа
  - Валидация отклоняет невалидные данные (422)

НЕ ИЗМЕНЯЙТЕ ЭТОТ ФАЙЛ.
"""

import pytest


class TestCategoryModel:
    """Создание категорий через API."""

    @pytest.mark.task(1)
    @pytest.mark.points(2)
    def test_create_category(self, client):
        r = client.post("/categories", json={"name": "History"})
        assert r.status_code == 201
        data = r.json()
        assert "id" in data
        assert data["name"] == "History"

    @pytest.mark.task(1)
    @pytest.mark.points(1)
    def test_create_category_empty_name(self, client):
        """Пустое имя -> 422."""
        r = client.post("/categories", json={"name": ""})
        assert r.status_code == 422


class TestQuizModel:
    """Создание квизов через API."""

    @pytest.mark.task(1)
    @pytest.mark.points(2)
    def test_create_quiz(self, client, seed_data):
        cat_id = seed_data["categories"]["Python"]
        r = client.post("/quizzes", json={
            "title": "Advanced Python",
            "category_id": cat_id,
            "time_limit": 120,
        })
        assert r.status_code == 201
        data = r.json()
        assert "id" in data
        assert data["title"] == "Advanced Python"
        assert data["category_id"] == cat_id
        assert data["time_limit"] == 120
        assert "created_at" in data

    @pytest.mark.task(1)
    @pytest.mark.points(2)
    def test_create_quiz_time_limit_too_low(self, client, seed_data):
        """time_limit < 30 -> 422."""
        cat_id = seed_data["categories"]["Python"]
        r = client.post("/quizzes", json={
            "title": "Quick Quiz",
            "category_id": cat_id,
            "time_limit": 10,
        })
        assert r.status_code == 422


class TestQuestionModel:
    """Создание вопросов через API."""

    @pytest.mark.task(1)
    @pytest.mark.points(2)
    def test_create_question(self, client, seed_data):
        quiz_id = seed_data["quizzes"]["Physics 101"]
        r = client.post(f"/quizzes/{quiz_id}/questions", json={
            "text": "What is Python?",
            "options": ["A snake", "A language", "A game", "A movie"],
            "correct_index": 1,
        })
        assert r.status_code == 201
        data = r.json()
        assert "id" in data
        assert data["text"] == "What is Python?"

    @pytest.mark.task(1)
    @pytest.mark.points(1)
    def test_create_question_empty_options(self, client, seed_data):
        """Пустой список options -> 422."""
        quiz_id = seed_data["quizzes"]["Python Basics"]
        r = client.post(f"/quizzes/{quiz_id}/questions", json={
            "text": "Bad question",
            "options": [],
            "correct_index": 0,
        })
        assert r.status_code == 422

    @pytest.mark.task(1)
    @pytest.mark.points(1)
    def test_create_question_too_many_options(self, client, seed_data):
        """Больше 6 вариантов -> 422."""
        quiz_id = seed_data["quizzes"]["Python Basics"]
        r = client.post(f"/quizzes/{quiz_id}/questions", json={
            "text": "Too many options",
            "options": ["a", "b", "c", "d", "e", "f", "g"],
            "correct_index": 0,
        })
        assert r.status_code == 422

    @pytest.mark.task(1)
    @pytest.mark.points(1)
    def test_create_question_negative_correct_index(self, client, seed_data):
        """correct_index < 0 -> 422."""
        quiz_id = seed_data["quizzes"]["Python Basics"]
        r = client.post(f"/quizzes/{quiz_id}/questions", json={
            "text": "Bad index",
            "options": ["a", "b"],
            "correct_index": -1,
        })
        assert r.status_code == 422


class TestPlayerModel:
    """Создание игроков через API."""

    @pytest.mark.task(1)
    @pytest.mark.points(2)
    def test_create_player(self, client):
        r = client.post("/players", json={
            "nickname": "charlie",
            "email": "charlie@hse.ru",
        })
        assert r.status_code == 201
        data = r.json()
        assert "id" in data
        assert data["nickname"] == "charlie"
        assert data["email"] == "charlie@hse.ru"

    @pytest.mark.task(1)
    @pytest.mark.points(1)
    def test_create_player_no_body(self, client):
        """Без тела -> 422."""
        r = client.post("/players")
        assert r.status_code == 422
