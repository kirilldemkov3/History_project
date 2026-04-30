"""
Основная логика бота
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler
import keyboards
import utils
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
import datetime
logger = logging.getLogger(__name__)


# ========== ОСНОВНЫЕ КОМАНДЫ ==========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Команда /start — приветствие и показ главного меню
    """
    user = update.effective_user
    user_id = update.effective_chat.id
    
    logger.info(f"Пользователь {user.first_name} (ID: {user_id}) запустил бота")
    
    welcome_text = (
        f"🤖 *Добро пожаловать в «Научный календарь»*, {user.first_name}!\n\n"
        f"Я буду рассказывать тебе об изобретениях и великих учёных.\n\n"
        f"📅 *Что я умею:*\n"
        f"• Ежедневная рассылка фактов о науке\n"
        f"• Викторины для проверки знаний\n"
        f"• Личная статистика и рейтинг\n\n"
        f"👇 *Выбери действие в меню ниже* 👇"
    )
    
    await update.message.reply_text(
        welcome_text,
        parse_mode="Markdown",
        reply_markup=keyboards.get_main_menu()
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Команда /help — справка
    """
    help_text = (
        "ℹ️ *Как пользоваться ботом*\n\n"
        "📅 *Сегодня в науке* — событие текущего дня\n"
        "🎲 *Случайное событие* — рандомный факт\n"
        "📊 *Мой рейтинг* — ваша статистика\n"
        "🏆 *Топ пользователей* — таблица лидеров\n\n"
        "❓ *Викторина*\n"
        "После каждого факта вы можете проверить знания, ответив на вопрос.\n\n"
        "📅 *Ежедневная рассылка*\n"
        "Каждый день в 9:00 я присылаю факт дня и вопрос!"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")


# ========== ОБРАБОТЧИКИ КНОПОК ГЛАВНОГО МЕНЮ ==========

async def today_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик кнопки «Сегодня в науке» (без предложения викторины)
    """
    # Получаем событие для сегодняшнего дня
    event = utils.get_today_event()
    
    # Проверяем, нашлось ли событие
    if event is None:
        await update.message.reply_text(
            "😕 Сегодня нет записей в базе данных.\n\n"
            "Добавь информацию в Google Таблицу или попробуй другую дату!",
            reply_markup=keyboards.get_main_menu()
        )
        return
    
    # Формируем сообщение ТОЛЬКО о событии (без викторины)
    message = (
        f"📅 *Сегодня в истории науки*\n\n"
        f"🔬 *{event['title']}*\n"
        f"👨‍🔬 Изобретатель: *{event['inventor']}*\n"
        f"📅 Год: *{event['year']}*\n\n"
        f"📝 {event['description']}"
    )
    
    # Отправляем сообщение без кнопок викторины
    await update.message.reply_text(
        message,
        parse_mode="Markdown",
        reply_markup=keyboards.get_main_menu()  # ← просто возвращаем главное меню
    )

async def random_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик кнопки «Случайное событие»
    """
    event = utils.get_random_event()
    
    message = (
        f"🎲 *Случайное событие*\n\n"
        f"Знаете ли вы, что...\n\n"
        f"🔬 *{event['title']}*\n"
        f"👨‍🔬 {event['inventor']}\n"
        f"📅 {event['year']} год\n\n"
        f"📝 {event['description']}"
    )
    
    await update.message.reply_text(message, parse_mode="Markdown")


async def my_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик кнопки «Мой рейтинг» — показывает статистику пользователя
    """
    user_id = update.effective_chat.id
    user = update.effective_user
    
    stats = utils.get_user_stats(user_id, user.first_name)
    
    # Определяем эмодзи в зависимости от точности
    if stats["accuracy"] >= 80:
        emoji = "🏆"
    elif stats["accuracy"] >= 60:
        emoji = "📈"
    elif stats["accuracy"] >= 40:
        emoji = "📊"
    else:
        emoji = "🌱"
    
    message = (
        f"📊 *{emoji} Ваша статистика*, {stats['username']}\n\n"
        f"✅ Правильных ответов: *{stats['correct']}*\n"
        f"❌ Неправильных: *{stats['total'] - stats['correct']}*\n"
        f"📈 Точность: *{stats['accuracy']}%*\n"
        f"🎯 Пройдено викторин: *{stats['total']}*"
    )
    
    await update.message.reply_text(message, parse_mode="Markdown")


async def top_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик кнопки «Топ пользователей»
    """
    top = utils.get_top_users(10)
    
    if not top:
        await update.message.reply_text("Пока нет активных пользователей!")
        return
    
    message = "🏆 *Топ пользователей*\n\n"
    
    emojis = ["🥇", "🥈", "🥉"]
    for i, user in enumerate(top):
        emoji = emojis[i] if i < 3 else f"{i+1}️⃣"
        message += f"{emoji} *{user['username']}* — {user['correct']} ✅ (точность {user['accuracy']}%)\n"
    
    await update.message.reply_text(message, parse_mode="Markdown")


# ========== ОБРАБОТЧИКИ ВИКТОРИНЫ (колбэки от inline-кнопок) ==========

async def quiz_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик нажатий на inline-кнопки викторины
    """
    query = update.callback_query
    await query.answer()  # Обязательно подтверждаем получение колбэка
    
    data = query.data
    user_id = update.effective_chat.id
    
    # Получаем информацию о пользователе
    user = update.effective_user
    username = user.username if user.username else None
    first_name = user.first_name if user.first_name else None
    
    # ========== 1. КНОПКА "ВЕРНУТЬСЯ В МЕНЮ" ==========
    if data == "back_to_menu":
        await query.edit_message_text(
            "🏠 Возвращаемся в главное меню...\n\n"
            "Используйте кнопки внизу экрана!",
            reply_markup=None
        )
        return
    
    # ========== 2. КНОПКА "ЗАКОНЧИТЬ ВИКТОРИНУ" ==========
    if data == "quiz_exit":
        await query.edit_message_text(
            "❌ Викторина завершена.\n\n"
            "Возвращайся, когда будешь готов снова проверить знания!",
            reply_markup=keyboards.get_back_to_menu()
        )
        return
    
    # ========== 3. ОБРАБОТКА ОТВЕТА НА ВИКТОРИНУ (сегодняшняя) ==========
    if data.startswith("quiz_today_"):
        parts = data.split("_")
        if len(parts) >= 3:
            selected_index = int(parts[2])
            
            # Получаем данные из контекста
            correct_answer = context.user_data.get("current_quiz_correct")
            options = context.user_data.get("current_quiz_options", [])
            question = context.user_data.get("current_quiz_question", "?")
            
            if correct_answer is None:
                await query.edit_message_text(
                    "❌ Что-то пошло не так. Попробуй начать викторину заново.",
                    reply_markup=keyboards.get_back_to_menu()
                )
                return
            
            selected_answer = options[selected_index] if selected_index < len(options) else None
            
            if selected_answer is None:
                await query.edit_message_text(
                    "❌ Ошибка: вариант ответа не найден.",
                    reply_markup=keyboards.get_back_to_menu()
                )
                return
            
            # Проверяем правильность
            is_correct = (selected_answer == correct_answer)
            
            # Обновляем статистику
            utils.update_user_score(user_id, is_correct, username, first_name)
            
            # Получаем обновлённую статистику
            stats = utils.get_user_stats(user_id, username, first_name)
            
            if is_correct:
                result_text = (
                    f"✅ *Правильно!*\n\n"
                    f"Вопрос: {question}\n"
                    f"Верный ответ: {correct_answer}\n\n"
                    f"📊 +1 балл! Теперь у тебя {stats['correct']} правильных ответов из {stats['total']} (точность {stats['accuracy']}%)"
                )
            else:
                result_text = (
                    f"❌ *Неправильно.*\n\n"
                    f"Вопрос: {question}\n"
                    f"Правильный ответ: {correct_answer}\n\n"
                    f"📊 Твоя статистика: {stats['correct']} правильных из {stats['total']} (точность {stats['accuracy']}%)"
                )
            
            await query.edit_message_text(
                f"{result_text}\n\n"
                f"Попробуй ещё раз через главное меню!",
                parse_mode="Markdown",
                reply_markup=keyboards.get_back_to_menu()
            )
            return
    
    # ========== 4. ОБРАБОТКА ОТВЕТА НА СЛУЧАЙНУЮ ВИКТОРИНУ ==========
    if data.startswith("quiz_rand_"):
        parts = data.split("_")
        if len(parts) >= 3:
            selected_index = int(parts[2])
            
            # Получаем данные из контекста
            correct_answer = context.user_data.get("current_quiz_correct")
            options = context.user_data.get("current_quiz_options", [])
            question = context.user_data.get("current_quiz_question", "?")
            
            if correct_answer is None:
                await query.edit_message_text(
                    "❌ Что-то пошло не так. Попробуй начать викторину заново.",
                    reply_markup=keyboards.get_back_to_menu()
                )
                return
            
            selected_answer = options[selected_index] if selected_index < len(options) else None
            
            if selected_answer is None:
                await query.edit_message_text(
                    "❌ Ошибка: вариант ответа не найден.",
                    reply_markup=keyboards.get_back_to_menu()
                )
                return
            
            # Проверяем правильность
            is_correct = (selected_answer == correct_answer)
            
            # Обновляем статистику
            utils.update_user_score(user_id, is_correct, username, first_name)
            
            # Получаем обновлённую статистику
            stats = utils.get_user_stats(user_id, username, first_name)
            
            if is_correct:
                result_text = (
                    f"✅ *Правильно!*\n\n"
                    f"Вопрос: {question}\n"
                    f"Верный ответ: {correct_answer}\n\n"
                    f"📊 +1 балл! Теперь у тебя {stats['correct']} правильных ответов из {stats['total']} (точность {stats['accuracy']}%)"
                )
            else:
                result_text = (
                    f"❌ *Неправильно.*\n\n"
                    f"Вопрос: {question}\n"
                    f"Правильный ответ: {correct_answer}\n\n"
                    f"📊 Твоя статистика: {stats['correct']} правильных из {stats['total']} (точность {stats['accuracy']}%)"
                )
            
            await query.edit_message_text(
                f"{result_text}\n\n"
                f"Попробуй ещё раз через главное меню!",
                parse_mode="Markdown",
                reply_markup=keyboards.get_back_to_menu()
            )
            return
    
    # ========== 5. ЕСЛИ НИЧЕГО НЕ ПОДОШЛО ==========
    await query.edit_message_text(
        "❓ Неизвестная команда.\n\n"
        "Используй кнопки меню для навигации.",
        reply_markup=keyboards.get_back_to_menu()
    )

# ========== ОБРАБОТЧИК ТЕКСТОВЫХ СООБЩЕНИЙ ==========

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик текстовых сообщений (для reply-кнопок)
    """
    text = update.message.text
    
    if text == "📅 Сегодня в науке":
        await today_event(update, context)
    elif text == "🎲 Случайное событие":
        await random_event(update, context)
    elif text == "❓ Случайная викторина":
        await random_quiz(update, context)
    elif text == "📊 Мой рейтинг":
        await my_rating(update, context)
    elif text == "🏆 Топ пользователей":
        await top_users(update, context)
    elif text == "ℹ️ Помощь":
        await help_command(update, context)
    else:
        await update.message.reply_text(
            "🤔 Не понимаю эту команду.\n"
            "Пожалуйста, используй кнопки меню 👇",
            reply_markup=keyboards.get_main_menu()
        )


async def random_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик кнопки «Случайная викторина»
    """
    # Получаем случайный вопрос
    quiz = utils.get_random_quiz()
    
    if quiz is None:
        await update.message.reply_text(
            "❌ К сожалению, викторины временно недоступны.\n\n"
            "Добавь вопросы в лист 'Викторины' в Google Sheets!",
            reply_markup=keyboards.get_main_menu()
        )
        return
    
    # Сохраняем правильный ответ в контексте
    context.user_data["current_quiz_correct"] = quiz["correct"]
    context.user_data["current_quiz_question"] = quiz["question"]
    context.user_data["current_quiz_options"] = quiz["options"]
    
    # Отправляем вопрос с кнопками
    keyboard = []
    for i, option in enumerate(quiz["options"]):
        keyboard.append([InlineKeyboardButton(option, callback_data=f"quiz_rand_{i}")])
    keyboard.append([InlineKeyboardButton("❌ Закончить викторину", callback_data="quiz_exit")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🎲 *Случайная викторина!*\n\n"
        f"❓ *{quiz['question']}*\n\n"
        f"Выбери правильный вариант:",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )
    
async def daily_broadcast(context: ContextTypes.DEFAULT_TYPE):
    """
    Ежедневная рассылка события дня всем пользователям
    """
    print("🕐 Функция daily_broadcast вызвана!")  # Отладочное сообщение
    
    try:
        # Получаем всех пользователей
        users = utils.get_all_users()
        print(f"📊 Пользователи: {users}")
        
        if not users:
            print("📭 Нет пользователей")
            return
        
        # Получаем событие дня
        event = utils.get_today_event()
        
        if event and event.get('title') != "Нет данных":
            message = (
                f"📅 *Доброе утро! Сегодня {datetime.datetime.now().strftime('%d.%m.%Y')}*\n\n"
                f"🔬 *{event['title']}*\n"
                f"👨‍🔬 *{event['inventor']}*\n"
                f"📅 Год: *{event['year']}*\n\n"
                f"📝 {event['description']}"
            )
        else:
            message = "😕 Сегодня нет записей в базе данных."
        
        # Отправляем
        for user_id in users:
            try:
                await context.bot.send_message(
                    chat_id=int(user_id),
                    text=message,
                    parse_mode="Markdown"
                )
                print(f"✅ Отправлено {user_id}")
            except Exception as e:
                print(f"❌ Ошибка {user_id}: {e}")
                
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()