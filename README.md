# Экзамен: Quiz Arena (платформа онлайн-квизов)

### Как сдавать решение?

1. Склонировать репозиторий

2. Создать виртуальное окружение и установить зависимости:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Сделать ветку `dev`: `git checkout -b dev`. Решать задание нужно в этой ветке. Все файлы для редактирования находятся в папке `solution`.

4. Как только вы готовы отправить решение откройте Pull Request в ветку `main` и добавьте преподавателя в Reviewers. Название PR: `Exam. Фамилия Имя`.


### Подготовка PostgreSQL

Вам нужна работающая PostgreSQL и база `quiz_arena`.

#### macOS

```bash
# 1. Установить и запустить (если еще не сделали на практике)
brew install postgresql@16
brew services start postgresql@16

# Создать суперпользователя с вашим логином (если еще нет)
createuser -s $(whoami) 2>/dev/null || true

# 2. Создать базу данных
createdb quiz_arena

# 3. Проверить, что все работает
psql -d quiz_arena -c "SELECT version();"
```

После этого в `solution/database.py` строка подключения без пароля:
```
postgresql+psycopg2:///quiz_arena
```

#### Linux / Windows (WSL)

```bash
# 1. Установить и запустить (если еще не сделали на практике)
sudo apt update && sudo apt install -y postgresql postgresql-contrib
sudo systemctl enable --now postgresql

# Создать суперпользователя с вашим логином (если еще нет)
sudo -u postgres createuser -s $USER 2>/dev/null || true

# 2. Создать базу данных
createdb quiz_arena

# 3. Проверить, что все работает
psql -d quiz_arena -c "SELECT version();"
```

> **Если `createdb` / `psql` не работает без `-U postgres`**, значит суперпользователь не создался. Тогда используйте:
> ```bash
> sudo -u postgres createdb quiz_arena
> ```
> и в `database.py`:
> ```
> postgresql+psycopg2://postgres:postgres@localhost:5432/quiz_arena
> ```


### Как запустить сервер и тесты

**Запустить тесты** (сервер поднимается автоматически внутри pytest, запускать вручную не нужно):

```bash
make test
# или
pytest test -s

# Быстрый запуск (без тестов с ожиданием ~30 сек):
make test-fast
```

> **Важно:** Не запускайте `uvicorn` вручную перед тестами - pytest сам поднимает сервер на порту 8000. Если порт занят, тесты упадут.

> **Внимание:** Тесты полностью очищают все таблицы в базе `quiz_arena` при каждом запуске. Не указывайте `DATABASE_URL` на важную или общую базу данных.

**Запустить сервер для ручной отладки** (через браузер, Postman, curl):

```bash
make run
# или
uvicorn solution.main:app --reload
```

**Линтер и форматтер:**

```bash
make fmt lint
```

> **CI:** В GitHub Actions PostgreSQL поднимается автоматически. Менять ничего не нужно просто открывайте PR и смотрите результат.

> **Требования:** Python 3.12+, PostgreSQL 16.


---


## Seed-данные (обязательный этап)

Перед тем как приступить к заданию, получите свои уникальные тестовые данные с сервера экзамена.

**Шаг 1.** Зарегистрируйтесь (укажите свой GitHub username и номер аудитории):

```bash
curl "http://158.160.200.187.nip.io:8080/register?github=ВАШ_GITHUB&room=НОМЕР_АУДИТОРИИ"
```

Аудитории: `331`, `332`, `333`, `334`, `335`, `338`

Пример:
```bash
curl "http://158.160.200.187.nip.io:8080/register?github=ivanov&room=331"
# → {"github": "ivanov", "room": "331", "token": "a1b2c3d4e5f6g7h8"}
```

**Шаг 2.** Получите seed-данные по токену и сохраните в файл:

```bash
curl "http://158.160.200.187.nip.io:8080/seed?token=ВАШ_ТОКЕН" -o solution/seed_data.json
```

**Шаг 3.** Проверьте, что файл на месте:

```bash
cat solution/seed_data.json | python3 -m json.tool | head -10
```

> Вы можете использовать любой способ: `curl`, браузер, `python3 -c "import requests; ..."` — результат одинаковый.

> Дашборд экзамена: http://158.160.200.187.nip.io:8080/dashboard

---


## Задание

