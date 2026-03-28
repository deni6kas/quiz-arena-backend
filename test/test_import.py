"""
Тесты Задачи 4: Импорт из внешнего API (15 баллов).

Проверяют:
  - Успешный импорт вопросов из Open Trivia DB (мок через respx)
  - Трансформацию формата (options + correct_index)
  - Обработку ошибок внешнего API -> 502

Эти тесты используют httpx.AsyncClient + ASGI transport (в отличие от остальных,
которые работают через subprocess). Это необходимо для перехвата
исходящих HTTP-запросов через respx.

НЕ ИЗМЕНЯЙТЕ ЭТОТ ФАЙЛ.
"""

from test.mock_data import MOCK_TRIVIA_RESPONSE

import pytest
import respx
from httpx import ASGITransport, AsyncClient, Response


@pytest.fixture
async def asgi_client():
    """Async-клиент через ASGI transport для перехвата внешних запросов через respx."""
    from solution.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture
def import_quiz(client, seed_data):
    """Создаёт отдельный квиз для тестов импорта (через subprocess сервер)."""
    cat_id = seed_data["categories"]["Science"]
    r = client.post("/quizzes", json={
        "title": "Import Quiz",
        "category_id": cat_id,
        "time_limit": 120,
    })
    assert r.status_code == 201
    return r.json()["id"]


# ── Успешный импорт (7 баллов) ───────────────────────────────────────────────


class TestImportSuccess:
    """POST /quizzes/{id}/import с мок-ответом."""

    @pytest.mark.task(4)
    @pytest.mark.points(3)
    @respx.mock
    async def test_import_creates_questions(self, asgi_client, import_quiz):
        """Импорт 3 вопросов -> 201, вопросы создаются."""
        quiz_id = import_quiz

        respx.get("https://opentdb.com/api.php").mock(
            return_value=Response(200, json=MOCK_TRIVIA_RESPONSE)
        )
        r = await asgi_client.post(f"/quizzes/{quiz_id}/import", json={"amount": 3})

        assert r.status_code == 201
        data = r.json()
        assert isinstance(data, list)
        assert len(data) == 3

    @pytest.mark.task(4)
    @pytest.mark.points(3)
    @respx.mock
    async def test_import_questions_have_correct_fields(self, asgi_client, seed_data):
        """Импортированные вопросы содержат text, options, id."""
        cat_id = seed_data["categories"]["Science"]

        # Создаём отдельный квиз
        r = await asgi_client.post("/quizzes", json={
            "title": "Import Fields Quiz",
            "category_id": cat_id,
            "time_limit": 120,
        })
        assert r.status_code == 201
        quiz_id = r.json()["id"]

        respx.get("https://opentdb.com/api.php").mock(
            return_value=Response(200, json=MOCK_TRIVIA_RESPONSE)
        )
        r = await asgi_client.post(f"/quizzes/{quiz_id}/import", json={"amount": 3})

        assert r.status_code == 201
        data = r.json()

        for q in data:
            assert "id" in q
            assert "text" in q
            assert "options" in q
            assert isinstance(q["options"], list)
            assert len(q["options"]) == 4  # 1 correct + 3 incorrect


# ── Трансформация формата (5 баллов) ─────────────────────────────────────────


