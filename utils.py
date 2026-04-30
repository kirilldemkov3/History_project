"""
Вспомогательные функции для работы с Google Sheets
"""

import os
import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
import datetime
import random

# Загружаем переменные из .env
load_dotenv()

# ========== НАСТРОЙКИ ДОСТУПА ==========
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Путь к credentials.json (из .env)
CREDS_FILE = os.getenv("GOOGLE_CREDS_PATH", "credentials.json")

# Название таблицы (из .env)
SHEET_NAME = os.getenv("SPREADSHEET_NAME", "Научный календарь")

# ... остальные функции без изменений

# ========== ФУНКЦИЯ ПОДКЛЮЧЕНИЯ ==========

def get_client():
    """
    Создаёт и возвращает клиент для работы с Google Sheets
    """
    if not os.path.exists(CREDS_FILE):
        print(f"❌ Файл {CREDS_FILE} не найден в папке {os.getcwd()}")
        raise FileNotFoundError(f"Файл {CREDS_FILE} не найден")
    
    creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPE)
    client = gspread.authorize(creds)
    print("✅ Подключение к Google Sheets установлено")
    return client


# ========== ФУНКЦИИ ДЛЯ РАБОТЫ С СОБЫТИЯМИ ==========

def get_today_event():
    """
    Получает событие для сегодняшней даты из листа 'События'
    """
    try:
        # Получаем сегодняшний день и месяц
        today_str = datetime.datetime.now().strftime("%d.%m")
        print(f"🔍 Ищем дату, начинающуюся с: {today_str}")
        
        client = get_client()
        spreadsheet = client.open(SHEET_NAME)
        sheet = spreadsheet.worksheet("События")
        
        records = sheet.get_all_records()
        print(f"📊 Всего записей в 'События': {len(records)}")
        
        for record in records:
            date_str = str(record.get("Дата", ""))
            if date_str.startswith(today_str):
                print(f"✅ Найдено совпадение: {date_str}")
                
                # Извлекаем год, если есть
                year = record.get("Год", "")
                if not year:
                    parts = date_str.split('.')
                    if len(parts) >= 3:
                        year = parts[2]
                
                return {
                    "title": record.get("Изобретение", "Неизвестно"),
                    "inventor": record.get("Изобретатель", "Неизвестен"),
                    "year": str(year) if year else "?",
                    "description": record.get("Описание", "")
                }
        
        print(f"⚠️ Запись для даты {today_str} не найдена")
        return None  # Возвращаем None, если не нашли
        
    except Exception as e:
        print(f"❌ Ошибка в get_today_event: {e}")
        import traceback
        traceback.print_exc()
        return None


