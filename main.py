"""
Точка входа — запуск бота
"""

import os
import datetime
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, 
    MessageHandler, filters
)
from bot import (
    start, help_command, today_event, random_event, 
    my_rating, top_users, random_quiz, quiz_callback_handler,
    handle_message, daily_broadcast
)

# Загружаем переменные из .env
load_dotenv()

# ========== НАСТРОЙКА ЛОГИРОВАНИЯ ==========
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен бота (берём из .env, а не из кода!)
TOKEN = os.getenv("BOT_TOKEN")

def main():
    if not TOKEN:
        logger.error("❌ BOT_TOKEN не найден в .env файле!")
        return
    
    logger.info("🚀 Запуск бота 'Научный календарь'...")
    
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(quiz_callback_handler))
    
    job_queue = app.job_queue
    
    if job_queue:
        target_time = datetime.time(hour=9, minute=0, second=0)
        job_queue.run_daily(
            daily_broadcast,
            time=target_time,
            days=tuple(range(7))
        )
        logger.info("✅ Ежедневная рассылка настроена на 9:00 утра")
    else:
        logger.warning("⚠️ JobQueue не доступна!")
    
    logger.info("✅ Бот готов к работе!")
    app.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()