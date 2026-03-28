"""
Фикстуры и плагин подсчёта баллов для экзамена Quiz Arena.

НЕ ИЗМЕНЯЙТЕ ЭТОТ ФАЙЛ.

Тесты работают через HTTP (чёрный ящик):
  - Не импортируют модели/БД напрямую
  - Запускают uvicorn в subprocess
  - Используют httpx.Client для запросов
"""

import json
import os
import subprocess
import sys
import time

import httpx
import pytest

# ── Константы ───────────────────────────────────────────────────────────────

BASE_URL = "http://localhost:8000"
STARTUP_TIMEOUT = 15  # секунд на запуск сервера

TASK_NAMES = {
    1: "Models",
    2: "CRUD",
    3: "Game Mechanics",
    4: "External API Import",
    5: "Leaderboard & Stats",
    6: "Error Handling",
}

TASK_MAX_POINTS = {
    1: 15,
    2: 20,
    3: 25,
    4: 15,
    5: 15,
    6: 5,
}


# ── Маркеры ──────────────────────────────────────────────────────────────────

def pytest_configure(config):
    config.addinivalue_line("markers", "points(n): баллы за тест")
    config.addinivalue_line("markers", "task(n): номер задачи")
    config.addinivalue_line("markers", "slow: тесты с ожиданием (time.sleep)")


# ── Плагин подсчёта баллов ───────────────────────────────────────────────────

class ScoreBoard:
    def __init__(self):
        self.results = {}  # task_id -> {"earned": int, "max": int}

    def record(self, task_id, points, passed):
        if task_id not in self.results:
            self.results[task_id] = {"earned": 0, "max": 0}
        self.results[task_id]["max"] += points
        if passed:
            self.results[task_id]["earned"] += points


_scoreboard = ScoreBoard()


def pytest_runtest_makereport(item, call):
    """Записать результат каждого теста."""
    if call.when != "call":
        return

    task_marker = item.get_closest_marker("task")
    points_marker = item.get_closest_marker("points")

    if task_marker is None or points_marker is None:
        return

    task_id = task_marker.args[0]
    points = points_marker.args[0]
    passed = call.excinfo is None

    _scoreboard.record(task_id, points, passed)


def pytest_sessionfinish(session, exitstatus):
    """Печатаем таблицу результатов и сохраняем results.json."""
    results = _scoreboard.results
    if not results:
        return

    # Проверяем ruff (линтер)
    lint_score = 0
    lint_max = 5
    try:
        ret = subprocess.run(
            [sys.executable, "-m", "ruff", "check", "solution", "--no-cache"],
            capture_output=True,
            timeout=30,
        )
        if ret.returncode == 0:
            lint_score = 5
    except Exception:
        pass

    # Таблица
    width = 52
    print()
    print("=" * width)
    print(f"{'EXAM RESULTS':^{width}}")
    print("=" * width)

    total_earned = 0
    total_max = 0

    for task_id in sorted(TASK_NAMES.keys()):
        name = TASK_NAMES[task_id]
        if task_id in results:
            earned = results[task_id]["earned"]
            max_pts = TASK_MAX_POINTS[task_id]
        else:
            earned = 0
            max_pts = TASK_MAX_POINTS[task_id]

        total_earned += earned
        total_max += max_pts

        label = f"  Task {task_id}: {name}"
        score_str = f"{earned:>3} / {max_pts:<3}"
        padding = width - len(label) - len(score_str) - 2
        print(f"{label}{'.' * max(padding, 1)}{score_str}  ")

    # Линтер
    label = "  Lint (ruff)"
    score_str = f"{lint_score:>3} / {lint_max:<3}"
    padding = width - len(label) - len(score_str) - 2
    print(f"{label}{'.' * max(padding, 1)}{score_str}  ")
    total_earned += lint_score
    total_max += lint_max

    print("-" * width)
    label = "  TOTAL"
    score_str = f"{total_earned:>3} / {total_max:<3}"
    padding = width - len(label) - len(score_str) - 2
    print(f"{label}{'.' * max(padding, 1)}{score_str}  ")
    print("=" * width)
    print()

    # Сохраняем results.json
    json_results = {
        "tasks": {},
        "lint": {"earned": lint_score, "max": lint_max},
        "total": {"earned": total_earned, "max": total_max},
    }
    for task_id in sorted(TASK_NAMES.keys()):
        if task_id in results:
            json_results["tasks"][f"task_{task_id}"] = {
                "name": TASK_NAMES[task_id],
                "earned": results[task_id]["earned"],
                "max": TASK_MAX_POINTS[task_id],
            }
        else:
            json_results["tasks"][f"task_{task_id}"] = {
                "name": TASK_NAMES[task_id],
                "earned": 0,
                "max": TASK_MAX_POINTS[task_id],
            }

    with open("results.json", "w") as f:
        json.dump(json_results, f, indent=2, ensure_ascii=False)