def get_random_event():
    """
    Возвращает случайное событие из листа 'События'
    """
    try:
        client = get_client()
        spreadsheet = client.open(SHEET_NAME)
        sheet = spreadsheet.worksheet("События")
        
        records = sheet.get_all_records()
        
        if not records:
            return {
                "title": "Нет данных",
                "inventor": "Неизвестен",
                "year": "?",
                "description": "Заполните базу знаний!"
            }
        
        event = random.choice(records)
        
        return {
            "title": event.get("Изобретение", "Неизвестно"),
            "inventor": event.get("Изобретатель", "Неизвестен"),
            "year": str(event.get("Год", "?")),
            "description": event.get("Описание", "")
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

def get_quiz_for_today():
    """
    Получает вопрос для викторины из листа 'Викторины'
    """
    try:
        today_str = datetime.datetime.now().strftime("%d.%m")
        
        client = get_client()
        spreadsheet = client.open(SHEET_NAME)
        sheet = spreadsheet.worksheet("Викторины")
        
        records = sheet.get_all_records()
        
        for record in records:
            date_str = str(record.get("Дата", ""))
            if date_str.startswith(today_str):
                options = [
                    record.get("Правильный ответ"),
                    record.get("Вариант 2"),
                    record.get("Вариант 3"),
                    record.get("Вариант 4")
                ]
                # Убираем пустые варианты
                options = [opt for opt in options if opt]
                random.shuffle(options)
                
                return {
                    "question": record.get("Вопрос"),
                    "options": options,
                    "correct": record.get("Правильный ответ"),
                    "id": record.get("ID", 1)
                }
        
        return None
        
    except Exception as e:
        print(f"❌ Ошибка в get_quiz_for_today: {e}")
        return None


# ========== ФУНКЦИИ ДЛЯ СТАТИСТИКИ ПОЛЬЗОВАТЕЛЕЙ ==========

def update_user_score(user_id: int, is_correct: bool, username: str = None, first_name: str = None):
    """
    Обновляет статистику пользователя после викторины
    """
    try:
        client = get_client()
        spreadsheet = client.open(SHEET_NAME)
        sheet = spreadsheet.worksheet("Пользователи")
        
        # Получаем все user_id из первой колонки
        user_ids = sheet.col_values(1)
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"📊 Обновление статистики для user_id: {user_id}")
        print(f"   Правильный ответ: {is_correct}")
        
        try:
            # Ищем пользователя
            row_index = user_ids.index(str(user_id)) + 1
            print(f"   Найден в строке {row_index}")
            
            # Читаем текущие значения
            row = sheet.row_values(row_index)
            print(f"   Текущие значения: {row}")
            
            # Убеждаемся, что в строке достаточно колонок
            while len(row) < 7:
                row.append("0")
            
            correct = int(row[3]) if row[3] and row[3].isdigit() else 0
            total = int(row[4]) if row[4] and row[4].isdigit() else 0
            
            # Обновляем
            if is_correct:
                correct += 1
            total += 1
            
            print(f"   Новые значения: correct={correct}, total={total}")
            
            # Обновляем username и first_name если они есть
            if username:
                sheet.update_cell(row_index, 2, username)  # колонка B = username
            if first_name:
                sheet.update_cell(row_index, 3, first_name)  # колонка C = first_name
            
            # Обновляем статистику
            sheet.update_cell(row_index, 4, correct)  # колонка D = correct_answers
            sheet.update_cell(row_index, 5, total)    # колонка E = total_answers
            sheet.update_cell(row_index, 6, now)      # колонка F = last_active
            
            print(f"✅ Статистика обновлена!")
            
        except ValueError as e:
            print(f"⚠️ Пользователь {user_id} не найден в таблице: {e}")
            # Создаём нового пользователя
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_row = [
                str(user_id),
                username or "",
                first_name or "",
                "1" if is_correct else "0",
                "1",
                now,
                now
            ]
            sheet.append_row(new_row)
            print(f"✅ Создан новый пользователь {user_id} с именем {username}")
            
    except Exception as e:
        print(f"❌ Ошибка в update_user_score: {e}")
        import traceback
        traceback.print_exc()


def get_user_stats(user_id: int, username: str = None, first_name: str = None):
    """
    Получает статистику пользователя из листа 'Пользователи'
    """
    try:
        client = get_client()
        spreadsheet = client.open(SHEET_NAME)
        
        try:
            sheet = spreadsheet.worksheet("Пользователи")
        except gspread.WorksheetNotFound:
            # Создаём лист, если его нет
            sheet = spreadsheet.add_worksheet(title="Пользователи", rows=1000, cols=7)
            sheet.append_row(['user_id', 'username', 'first_name', 'correct_answers', 'total_answers', 'last_active', 'registered_at'])
            print("✅ Создан новый лист 'Пользователи'")
        
        # Получаем все user_id
        user_ids = sheet.col_values(1)
        
        try:
            row_index = user_ids.index(str(user_id)) + 1
            row = sheet.row_values(row_index)
            
            # Убеждаемся, что в строке достаточно колонок
            while len(row) < 7:
                row.append("0")
            
            correct = int(row[3]) if row[3] and row[3].isdigit() else 0
            total = int(row[4]) if row[4] and row[4].isdigit() else 0
            
            # Если в таблице нет username, но он передан в функцию - обновляем
            current_username = row[1] if len(row) > 1 and row[1] else ""
            if not current_username and username:
                sheet.update_cell(row_index, 2, username)
                current_username = username
            
            current_first_name = row[2] if len(row) > 2 and row[2] else ""
            if not current_first_name and first_name:
                sheet.update_cell(row_index, 3, first_name)
                current_first_name = first_name
            
            stats = {
                "username": current_username if current_username else (username or "Гость"),
                "first_name": current_first_name,
                "correct": correct,
                "total": total,
                "accuracy": round(correct / total * 100, 1) if total > 0 else 0
            }
            print(f"📊 Статистика для {user_id}: {stats}")
            return stats
            
        except ValueError:
            # Новый пользователь — создаём запись
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_row = [
                str(user_id),
                username or "",
                first_name or "",
                "0",
                "0",
                now,
                now
            ]
            sheet.append_row(new_row)
            print(f"✅ Создана новая запись для пользователя {user_id} (username: {username})")
            
            return {
                "username": username or "Гость",
                "first_name": first_name or "",
                "correct": 0,
                "total": 0,
                "accuracy": 0
            }
            
    except Exception as e:
        print(f"❌ Ошибка в get_user_stats: {e}")
        import traceback
        traceback.print_exc()
        return {
            "username": username or "Гость",
            "first_name": first_name or "",
            "correct": 0,
            "total": 0,
            "accuracy": 0
        }
        
        