class TestImportTransformation:
    """Проверяем, что correct_answer попал в options и correct_index корректен."""

    @pytest.mark.task(4)
    @pytest.mark.points(3)
    @respx.mock
    async def test_correct_answer_in_options(self, asgi_client, seed_data):
        """correct_answer из API должен быть среди options."""
        cat_id = seed_data["categories"]["Science"]

        r = await asgi_client.post("/quizzes", json={
            "title": "Transform Test Quiz",
            "category_id": cat_id,
            "time_limit": 120,
        })
        assert r.status_code == 201
        quiz_id = r.json()["id"]

        respx.get("https://opentdb.com/api.php").mock(
            return_value=Response(200, json=MOCK_TRIVIA_RESPONSE)
        )
        r = await asgi_client.post(f"/quizzes/{quiz_id}/import", json={"amount": 3})
        assert r.status_code == 201

        # Получаем вопросы через API (без correct_index)
        r = await asgi_client.get(f"/quizzes/{quiz_id}/questions")
        assert r.status_code == 200
        questions = r.json()

        for q in questions:
            # Находим оригинальный вопрос из мока
            original = next(
                (item for item in MOCK_TRIVIA_RESPONSE["results"]
                 if item["question"] == q["text"]),
                None,
            )
            if original is None:
                continue

            # correct_answer должен быть в options
            assert original["correct_answer"] in q["options"], (
                f"correct_answer '{original['correct_answer']}' "
                f"not found in options {q['options']}"
            )
            # Все incorrect_answers тоже должны быть в options
            for wrong in original["incorrect_answers"]:
                assert wrong in q["options"], (
                    f"incorrect_answer '{wrong}' not found in options {q['options']}"
                )

    @pytest.mark.task(4)
    @pytest.mark.points(2)
    @respx.mock
    async def test_import_correct_index_is_valid(self, asgi_client, seed_data):
        """Проверяем, что correct_index корректен: проходим импортированный квиз с правильными ответами."""
        cat_id = seed_data["categories"]["Science"]

        # Создаём квиз
        r = await asgi_client.post("/quizzes", json={
            "title": "Verify Import Quiz",
            "category_id": cat_id,
            "time_limit": 300,
        })
        assert r.status_code == 201
        quiz_id = r.json()["id"]

        # Импортируем вопросы
        from test.mock_data import MOCK_TRIVIA_RESPONSE
        respx.get("https://opentdb.com/api.php").mock(
            return_value=Response(200, json=MOCK_TRIVIA_RESPONSE)
        )
        r = await asgi_client.post(f"/quizzes/{quiz_id}/import", json={"amount": 3})
        assert r.status_code == 201

        # Создаём игрока
        r = await asgi_client.post("/players", json={
            "nickname": "import_verify_player",
            "email": "import_verify@hse.ru",
        })
        assert r.status_code == 201
        player_id = r.json()["id"]

        # Начинаем попытку
        r = await asgi_client.post(f"/quizzes/{quiz_id}/start", json={"player_id": player_id})
        assert r.status_code == 201
        attempt_id = r.json()["attempt_id"]

        # Получаем вопросы
        r = await asgi_client.get(f"/quizzes/{quiz_id}/questions")
        assert r.status_code == 200
        questions = r.json()
        assert len(questions) == 3

        # Для каждого вопроса находим правильный ответ из мока
        answers = []
        for q in questions:
            original = next(
                (item for item in MOCK_TRIVIA_RESPONSE["results"]
                 if item["question"] == q["text"]),
                None,
            )
            assert original is not None, f"Question '{q['text']}' not found in mock data"
            correct_answer = original["correct_answer"]
            correct_idx = q["options"].index(correct_answer)
            answers.append({"question_id": q["id"], "answer": correct_idx})

        # Отправляем ответы все должны быть правильными
        r = await asgi_client.post(f"/attempts/{attempt_id}/submit", json={"answers": answers})
        assert r.status_code == 200
        data = r.json()
        assert data["score"] == 3, (
            f"Все ответы правильные, но score={data['score']}. "
            "Проверьте, что correct_index при импорте вычислен корректно."
        )


# ── Ошибка внешнего API (3 балла) ────────────────────────────────────────────


class TestImportAPIError:
    """Ошибка внешнего API -> 502."""

    @pytest.mark.task(4)
    @pytest.mark.points(1)
    @respx.mock
    async def test_import_invalid_amount(self, asgi_client, seed_data):
        """amount=0 -> 422."""
        quiz_id = seed_data["quizzes"]["Python Basics"]
        r = await asgi_client.post(f"/quizzes/{quiz_id}/import", json={"amount": 0})
        assert r.status_code == 422

    @pytest.mark.task(4)
    @pytest.mark.points(3)
    @respx.mock
    async def test_external_api_error_returns_502(self, asgi_client, seed_data):
        """Внешний API вернул 500 -> наш сервер отвечает 502."""
        quiz_id = seed_data["quizzes"]["Python Basics"]

        respx.get("https://opentdb.com/api.php").mock(
            return_value=Response(500, json={"error": "Internal Server Error"})
        )
        r = await asgi_client.post(f"/quizzes/{quiz_id}/import", json={"amount": 3})

        assert r.status_code == 502