# ── Сброс БД ────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session", autouse=True)
def _reset_db():
    """Сбрасывает БД перед прогоном безопасно перезапускать тесты."""
    import sqlalchemy
    url = os.getenv("DATABASE_URL", "postgresql+psycopg2:///quiz_arena")
    eng = sqlalchemy.create_engine(url)
    with eng.connect() as conn:
        conn.execute(sqlalchemy.text(
            "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
        ))
        conn.commit()
    eng.dispose()


# ── Сервер ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session", autouse=True)
def server(_reset_db):
    """Запускает uvicorn перед тестами, останавливает после."""
    env = {**os.environ}

    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "solution.main:app",
         "--host", "0.0.0.0", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )

    # Ждём, пока сервер ответит
    deadline = time.time() + STARTUP_TIMEOUT
    while time.time() < deadline:
        try:
            r = httpx.get(f"{BASE_URL}/categories", timeout=1)
            if r.status_code in (200, 404, 405, 422, 501):
                break
        except httpx.ConnectError:
            time.sleep(0.3)
    else:
        proc.terminate()
        out, err = proc.communicate(timeout=5)
        pytest.fail(
            f"Server did not start within {STARTUP_TIMEOUT}s.\n"
            f"stdout: {out.decode()}\nstderr: {err.decode()}"
        )

    yield proc

    proc.terminate()
    proc.wait(timeout=5)


@pytest.fixture(scope="session")
def client():
    """Sync HTTP-клиент для тестов."""
    with httpx.Client(base_url=BASE_URL, timeout=10) as c:
        yield c


# ── Seed Data ────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def seed_data(client):
    """Создаёт базовые данные для тестов. Вызывается один раз.

    Создаёт:
      - 2 категории: "Python", "Science"
      - 2 квиза: "Python Basics" (time_limit=300), "Physics 101" (time_limit=60)
      - 3 вопроса к "Python Basics"
      - 2 вопроса к "Physics 101"
      - 2 игрока: alice, bob
    """
    # Категории
    categories = {}
    for name in ("Python", "Science"):
        r = client.post("/categories", json={"name": name})
        assert r.status_code == 201, f"POST /categories failed: {r.text}"
        categories[name] = r.json()["id"]

    # Квизы
    quizzes = {}
    r = client.post("/quizzes", json={
        "title": "Python Basics",
        "category_id": categories["Python"],
        "time_limit": 300,
    })
    assert r.status_code == 201, f"POST /quizzes failed: {r.text}"
    quizzes["Python Basics"] = r.json()["id"]

    r = client.post("/quizzes", json={
        "title": "Physics 101",
        "category_id": categories["Science"],
        "time_limit": 60,
    })
    assert r.status_code == 201, f"POST /quizzes failed: {r.text}"
    quizzes["Physics 101"] = r.json()["id"]

    # Вопросы для Python Basics
    questions = {}
    python_questions = [
        {
            "text": "What does len([1, 2, 3]) return?",
            "options": ["1", "2", "3", "4"],
            "correct_index": 2,
        },
        {
            "text": "Which keyword defines a function in Python?",
            "options": ["func", "def", "function", "define"],
            "correct_index": 1,
        },
        {
            "text": "What is 2 ** 3?",
            "options": ["6", "8", "9", "5"],
            "correct_index": 1,
        },
    ]
    quiz_id = quizzes["Python Basics"]
    questions["Python Basics"] = []
    for q in python_questions:
        r = client.post(f"/quizzes/{quiz_id}/questions", json=q)
        assert r.status_code == 201, f"POST /quizzes/{quiz_id}/questions failed: {r.text}"
        questions["Python Basics"].append(r.json()["id"])

    # Вопросы для Physics 101
    physics_questions = [
        {
            "text": "What is the SI unit of force?",
            "options": ["Joule", "Newton", "Watt", "Pascal"],
            "correct_index": 1,
        },
        {
            "text": "What is the speed of light (approx)?",
            "options": ["300,000 km/s", "150,000 km/s", "1,000 km/s", "3,000 km/s"],
            "correct_index": 0,
        },
    ]
    quiz_id = quizzes["Physics 101"]
    questions["Physics 101"] = []
    for q in physics_questions:
        r = client.post(f"/quizzes/{quiz_id}/questions", json=q)
        assert r.status_code == 201, f"POST /quizzes/{quiz_id}/questions failed: {r.text}"
        questions["Physics 101"].append(r.json()["id"])

    # Игроки
    players = {}
    for nick, email in [("alice", "alice@hse.ru"), ("bob", "bob@hse.ru")]:
        r = client.post("/players", json={"nickname": nick, "email": email})
        assert r.status_code == 201, f"POST /players failed: {r.text}"
        players[nick] = r.json()["id"]

    return {
        "categories": categories,
        "quizzes": quizzes,
        "questions": questions,
        "players": players,
    }