def get_top_users(limit: int = 10):
    
    
    """
    Получает топ пользователей по правильным ответам
    """
    try:
        client = get_client()
        spreadsheet = client.open(SHEET_NAME)
        sheet = spreadsheet.worksheet("Пользователи")
        
        records = sheet.get_all_records()
        
        sorted_users = sorted(
            records,
            key=lambda x: int(x.get("correct_answers", 0)),
            reverse=True
        )
        
        result = []
        for user in sorted_users[:limit]:
            correct = int(user.get("correct_answers", 0))
            total = int(user.get("total_answers", 0))
            result.append({
                "username": user.get("username", "Аноним"),
                "correct": correct,
                "total": total,
                "accuracy": round(correct / total * 100, 1) if total > 0 else 0
            })
        
        return result
        
    except Exception as e:
        print(f"❌ Ошибка в get_top_users: {e}")
        return []
    
    
    
def get_random_quiz():
    """
    Возвращает случайный вопрос из листа 'Викторины'
    """
    try:
        client = get_client()
        spreadsheet = client.open(SHEET_NAME)
        
        # Проверяем, существует ли лист "Викторины"
        try:
            sheet = spreadsheet.worksheet("Викторины")
        except gspread.WorksheetNotFound:
            print("⚠️ Лист 'Викторины' не найден")
            return None
        
        records = sheet.get_all_records()
        
        if not records:
            print("⚠️ Лист 'Викторины' пуст")
            return None
        
        # Выбираем случайный вопрос
        quiz = random.choice(records)
        
        # Собираем варианты ответов
        options = [
            quiz.get("Правильный ответ"),
            quiz.get("Вариант 2"),
            quiz.get("Вариант 3"),
            quiz.get("Вариант 4")
        ]
        # Убираем пустые варианты
        options = [opt for opt in options if opt]
        
        if len(options) < 2:
            print(f"⚠️ Недостаточно вариантов для вопроса")
            return None
        
        random.shuffle(options)
        
        return {
            "question": quiz.get("Вопрос"),
            "options": options,
            "correct": quiz.get("Правильный ответ"),
            "id": quiz.get("ID", random.randint(1, 1000))
        }
        
    except Exception as e:
        print(f"❌ Ошибка в get_random_quiz: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    
def get_all_users():
    """
    Получает список всех user_id из листа 'Пользователи'
    """
    try:
        client = get_client()
        spreadsheet = client.open(SHEET_NAME)
        
        try:
            sheet = spreadsheet.worksheet("Пользователи")
        except gspread.WorksheetNotFound:
            print("⚠️ Лист 'Пользователи' ещё не создан")
            return []
        
        # Получаем все значения из колонки A (user_id)
        user_ids = sheet.col_values(1)
        
        # Пропускаем заголовок
        if user_ids and user_ids[0] == 'user_id':
            user_ids = user_ids[1:]
        
        # Фильтруем пустые значения и конвертируем в int
        result = []
        for uid in user_ids:
            if uid and uid.strip():
                try:
                    result.append(int(float(uid)))
                except:
                    pass
        
        print(f"📊 Найдено пользователей для рассылки: {len(result)}")
        return result
        
    except Exception as e:
        print(f"❌ Ошибка в get_all_users: {e}")
        return []