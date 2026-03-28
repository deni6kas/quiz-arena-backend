"""
Тесты Задачи 3: Игровая механика (25 баллов).

Проверяют:
  - Начало попытки (start)
  - Отправку ответов (submit) с подсчётом очков
  - Проверку таймера (time_limit)
  - Защиту от повторного submit

НЕ ИЗМЕНЯЙТЕ ЭТОТ ФАЙЛ.
"""

import pytest

# ── Start Attempt (5 баллов) ─────────────────────────────────────────────────


class TestStartAttempt:
    """POST /quizzes/{id}/start."""

    @pytest.mark.task(3)
    @pytest.mark.points(3)
    def test_start_attempt(self, client, seed_data):
        quiz_id = seed_data["quizzes"]["Python Basics"]
        player_id = seed_data["players"]["alice"]

        r = client.post(f"/quizzes/{quiz_id}/start", json={"player_id": player_id})
        assert r.status_code == 201
        data = r.json()
        assert "attempt_id" in data
        assert "started_at" in data
        assert "time_limit" in data
        assert data["time_limit"] == 300

    @pytest.mark.task(3)
    @pytest.mark.points(2)
    def test_start_attempt_quiz_not_found(self, client, seed_data):
        player_id = seed_data["players"]["alice"]
        r = client.post("/quizzes/99999/start", json={"player_id": player_id})
        assert r.status_code == 404


# ── Submit Attempt (10 баллов) ───────────────────────────────────────────────


class TestSubmitAttempt:
    """POST /attempts/{id}/submit."""

    @pytest.mark.task(3)
    @pytest.mark.points(4)
    def test_submit_all_correct(self, client, seed_data):
        """Все ответы правильные -> score = max_score."""
        quiz_id = seed_data["quizzes"]["Python Basics"]
        player_id = seed_data["players"]["bob"]
        question_ids = seed_data["questions"]["Python Basics"]

        # Начинаем попытку
        r = client.post(f"/quizzes/{quiz_id}/start", json={"player_id": player_id})
        assert r.status_code == 201
        attempt_id = r.json()["attempt_id"]

        # Правильные ответы: correct_index = 2, 1, 1
        answers = [
            {"question_id": question_ids[0], "answer": 2},
            {"question_id": question_ids[1], "answer": 1},
            {"question_id": question_ids[2], "answer": 1},
        ]

        r = client.post(f"/attempts/{attempt_id}/submit", json={"answers": answers})
        assert r.status_code == 200
        data = r.json()
        assert data["score"] == 3
        assert data["max_score"] == 3
        assert data["percent"] == pytest.approx(100.0, abs=0.1)
        assert "finished_at" in data

    @pytest.mark.task(3)
    @pytest.mark.points(4)
    def test_submit_partial_correct(self, client, seed_data):
        """Часть ответов правильная."""
        quiz_id = seed_data["quizzes"]["Python Basics"]
        player_id = seed_data["players"]["alice"]
        question_ids = seed_data["questions"]["Python Basics"]

        # Начинаем новую попытку (повторные попытки на тот же квиз разрешены)
        r = client.post(f"/quizzes/{quiz_id}/start", json={"player_id": player_id})
        assert r.status_code == 201, (
            "Повторные попытки одного игрока на тот же квиз должны быть разрешены. "
            "Не добавляйте UNIQUE(player_id, quiz_id) в таблицу attempts."
        )
        attempt_id = r.json()["attempt_id"]

        # 1 правильный (первый), 2 неправильных
        answers = [
            {"question_id": question_ids[0], "answer": 2},  # correct
            {"question_id": question_ids[1], "answer": 0},  # wrong (correct=1)
            {"question_id": question_ids[2], "answer": 3},  # wrong (correct=1)
        ]

        r = client.post(f"/attempts/{attempt_id}/submit", json={"answers": answers})
        assert r.status_code == 200
        data = r.json()
        assert data["score"] == 1
        assert data["max_score"] == 3
        assert data["percent"] == pytest.approx(33.33, abs=1.0)

    @pytest.mark.task(3)
    @pytest.mark.points(2)
    def test_submit_incomplete_answers(self, client, seed_data):
        """Отправка ответов не на все вопросы: max_score = кол-во вопросов, а не ответов."""
        quiz_id = seed_data["quizzes"]["Python Basics"]
        player_id = seed_data["players"]["bob"]
        question_ids = seed_data["questions"]["Python Basics"]

        # Начинаем попытку
        r = client.post(f"/quizzes/{quiz_id}/start", json={"player_id": player_id})
        assert r.status_code == 201
        attempt_id = r.json()["attempt_id"]

        # Отправляем ответ только на 1 из 3 вопросов (правильный)
        answers = [
            {"question_id": question_ids[0], "answer": 2},
        ]

        r = client.post(f"/attempts/{attempt_id}/submit", json={"answers": answers})
        assert r.status_code == 200
        data = r.json()
        assert data["score"] == 1
        assert data["max_score"] == 3, (
            f"max_score должен быть равен количеству вопросов в квизе (3), "
            f"а не количеству отправленных ответов ({len(answers)}). "
            f"Получено: max_score={data['max_score']}"
        )