Вы бэкенд-разработчик в EdTech-стартапе. Ваша задача: построить серверную часть платформы для онлайн-квизов. Пользователи создают квизы с вопросами, другие игроки проходят их, а система считает результаты и ведёт таблицу лидеров.


### Что реализовать

Все файлы находятся в `solution/`:

| Файл | Что нужно сделать |
|------|------------------|
| `models.py` | Описать SQLAlchemy-модели: Category, Quiz, Question, Player, Attempt |
| `schemas.py` | Описать Pydantic-схемы для валидации запросов и ответов |
| `main.py` | Реализовать FastAPI-эндпоинты (список ниже) |
| `database.py` | Готов к использованию, можно менять при необходимости |

**НЕ ИЗМЕНЯЙТЕ** папку `test/` и файл `.github/workflows/ci.yml`.


### Структура проекта

```
omp_exam_quiz_arena/
├── solution/
│   ├── __init__.py
│   ├── database.py      # Подключение к БД (готов, менять не обязательно)
│   ├── models.py        # ← Задача 1: SQLAlchemy-модели
│   ├── schemas.py       # ← Задача 1: Pydantic-схемы
│   └── main.py          # ← Задачи 2–6: FastAPI-эндпоинты
├── test/                # Тесты (НЕ ИЗМЕНЯТЬ)
├── .github/workflows/   # CI (НЕ ИЗМЕНЯТЬ)
├── Makefile
├── pyproject.toml
├── requirements.txt
└── README.md
```


### Схема БД

```
categories
├── id          SERIAL PRIMARY KEY
└── name        VARCHAR UNIQUE NOT NULL

quizzes
├── id          SERIAL PRIMARY KEY
├── title       VARCHAR NOT NULL
├── category_id INTEGER FK -> categories (NOT NULL)
├── time_limit  INTEGER NOT NULL (секунды, >= 30)
└── created_at  TIMESTAMP DEFAULT now()

questions
├── id              SERIAL PRIMARY KEY
├── quiz_id         INTEGER FK -> quizzes ON DELETE CASCADE
├── text            VARCHAR NOT NULL
├── options         JSON NOT NULL (список из 2–6 строк)
└── correct_index   INTEGER NOT NULL (>= 0)

players
├── id        SERIAL PRIMARY KEY
├── nickname  VARCHAR UNIQUE NOT NULL
└── email     VARCHAR UNIQUE NOT NULL

attempts
├── id          SERIAL PRIMARY KEY
├── player_id   INTEGER FK -> players (NOT NULL)
├── quiz_id     INTEGER FK -> quizzes ON DELETE CASCADE
├── score       INTEGER (NULL пока не завершена)
├── max_score   INTEGER (NULL пока не завершена)
├── started_at  TIMESTAMP NOT NULL DEFAULT now()
└── finished_at TIMESTAMP (NULL пока не завершена)
```

Связи:
```
categories  1 ── * quizzes
quizzes     1 ── * questions
quizzes     1 ── * attempts
players     1 ── * attempts
```


### Эндпоинты

#### Categories

| Метод | URL | Код | Описание |
|-------|-----|-----|----------|
| POST | `/categories` | 201 | Создать категорию `{"name": "..."}` |
| GET | `/categories` | 200 | Список всех категорий |

#### Quizzes

| Метод | URL | Код | Описание |
|-------|-----|-----|----------|
| POST | `/quizzes` | 201 | Создать квиз `{"title", "category_id", "time_limit"}` |
| GET | `/quizzes` | 200 | Список квизов. Query: `category_id` (опционально) |
| GET | `/quizzes/{id}` | 200 | Один квиз (+ `questions_count` кол-во вопросов) |
| DELETE | `/quizzes/{id}` | 204 | Удалить квиз (каскадно удаляет вопросы и попытки) |

#### Questions

| Метод | URL | Код | Описание |
|-------|-----|-----|----------|
| POST | `/quizzes/{id}/questions` | 201 | Добавить вопрос к квизу |
| GET | `/quizzes/{id}/questions` | 200 | Список вопросов квиза (**без** `correct_index` не раскрываем ответы!) |

#### Players

| Метод | URL | Код | Описание |
|-------|-----|-----|----------|
| POST | `/players` | 201 | Зарегистрировать игрока `{"nickname", "email"}` |
| GET | `/players/{id}` | 200 | Профиль игрока |

#### Game Flow (попытки)

