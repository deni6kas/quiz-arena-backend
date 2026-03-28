"""
Тесты Задачи 5: Лидерборд и статистика (15 баллов).

Проверяют:
  - GET /quizzes/{id}/leaderboard сортировка по score DESC, при равенстве по времени ASC
  - GET /players/{id}/stats total_attempts, avg_score_percent, best_quiz

НЕ ИЗМЕНЯЙТЕ ЭТОТ ФАЙЛ.
"""

import time

import pytest

# ── Leaderboard (7 баллов) ───────────────────────────────────────────────────


class TestLeaderboard:
    """GET /quizzes/{id}/leaderboard."""

    @pytest.fixture(scope="class")
    def leaderboard_data(self, client, seed_data):
        """Создаём квиз и несколько завершённых попыток для лидерборда."""
        cat_id = seed_data["categories"]["Python"]

        # Создаём квиз
        r = client.post("/quizzes", json={
            "title": "Leaderboard Quiz",
            "category_id": cat_id,
            "time_limit": 300,
        })
        assert r.status_code == 201
        quiz_id = r.json()["id"]

        # Добавляем 2 вопроса
        q_ids = []
        for text in ["LB Q1?", "LB Q2?"]:
            r = client.post(f"/quizzes/{quiz_id}/questions", json={
                "text": text,
                "options": ["A", "B", "C"],
                "correct_index": 0,
            })
            assert r.status_code == 201
            q_ids.append(r.json()["id"])

        # Создаём 3 игрока
        players = {}
        for nick, email in [
            ("lb_player1", "lb1@hse.ru"),
            ("lb_player2", "lb2@hse.ru"),
            ("lb_player3", "lb3@hse.ru"),
        ]:
            r = client.post("/players", json={"nickname": nick, "email": email})
            assert r.status_code == 201
            players[nick] = r.json()["id"]

        # Попытки:
        # lb_player1: 2/2 (лучший по score)
        # lb_player2: 1/2
        # lb_player3: 2/2 но позже (проигрывает по времени)

        # player1: все правильные
        r = client.post(f"/quizzes/{quiz_id}/start", json={"player_id": players["lb_player1"]})
        assert r.status_code == 201
        a1 = r.json()["attempt_id"]
        r = client.post(f"/attempts/{a1}/submit", json={
            "answers": [
                {"question_id": q_ids[0], "answer": 0},
                {"question_id": q_ids[1], "answer": 0},
            ]
        })
        assert r.status_code == 200

        # player2: 1 правильный
        r = client.post(f"/quizzes/{quiz_id}/start", json={"player_id": players["lb_player2"]})
        assert r.status_code == 201
        a2 = r.json()["attempt_id"]
        r = client.post(f"/attempts/{a2}/submit", json={
            "answers": [
                {"question_id": q_ids[0], "answer": 0},  # correct
                {"question_id": q_ids[1], "answer": 1},  # wrong
            ]
        })
        assert r.status_code == 200

        # player3: все правильные, но с задержкой -> time_seconds больше
        time.sleep(1)
        r = client.post(f"/quizzes/{quiz_id}/start", json={"player_id": players["lb_player3"]})
        assert r.status_code == 201
        a3 = r.json()["attempt_id"]
        time.sleep(1)
        r = client.post(f"/attempts/{a3}/submit", json={
            "answers": [
                {"question_id": q_ids[0], "answer": 0},
                {"question_id": q_ids[1], "answer": 0},
            ]
        })
        assert r.status_code == 200

        return {
            "quiz_id": quiz_id,
            "players": players,
            "question_ids": q_ids,
        }

    @pytest.mark.task(5)
    @pytest.mark.points(3)
    def test_leaderboard_sorted_by_score(self, client, leaderboard_data):
        """Лидерборд отсортирован по score DESC."""
        quiz_id = leaderboard_data["quiz_id"]
        r = client.get(f"/quizzes/{quiz_id}/leaderboard")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) >= 3

        # Score должен быть отсортирован по убыванию
        scores = [entry["score"] for entry in data]
        assert scores == sorted(scores, reverse=True)

        # Первые два должны иметь score=2, третий score=1
        assert data[0]["score"] == 2
        assert data[-1]["score"] == 1

    @pytest.mark.task(5)
    @pytest.mark.points(3)
    def test_leaderboard_tiebreaker_by_time(self, client, leaderboard_data):
        """При равном score сортировка по time_seconds ASC."""
        quiz_id = leaderboard_data["quiz_id"]
        r = client.get(f"/quizzes/{quiz_id}/leaderboard")
        assert r.status_code == 200
        data = r.json()

        # Среди записей с score=2, первый должен иметь меньше time_seconds
        top_entries = [e for e in data if e["score"] == 2]
        assert len(top_entries) == 2

        assert "time_seconds" in top_entries[0]
        assert "time_seconds" in top_entries[1]
        assert top_entries[0]["time_seconds"] <= top_entries[1]["time_seconds"]

        # player1 прошёл быстрее
        assert top_entries[0]["nickname"] == "lb_player1"
        assert top_entries[1]["nickname"] == "lb_player3"

    @pytest.mark.task(5)
    @pytest.mark.points(1)
    def test_leaderboard_limit(self, client, leaderboard_data):
        """GET /quizzes/{id}/leaderboard?limit=1 -> только одна запись."""
        quiz_id = leaderboard_data["quiz_id"]
        r = client.get(f"/quizzes/{quiz_id}/leaderboard", params={"limit": 1})
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 1