# ── Time Limit (5 баллов) ────────────────────────────────────────────────────


class TestTimeLimit:
    """Submit после истечения time_limit -> 400."""

    @pytest.mark.task(3)
    @pytest.mark.points(5)
    @pytest.mark.slow
    def test_submit_after_time_limit(self, client, seed_data):
        """Квиз с time_limit=30: ждём 31 сек, submit после истечения -> 400."""
        import time

        # Создаём квиз с минимальным time_limit
        cat_id = seed_data["categories"]["Science"]
        r = client.post("/quizzes", json={
            "title": "Speed Quiz",
            "category_id": cat_id,
            "time_limit": 30,
        })
        assert r.status_code == 201
        quiz_id = r.json()["id"]

        # Добавляем один вопрос
        r = client.post(f"/quizzes/{quiz_id}/questions", json={
            "text": "Quick Q?",
            "options": ["Yes", "No"],
            "correct_index": 0,
        })
        assert r.status_code == 201
        q_id = r.json()["id"]

        # Начинаем попытку
        player_id = seed_data["players"]["bob"]
        r = client.post(f"/quizzes/{quiz_id}/start", json={"player_id": player_id})
        assert r.status_code == 201
        attempt_id = r.json()["attempt_id"]

        # Ждём чтобы время вышло
        time.sleep(31)

        # Submit после истечения time_limit -> 400
        answers = [{"question_id": q_id, "answer": 0}]
        r = client.post(f"/attempts/{attempt_id}/submit", json={"answers": answers})
        assert r.status_code == 400
        assert "time" in r.json().get("detail", "").lower() or "time" in str(r.json()).lower()


# ── Повторный Submit (5 баллов) ──────────────────────────────────────────────


class TestDoubleSubmit:
    """Повторный submit -> 409."""

    @pytest.mark.task(3)
    @pytest.mark.points(5)
    def test_double_submit(self, client, seed_data):
        quiz_id = seed_data["quizzes"]["Physics 101"]
        player_id = seed_data["players"]["alice"]
        question_ids = seed_data["questions"]["Physics 101"]

        # Начинаем попытку
        r = client.post(f"/quizzes/{quiz_id}/start", json={"player_id": player_id})
        assert r.status_code == 201
        attempt_id = r.json()["attempt_id"]

        answers = [
            {"question_id": question_ids[0], "answer": 1},
            {"question_id": question_ids[1], "answer": 0},
        ]

        # Первый submit OK
        r = client.post(f"/attempts/{attempt_id}/submit", json={"answers": answers})
        assert r.status_code == 200

        # Повторный submit -> 409
        r = client.post(f"/attempts/{attempt_id}/submit", json={"answers": answers})
        assert r.status_code == 409
