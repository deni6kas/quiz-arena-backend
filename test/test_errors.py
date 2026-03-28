"""
Тесты Задачи 6: Обработка ошибок (5 баллов).

Проверяют:
  - 404 для несуществующих сущностей
  - 409 для дубликатов (UNIQUE violation)
  - 400/404 для FK violation
  - Никогда не 500

НЕ ИЗМЕНЯЙТЕ ЭТОТ ФАЙЛ.
"""

import pytest


class TestNotFound:
    """404 для несуществующих сущностей."""

    @pytest.mark.task(6)
    @pytest.mark.points(1)
    def test_quiz_not_found(self, client):
        r = client.get("/quizzes/99999")
        assert r.status_code == 404

    @pytest.mark.task(6)
    @pytest.mark.points(1)
    def test_player_not_found(self, client):
        r = client.get("/players/99999")
        assert r.status_code == 404


class TestUniqueViolation:
    """409 для UNIQUE violation."""

    @pytest.mark.task(6)
    @pytest.mark.points(1)
    def test_category_duplicate_name(self, client):
        client.post("/categories", json={"name": "err_unique_cat"})
        r = client.post("/categories", json={"name": "err_unique_cat"})
        assert r.status_code == 409, (
            f"UNIQUE violation (category name) should return 409, got {r.status_code}"
        )

    @pytest.mark.task(6)
    @pytest.mark.points(1)
    def test_player_duplicate_nickname(self, client):
        client.post("/players", json={"nickname": "err_dup_nick", "email": "dup1@hse.ru"})
        r = client.post("/players", json={"nickname": "err_dup_nick", "email": "dup2@hse.ru"})
        assert r.status_code == 409, (
            f"UNIQUE violation (nickname) should return 409, got {r.status_code}"
        )


class TestForeignKeyViolation:
    """FK violation -> 400 или 404, но НЕ 500."""

    @pytest.mark.task(6)
    @pytest.mark.points(1)
    def test_quiz_invalid_category_fk(self, client):
        r = client.post("/quizzes", json={
            "title": "FK Test",
            "category_id": 99999,
            "time_limit": 60,
        })
        assert r.status_code in (400, 404), (
            f"FK violation should return 400 or 404, got {r.status_code}"
        )
