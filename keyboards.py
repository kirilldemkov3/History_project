"""
Все клавиатуры бота
"""

from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
# ========== REPLY-КЛАВИАТУРА (главное меню) ==========
# Прикрепляется к полю ввода, всегда видна

def get_main_menu():
    """
    Главное меню бота (reply-кнопки)
    """
    keyboard = [
        ["📅 Сегодня в науке", "🎲 Случайное событие"],
        ["❓ Случайная викторина", "📊 Мой рейтинг"],  # ← Новая кнопка
        ["🏆 Топ пользователей", "ℹ️ Помощь"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# ========== INLINE-КЛАВИАТУРЫ (внутри сообщений) ==========

def get_quiz_buttons(question_id: int = 1):
    """
    Кнопки для викторины (варианты ответов)
    Возвращает InlineKeyboardMarkup с 4 вариантами
    """
    # Временно заглушка — позже будем брать из БД
    quiz_data = {
        1: {
            "question": "Кто изобрел телефон?",
            "options": ["Александр Попов", "Томас Эдисон", "Александр Белл", "Никола Тесла"],
            "correct": "Александр Белл"
        }
    }
    
    data = quiz_data.get(question_id, quiz_data[1])
    options = data["options"]
    
    keyboard = [
        [InlineKeyboardButton(options[0], callback_data=f"quiz_{question_id}_0")],
        [InlineKeyboardButton(options[1], callback_data=f"quiz_{question_id}_1")],
        [InlineKeyboardButton(options[2], callback_data=f"quiz_{question_id}_2")],
        [InlineKeyboardButton(options[3], callback_data=f"quiz_{question_id}_3")],
    ]
    
    # Добавляем кнопку "Выход"
    keyboard.append([InlineKeyboardButton("❌ Закончить викторину", callback_data="quiz_exit")])
    
    return InlineKeyboardMarkup(keyboard), data["correct"]


def get_quiz_offer():
    """
    Кнопки "Да/Нет" после информации о событии
    """
    keyboard = [
        [
            InlineKeyboardButton("✅ Да, хочу проверить знания", callback_data="quiz_yes"),
            InlineKeyboardButton("❌ Нет, в другой раз", callback_data="quiz_no")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_back_to_menu():
    """
    Кнопка возврата в главное меню
    """
    keyboard = [
        [InlineKeyboardButton("🏠 Вернуться в главное меню", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)