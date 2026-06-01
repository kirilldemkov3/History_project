"""
Вспомогательные функции для работы с SQLite базой данных
"""

import sqlite3
import datetime
import random
from database import get_connection, init_db

# Инициализируем БД при первом импорте
init_db()


# ========== ФУНКЦИИ ДЛЯ РАБОТЫ С СОБЫТИЯМИ ==========

def get_today_event():
    """
    Получает событие для сегодняшней даты
    """
    try:
        today_str = datetime.datetime.now().strftime("%d.%m")
        print(f"🔍 Ищем дату, начинающуюся с: {today_str}")
        
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT title, inventor, year, description, date
            FROM events 
            WHERE date LIKE ?
            LIMIT 1
        ''', (today_str + '%',))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            print(f"✅ Найдено совпадение: {row['date']}")
            return {
                "title": row["title"],
                "inventor": row["inventor"] if row["inventor"] else "Неизвестен",
                "year": str(row["year"]) if row["year"] else "?",
                "description": row["description"] if row["description"] else ""
            }
        
        print(f"⚠️ Запись для даты {today_str} не найдена")
        return None
        
    except Exception as e:
        print(f"❌ Ошибка в get_today_event: {e}")
        return None


def get_random_event():
    """
    Возвращает случайное событие из базы
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT title, inventor, year, description
            FROM events 
            ORDER BY RANDOM() 
            LIMIT 1
        ''')
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "title": row["title"],
                "inventor": row["inventor"] if row["inventor"] else "Неизвестен",
                "year": str(row["year"]) if row["year"] else "?",
                "description": row["description"] if row["description"] else ""
            }
        
        return {
            "title": "Нет данных",
            "inventor": "Неизвестен",
            "year": "?",
            "description": "Добавьте события в базу данных!"
        }
        
    except Exception as e:
        print(f"❌ Ошибка в get_random_event: {e}")
        return {
            "title": "Ошибка",
            "inventor": "Ошибка",
            "year": "?",
            "description": f"Ошибка доступа к базе: {e}"
        }


# ========== ФУНКЦИИ ДЛЯ ВИКТОРИНЫ ==========