| Метод | URL | Код | Описание |
|-------|-----|-----|----------|
| POST | `/quizzes/{id}/start` | 201 | Начать попытку. Body: `{"player_id"}`. Возвращает `attempt_id`, `started_at`, `time_limit` |
| POST | `/attempts/{id}/submit` | 200 | Отправить ответы. Body: `{"answers": [{"question_id": N, "answer": M}, ...]}`. Возвращает `score`, `max_score`, `percent`, `finished_at` |

> **Важно:** Один игрок может проходить один и тот же квиз несколько раз. Повторные попытки разрешены (не добавляйте UNIQUE на пару `player_id + quiz_id`).

#### Leaderboard и статистика

| Метод | URL | Код | Описание |
|-------|-----|-----|----------|
| GET | `/quizzes/{id}/leaderboard` | 200 | Топ игроков по `score` (при равенстве по времени). Query: `limit` (default 10) |
| GET | `/players/{id}/stats` | 200 | Статистика: `total_attempts`, `avg_score_percent`, `best_quiz` |

**Формат leaderboard entry:**
- `nickname` - никнейм игрока
- `score` - количество правильных ответов
- `max_score` - количество вопросов в квизе
- `time_seconds` - время прохождения в секундах (`finished_at - started_at`), тип `float`
- Только завершённые попытки (`finished_at IS NOT NULL`)

#### Импорт вопросов (внешний API)

| Метод | URL | Код | Описание |
|-------|-----|-----|----------|
| POST | `/quizzes/{id}/import` | 201 | Импортировать вопросы из Open Trivia DB. Body: `{"amount": N}` |


---


## Задачи и баллы

### Задача 1. Модели (15 баллов)

**Файлы:** `solution/models.py`, `solution/schemas.py`

Реализовать:
- SQLAlchemy-модели: `Category`, `Quiz`, `Question`, `Player`, `Attempt`
- Pydantic-схемы для request/response каждого эндпоинта
- Валидация: `time_limit >= 30`, `correct_index >= 0`, `options` - список из 2-6 элементов
- `name` - непустая строка (для категорий)

### Задача 2. CRUD-эндпоинты (20 баллов)

**Файл:** `solution/main.py`

| Группа | Баллов |
|--------|--------|
| Categories: POST + GET | 3 |
| Quizzes: POST + GET list + GET one + DELETE | 7 |
| Questions: POST + GET (без correct_index!) | 5 |
| Players: POST + GET | 3 |
| Фильтрация `GET /quizzes?category_id=...` | 2 |

### Задача 3. Игровая механика (25 баллов)

| Что проверяется | Баллов |
|-----------------|--------|
| `POST /quizzes/{id}/start` - создание попытки | 5 |
| `POST /attempts/{id}/submit` - подсчёт очков | 10 |
| Проверка time_limit: если `now() - started_at > time_limit` -> 400 `"Time is up"` | 5 |
| Защита от повторного submit (если `finished_at` уже заполнен - 409) | 5 |

**Логика submit:**
```
Для каждого ответа в answers:
  - Найти вопрос по question_id (должен принадлежать квизу попытки)
  - Сравнить answer с correct_index
  - Если совпадает -> +1 к score
Записать score, max_score = кол-во вопросов, finished_at = now()
```

### Задача 4. Импорт из внешнего API (15 баллов)

Реализовать `POST /quizzes/{id}/import`:

1. Принять `{"amount": N}` (1 <= N <= 20)
2. Отправить GET-запрос к `https://opentdb.com/api.php?amount=N&type=multiple`
3. Трансформировать ответ: из `incorrect_answers` + `correct_answer` собрать `options` (перемешать!), вычислить `correct_index`
4. Сохранить вопросы в БД, привязать к квизу
5. Вернуть список созданных вопросов

| Что проверяется | Баллов |
|-----------------|--------|
| Успешный импорт (мок через respx) | 7 |
| Трансформация формата (options + correct_index) | 5 |
| Ошибка внешнего API -> 502 | 3 |

### Задача 5. Лидерборд и статистика (15 баллов)

| Что проверяется | Баллов |
|-----------------|--------|
| `GET /quizzes/{id}/leaderboard` - сортировка по score DESC, затем по времени ASC | 7 |
| `GET /players/{id}/stats` - `total_attempts`, `avg_score_percent`, `best_quiz` | 8 |

