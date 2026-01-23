import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from sqlalchemy.orm import Session
from database import SessionLocal
from models_db import User
import threading

# Bot Token from environment
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# Global app instance for shutdown
telegram_app = None


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /start command.
    """
    await update.message.reply_text("Hello from TraderCopilot!")


async def start_telegram_bot():
    """Start the bot in non-blocking mode"""
    global telegram_app

    if not BOT_TOKEN:
        print("[TELEGRAM BOT] No Token found. Bot waiting...")
        return

    print("[TELEGRAM BOT] Initializing Bot...")

    # Build Application
    telegram_app = Application.builder().token(BOT_TOKEN).build()

    # Register Handlers
    telegram_app.add_handler(CommandHandler("start", start_command))

    # Initialize and Start
    await telegram_app.initialize()
    await telegram_app.start()
    await telegram_app.updater.start_polling(allowed_updates=Update.ALL_TYPES)

    print(f"[TELEGRAM BOT] Bot is listening (Username: @{telegram_app.bot.username})")


def start_telegram_polling():
    """
    Synchronous wrapper for main.py (Legacy)
    Recommends using bot_runner.py instead.
    """
    print("[TELEGRAM] Warning: start_telegram_polling called. Please run 'python bot_runner.py' for better stability.")
    # Threading logic removed to prevent blocking API
    pass


if __name__ == "__main__":
    # Standalone testing
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(start_telegram_bot())
        loop.run_forever()
    except KeyboardInterrupt:
        pass
