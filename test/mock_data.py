"""
Mock-данные для тестов импорта из Open Trivia DB.

Реалистичный ответ от https://opentdb.com/api.php?amount=3&type=multiple
Используется в respx-моках для перехвата HTTP-запросов.

НЕ ИЗМЕНЯЙТЕ ЭТОТ ФАЙЛ.
"""

MOCK_TRIVIA_RESPONSE = {
    "response_code": 0,
    "results": [
        {
            "type": "multiple",
            "difficulty": "medium",
            "category": "Science: Computers",
            "question": "What does CPU stand for?",
            "correct_answer": "Central Processing Unit",
            "incorrect_answers": [
                "Central Process Unit",
                "Computer Personal Unit",
                "Central Processor Unit",
            ],
        },
        {
            "type": "multiple",
            "difficulty": "easy",
            "category": "Science: Computers",
            "question": "What does HTML stand for?",
            "correct_answer": "HyperText Markup Language",
            "incorrect_answers": [
                "Hyper Tool Multi Language",
                "HyperText Multi Language",
                "HyperText Markup Level",
            ],
        },
        {
            "type": "multiple",
            "difficulty": "hard",
            "category": "Science: Computers",
            "question": "Which programming language was developed by Guido van Rossum?",
            "correct_answer": "Python",
            "incorrect_answers": [
                "Java",
                "C++",
                "Ruby",
            ],
        },
    ],
}

MOCK_TRIVIA_RESPONSE_ERROR = {
    "response_code": 1,
    "results": [],
}