**Подробности stats:**
```json
{
  "player": {"id": 1, "nickname": "alice", "email": "alice@hse.ru"},
  "total_attempts": 5,
  "avg_score_percent": 72.5,
  "best_quiz": {
    "quiz_title": "Python Basics",
    "score": 9,
    "max_score": 10,
    "percent": 90.0
  }
}
```

`avg_score_percent` - среднее от `(score / max_score * 100)` по завершённым попыткам.

Если у игрока нет завершённых попыток: `total_attempts: 0`, `avg_score_percent: 0.0`, `best_quiz: null`.

### Задача 6. Обработка ошибок (5 баллов)

| Ситуация | HTTP-код |
|----------|----------|
| Невалидные данные (Pydantic) | 422 |
| Сущность не найдена | 404 |
| FK violation | 400 или 404 |
| UNIQUE violation | 409 |
| Повторный submit | 409 |
| Время вышло | 400 |
| Ошибка внешнего API | 502 |
| **Сервер никогда не возвращает 500** | - |

### Линтер (5 баллов)

`ruff check solution/` - без ошибок.


### Итого

| Задача | Баллов |
|--------|--------|
| 1. Модели (SQLAlchemy + Pydantic) | 15 |
| 2. CRUD-эндпоинты | 20 |
| 3. Игровая механика (start + submit + timer) | 25 |
| 4. Импорт из внешнего API | 15 |
| 5. Лидерборд + статистика | 15 |
| 6. Обработка ошибок | 5 |
| Линтер (ruff) | 5 |
| **Итого** | **100** |

> **Рекомендуемый порядок:** 1 (модели) → 2 (CRUD) → 3 (игровая механика) → 4 (импорт) → 5 (статистика) → 6 (ошибки). Задачи 2–6 зависят от моделей, поэтому начните с задачи 1.

### С чего начать

1. Опишите модели в `solution/models.py` (Category, Quiz, Question, Player, Attempt)
2. Опишите Pydantic-схемы в `solution/schemas.py`
3. Раскомментируйте `Base.metadata.create_all(bind=engine)` в `solution/main.py`
4. Запустите `make test` - если модели верны, сервер поднимется и seed_data создастся
5. Реализуйте эндпоинты в `solution/main.py` один за другим, проверяя тестами

---


## Пример сценария прохождения

```bash
# 1. Создать категорию
POST /categories  {"name": "Python"}  -> 201, {"id": 1, "name": "Python"}

# 2. Создать квиз
POST /quizzes  {"title": "Python Basics", "category_id": 1, "time_limit": 300}
-> 201, {"id": 1, ...}

# 3. Добавить вопросы
POST /quizzes/1/questions  {
  "text": "Что вернёт len([1, 2, 3])?",
  "options": ["1", "2", "3", "4"],
  "correct_index": 2
}
-> 201

# 4. Зарегистрировать игрока
POST /players  {"nickname": "alice", "email": "alice@hse.ru"}  -> 201

# 5. Начать попытку
POST /quizzes/1/start  {"player_id": 1}
-> 201, {"attempt_id": 1, "started_at": "2026-03-25T10:00:00", "time_limit": 300}

# 6. Получить вопросы (correct_index НЕ возвращается!)
GET /quizzes/1/questions
-> 200, [{"id": 1, "text": "Что вернёт len(...)?", "options": [...]}]

# 7. Отправить ответы
POST /attempts/1/submit  {"answers": [{"question_id": 1, "answer": 2}]}
-> 200, {"score": 1, "max_score": 1, "percent": 100.0, "finished_at": "..."}

# 8. Посмотреть лидерборд
GET /quizzes/1/leaderboard
-> 200, [{"nickname": "alice", "score": 1, "max_score": 1, "time_seconds": 42}]
```


---


## Полезные ссылки

- [FastAPI - Query Parameters](https://fastapi.tiangolo.com/tutorial/query-params/)
- [FastAPI - Request Body](https://fastapi.tiangolo.com/tutorial/body/)
- [FastAPI - Handling Errors](https://fastapi.tiangolo.com/tutorial/handling-errors/)
- [SQLAlchemy ORM Quick Start](https://docs.sqlalchemy.org/en/20/orm/quickstart.html)
- [Pydantic v2 - Models](https://docs.pydantic.dev/latest/concepts/models/)
- [httpx - Async Client](https://www.python-httpx.org/async/)
- [Open Trivia DB API](https://opentdb.com/api_config.php)
