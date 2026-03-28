"""
Тесты Задачи 2: CRUD-эндпоинты (20 баллов).

Проверяют полный набор CRUD-операций для всех сущностей.

НЕ ИЗМЕНЯЙТЕ ЭТОТ ФАЙЛ.
"""

import pytest

# ── Categories (3 балла) ─────────────────────────────────────────────────────


class TestCategoriesCRUD:
    """POST /categories + GET /categories."""

    @pytest.mark.task(2)
    @pytest.mark.points(1)
    def test_create_category(self, client):
        r = client.post("/categories", json={"name": "Geography"})
        assert r.status_code == 201
        data = r.json()
        assert data["name"] == "Geography"
        assert "id" in data

    @pytest.mark.task(2)
    @pytest.mark.points(1)
    def test_list_categories(self, client, seed_data):
        r = client.get("/categories")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) >= 2  # Python, Science from seed
        assert all("id" in c and "name" in c for c in data)

    @pytest.mark.task(2)
    @pytest.mark.points(1)
    def test_list_categories_contains_seed(self, client, seed_data):
        r = client.get("/categories")
        names = [c["name"] for c in r.json()]
        assert "Python" in names
        assert "Science" in names


# ── Quizzes (7 баллов) ───────────────────────────────────────────────────────


class TestQuizzesCRUD:
    """POST + GET list + GET one + DELETE."""

    @pytest.mark.task(2)
    @pytest.mark.points(1)
    def test_create_quiz(self, client, seed_data):
        r = client.post("/quizzes", json={
            "title": "CRUD Test Quiz",
            "category_id": seed_data["categories"]["Python"],
            "time_limit": 60,
        })
        assert r.status_code == 201
        data = r.json()
        assert data["title"] == "CRUD Test Quiz"
        assert "id" in data
        assert "created_at" in data

    @pytest.mark.task(2)
    @pytest.mark.points(1)
    def test_list_quizzes(self, client, seed_data):
        r = client.get("/quizzes")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) >= 2  # Python Basics, Physics 101 from seed

    @pytest.mark.task(2)
    @pytest.mark.points(2)
    def test_get_quiz_by_id(self, client, seed_data):
        quiz_id = seed_data["quizzes"]["Python Basics"]
        r = client.get(f"/quizzes/{quiz_id}")
        assert r.status_code == 200
        data = r.json()
        assert data["title"] == "Python Basics"
        assert data["id"] == quiz_id
        # QuizDetail должен содержать questions_count
        assert "questions_count" in data
        assert data["questions_count"] >= 3

    @pytest.mark.task(2)
    @pytest.mark.points(1)
    def test_get_quiz_not_found(self, client):
        r = client.get("/quizzes/99999")
        assert r.status_code == 404

    @pytest.mark.task(2)
    @pytest.mark.points(2)
    def test_delete_quiz(self, client, seed_data):
        """Создаём квиз, добавляем вопрос, удаляем всё каскадно."""
        r = client.post("/quizzes", json={
            "title": "To Delete",
            "category_id": seed_data["categories"]["Science"],
            "time_limit": 30,
        })
        qid = r.json()["id"]

        # Добавляем вопрос
        client.post(f"/quizzes/{qid}/questions", json={
            "text": "Test?",
            "options": ["A", "B"],
            "correct_index": 0,
        })

        # Удаляем
        r = client.delete(f"/quizzes/{qid}")
        assert r.status_code == 204

        # Проверяем что удалился
        r = client.get(f"/quizzes/{qid}")
        assert r.status_code == 404


# ── Questions (5 баллов) ─────────────────────────────────────────────────────


class TestQuestionsCRUD:
    """POST + GET (без correct_index!)."""

    @pytest.mark.task(2)
    @pytest.mark.points(2)
    def test_create_question(self, client, seed_data):
        quiz_id = seed_data["quizzes"]["Physics 101"]
        r = client.post(f"/quizzes/{quiz_id}/questions", json={
            "text": "What is gravity?",
            "options": ["A force", "A color", "A sound"],
            "correct_index": 0,
        })
        assert r.status_code == 201
        data = r.json()
        assert data["text"] == "What is gravity?"
        assert "id" in data

    @pytest.mark.task(2)
    @pytest.mark.points(3)
    def test_list_questions_without_correct_index(self, client, seed_data):
        """GET /quizzes/{id}/questions correct_index НЕ должен возвращаться!"""
        quiz_id = seed_data["quizzes"]["Python Basics"]
        r = client.get(f"/quizzes/{quiz_id}/questions")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) >= 3

        for q in data:
            assert "id" in q
            assert "text" in q
            assert "options" in q
            assert isinstance(q["options"], list)
            # КЛЮЧЕВАЯ ПРОВЕРКА: correct_index не раскрывается!
            assert "correct_index" not in q, (
                "GET /quizzes/{id}/questions НЕ должен возвращать correct_index! "
                "Не раскрывайте правильные ответы."
            )


# ── Players (3 балла) ────────────────────────────────────────────────────────


class TestPlayersCRUD:
    """POST + GET."""

    @pytest.mark.task(2)
    @pytest.mark.points(1)
    def test_create_player(self, client):
        r = client.post("/players", json={
            "nickname": "dave_crud",
            "email": "dave_crud@hse.ru",
        })
        assert r.status_code == 201
        data = r.json()
        assert data["nickname"] == "dave_crud"
        assert "id" in data

    @pytest.mark.task(2)
    @pytest.mark.points(2)
    def test_get_player_by_id(self, client, seed_data):
        player_id = seed_data["players"]["alice"]
        r = client.get(f"/players/{player_id}")
        assert r.status_code == 200
        data = r.json()
        assert data["nickname"] == "alice"
        assert data["email"] == "alice@hse.ru"
        assert data["id"] == player_id


# ── Фильтрация (2 балла) ────────────────────────────────────────────────────


class TestQuizzesFilter:
    """GET /quizzes?category_id=..."""

    @pytest.mark.task(2)
    @pytest.mark.points(2)
    def test_filter_by_category(self, client, seed_data):
        cat_id = seed_data["categories"]["Python"]
        r = client.get("/quizzes", params={"category_id": cat_id})
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert all(q["category_id"] == cat_id for q in data)

        # Проверяем, что Physics не попал
        titles = [q["title"] for q in data]
        assert "Physics 101" not in titles
