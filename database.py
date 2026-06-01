"""
Инициализация и работа с SQLite базой данных
"""

import sqlite3
import os

DB_PATH = 'scientific.db'

def get_connection():
    """Возвращает соединение с БД"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Чтобы можно было обращаться по именам колонок
    return conn

def init_db():
    """Создаёт таблицы, если их нет"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Таблица событий (изобретения и учёные)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            title TEXT NOT NULL,
            inventor TEXT,
            year TEXT,
            description TEXT
        )
    ''')
    
    # Таблица викторин
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quizzes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            question TEXT NOT NULL,
            correct TEXT NOT NULL,
            option2 TEXT,
            option3 TEXT,
            option4 TEXT
        )
    ''')
    
    # Таблица пользователей (статистика)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            correct_answers INTEGER DEFAULT 0,
            total_answers INTEGER DEFAULT 0,
            last_active TEXT,
            registered_at TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ База данных инициализирована")

def add_sample_data():
    """Добавляет тестовые данные (если таблицы пустые)"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Проверяем, есть ли события
    cursor.execute("SELECT COUNT(*) FROM events")
    events_count = cursor.fetchone()[0]
    
    if events_count == 0:
        # Добавляем тестовые события
        sample_events = [
            ("14.03", "Телефон", "Александр Белл", "1876", "Первый телефонный звонок состоялся 10 марта 1876 года."),
            ("15.03", "Радио", "Александр Попов", "1895", "Первый в мире радиоприёмник."),
            ("16.03", "Лампочка", "Томас Эдисон", "1879", "Первая коммерчески успешная лампа накаливания."),
        ]
        cursor.executemany('''
            INSERT INTO events (date, title, inventor, year, description)
            VALUES (?, ?, ?, ?, ?)
        ''', sample_events)
        print("✅ Добавлены тестовые события")
    
    # Проверяем, есть ли викторины
    cursor.execute("SELECT COUNT(*) FROM quizzes")
    quizzes_count = cursor.fetchone()[0]
    
    if quizzes_count == 0:
        # Добавляем тестовые вопросы
        sample_quizzes = [
            ("14.03", "Кто изобрёл телефон?", "Александр Белл", "Александр Попов", "Томас Эдисон", "Никола Тесла"),
            ("15.03", "Кто изобрёл радио?", "Александр Попов", "Гульельмо Маркони", "Никола Тесла", "Томас Эдисон"),
        ]
        cursor.executemany('''
            INSERT INTO qu izzes (date, question, correct, option2, option3, option4)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', sample_quizzes)
        print("✅ Добавлены тестовые вопросы")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    add_sample_data()
    print("🎉 База данных готова к работе!")