def get_random_quiz():
    """
    Возвращает случайный вопрос из таблицы викторин
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, question, correct, option2, option3, option4
            FROM quizzes 
            ORDER BY RANDOM() 
            LIMIT 1
        ''')
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            print("⚠️ Вопросы не найдены")
            return None
        
        # Собираем варианты ответов
        options = [row["correct"]]
        if row["option2"]:
            options.append(row["option2"])
        if row["option3"]:
            options.append(row["option3"])
        if row["option4"]:
            options.append(row["option4"])
        
        random.shuffle(options)
        
        return {
            "id": row["id"],
            "question": row["question"],
            "options": options,
            "correct": row["correct"]
        }
        
    except Exception as e:
        print(f"❌ Ошибка в get_random_quiz: {e}")
        return None


def get_quiz_for_today():
    """
    Получает вопрос для викторины по сегодняшней дате
    """
    try:
        today_str = datetime.datetime.now().strftime("%d.%m")
        
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, question, correct, option2, option3, option4
            FROM quizzes 
            WHERE date LIKE ?
            LIMIT 1
        ''', (today_str + '%',))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        options = [row["correct"], row["option2"], row["option3"], row["option4"]]
        options = [opt for opt in options if opt]
        random.shuffle(options)
        
        return {
            "id": row["id"],
            "question": row["question"],
            "options": options,
            "correct": row["correct"]
        }
        
    except Exception as e:
        print(f"❌ Ошибка в get_quiz_for_today: {e}")
        return None


# ========== ФУНКЦИИ ДЛЯ СТАТИСТИКИ ПОЛЬЗОВАТЕЛЕЙ ==========

def get_user_stats(user_id: int, username: str = None, first_name: str = None):
    """
    Получает статистику пользователя
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT username, first_name, correct_answers, total_answers
            FROM users 
            WHERE user_id = ?
        ''', (user_id,))
        
        row = cursor.fetchone()
        
        if row:
            correct = row["correct_answers"] or 0
            total = row["total_answers"] or 0
            
            stats = {
                "username": row["username"] if row["username"] else (username or "Гость"),
                "first_name": row["first_name"] if row["first_name"] else (first_name or ""),
                "correct": correct,
                "total": total,
                "accuracy": round(correct / total * 100, 1) if total > 0 else 0
            }
        else:
            # Новый пользователь
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute('''
                INSERT INTO users (user_id, username, first_name, correct_answers, total_answers, last_active, registered_at)
                VALUES (?, ?, ?, 0, 0, ?, ?)
            ''', (user_id, username or "", first_name or "", now, now))
            conn.commit()
            
            stats = {
                "username": username or "Гость",
                "first_name": first_name or "",
                "correct": 0,
                "total": 0,
                "accuracy": 0
            }
        
        conn.close()
        print(f"📊 Статистика для {user_id}: {stats}")
        return stats
        
    except Exception as e:
        print(f"❌ Ошибка в get_user_stats: {e}")
        return {
            "username": username or "Гость",
            "first_name": first_name or "",
            "correct": 0,
            "total": 0,
            "accuracy": 0
        }


def update_user_score(user_id: int, is_correct: bool, username: str = None, first_name: str = None):
    """
    Обновляет статистику пользователя после викторины
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Проверяем, существует ли пользователь
        cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        exists = cursor.fetchone()
        
        if exists:
            # Обновляем существующего
            if is_correct:
                cursor.execute('''
                    UPDATE users 
                    SET correct_answers = correct_answers + 1,
                        total_answers = total_answers + 1,
                        last_active = ?
                    WHERE user_id = ?
                ''', (now, user_id))
            else:
                cursor.execute('''
                    UPDATE users 
                    SET total_answers = total_answers + 1,
                        last_active = ?
                    WHERE user_id = ?
                ''', (now, user_id))
            
            # Обновляем имя, если оно пустое
            if username:
                cursor.execute('''
                    UPDATE users 
                    SET username = COALESCE(username, ?)
                    WHERE user_id = ? AND (username IS NULL OR username = '')
                ''', (username, user_id))
            if first_name:
                cursor.execute('''
                    UPDATE users 
                    SET first_name = COALESCE(first_name, ?)
                    WHERE user_id = ? AND (first_name IS NULL OR first_name = '')
                ''', (first_name, user_id))
        else:
            # Создаём нового пользователя
            cursor.execute('''
                INSERT INTO users (user_id, username, first_name, correct_answers, total_answers, last_active, registered_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                username or "",
                first_name or "",
                1 if is_correct else 0,
                1,
                now,
                now
            ))
        
        conn.commit()
        conn.close()
        print(f"✅ Статистика обновлена для {user_id}: +{'1' if is_correct else '0'} правильных")
        
    except Exception as e:
        print(f"❌ Ошибка в update_user_score: {e}")


def get_top_users(limit: int = 10):
    """
    Получает топ пользователей по правильным ответам
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT username, correct_answers as correct, total_answers as total
            FROM users 
            WHERE total_answers > 0
            ORDER BY correct_answers DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        result = []
        for row in rows:
            correct = row["correct"] or 0
            total = row["total"] or 0
            result.append({
                "username": row["username"] if row["username"] else "Аноним",
                "correct": correct,
                "total": total,
                "accuracy": round(correct / total * 100, 1) if total > 0 else 0
            })
        
        return result
        
    except Exception as e:
        print(f"❌ Ошибка в get_top_users: {e}")
        return []


def get_all_users():
    """
    Получает список всех user_id для рассылки
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT user_id FROM users")
        rows = cursor.fetchall()
        conn.close()
        
        return [row["user_id"] for row in rows]
        
    except Exception as e:
        print(f"❌ Ошибка в get_all_users: {e}")
        return []