# ── Player Stats (8 баллов) ──────────────────────────────────────────────────


class TestPlayerStats:
    """GET /players/{id}/stats."""

    @pytest.fixture(scope="class")
    def stats_data(self, client, seed_data):
        """Создаём данные для статистики: игрок с несколькими попытками."""
        cat_id = seed_data["categories"]["Python"]

        # Создаём 2 квиза
        quizzes = {}
        for title, tl in [("Stats Quiz 1", 300), ("Stats Quiz 2", 300)]:
            r = client.post("/quizzes", json={
                "title": title,
                "category_id": cat_id,
                "time_limit": tl,
            })
            assert r.status_code == 201
            quizzes[title] = r.json()["id"]

        # Вопросы для Stats Quiz 1 (2 вопроса)
        q1_ids = []
        for text in ["SQ1 Q1?", "SQ1 Q2?"]:
            r = client.post(f"/quizzes/{quizzes['Stats Quiz 1']}/questions", json={
                "text": text,
                "options": ["A", "B"],
                "correct_index": 0,
            })
            assert r.status_code == 201
            q1_ids.append(r.json()["id"])

        # Вопросы для Stats Quiz 2 (2 вопроса)
        q2_ids = []
        for text in ["SQ2 Q1?", "SQ2 Q2?"]:
            r = client.post(f"/quizzes/{quizzes['Stats Quiz 2']}/questions", json={
                "text": text,
                "options": ["X", "Y"],
                "correct_index": 1,
            })
            assert r.status_code == 201
            q2_ids.append(r.json()["id"])

        # Создаём игрока
        r = client.post("/players", json={
            "nickname": "stats_player",
            "email": "stats@hse.ru",
        })
        assert r.status_code == 201
        player_id = r.json()["id"]

        # Попытка 1: Stats Quiz 1 2/2 = 100%
        r = client.post(f"/quizzes/{quizzes['Stats Quiz 1']}/start", json={"player_id": player_id})
        assert r.status_code == 201
        a1 = r.json()["attempt_id"]
        r = client.post(f"/attempts/{a1}/submit", json={
            "answers": [
                {"question_id": q1_ids[0], "answer": 0},
                {"question_id": q1_ids[1], "answer": 0},
            ]
        })
        assert r.status_code == 200
        assert r.json()["score"] == 2

        # Попытка 2: Stats Quiz 2 1/2 = 50%
        r = client.post(f"/quizzes/{quizzes['Stats Quiz 2']}/start", json={"player_id": player_id})
        assert r.status_code == 201
        a2 = r.json()["attempt_id"]
        r = client.post(f"/attempts/{a2}/submit", json={
            "answers": [
                {"question_id": q2_ids[0], "answer": 1},  # correct
                {"question_id": q2_ids[1], "answer": 0},  # wrong
            ]
        })
        assert r.status_code == 200
        assert r.json()["score"] == 1

        return {
            "player_id": player_id,
            "quizzes": quizzes,
        }

    @pytest.mark.task(5)
    @pytest.mark.points(3)
    def test_stats_total_attempts(self, client, stats_data):
        """total_attempts = количество завершённых попыток."""
        player_id = stats_data["player_id"]
        r = client.get(f"/players/{player_id}/stats")
        assert r.status_code == 200
        data = r.json()
        assert "total_attempts" in data
        assert data["total_attempts"] == 2
        assert "player" in data
        assert data["player"]["nickname"] == "stats_player"

    @pytest.mark.task(5)
    @pytest.mark.points(3)
    def test_stats_avg_score(self, client, stats_data):
        """avg_score_percent = среднее от (score/max_score * 100)."""
        player_id = stats_data["player_id"]
        r = client.get(f"/players/{player_id}/stats")
        assert r.status_code == 200
        data = r.json()
        assert "avg_score_percent" in data
        # (100% + 50%) / 2 = 75%
        assert data["avg_score_percent"] == pytest.approx(75.0, abs=1.0)

    @pytest.mark.task(5)
    @pytest.mark.points(2)
    def test_stats_best_quiz(self, client, stats_data):
        """best_quiz = квиз с лучшим процентом."""
        player_id = stats_data["player_id"]
        r = client.get(f"/players/{player_id}/stats")
        assert r.status_code == 200
        data = r.json()
        assert "best_quiz" in data
        best = data["best_quiz"]
        assert best is not None
        assert best["quiz_title"] == "Stats Quiz 1"
        assert best["score"] == 2
        assert best["max_score"] == 2
        assert best["percent"] == pytest.approx(100.0, abs=0.1)
