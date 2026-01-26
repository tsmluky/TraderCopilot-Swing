import os
import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from database import SessionLocal
from models_db import User

# Configure Logging
LOG = logging.getLogger("tradercopilot")

# Bot Token from environment
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("TRADERCOPILOT_BOT_TOKEN", "")

# Global app instance
telegram_app = None

def link_user_to_telegram(user_id: int, chat_id: str, username: str = None) -> bool:
    """Updates the user record with Telegram details."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        user.telegram_chat_id = str(chat_id)
        if username:
            user.telegram_username = username
        
        db.commit()
        LOG.info(f"Linked User {user_id} to Telegram Chat {chat_id}")
        return True
    except Exception as e:
        LOG.error(f"Failed to link user {user_id}: {e}")
        db.rollback()
        return False
    finally:
        db.close()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /start command.
    If args provided (e.g., /start 123), link the user.
    """
    chat_id = update.effective_chat.id
    username = update.effective_chat.username
    args = context.args

    if not args:
        await update.message.reply_text(
            "👋 **Welcome to TraderCopilot!**\n\n"
            "To link your account, please use the 'Connect Bot' button on the dashboard settings page.\n"
            "This will generate a secure link with your ID.",
            parse_mode="Markdown"
        )
        return

    try:
        # User ID passed via deep link: t.me/bot?start=123
        user_id = int(args[0])
        success = link_user_to_telegram(user_id, str(chat_id), username)
        
        if success:
            await update.message.reply_text(
                f"✅ **Account Linked Successfully!**\n\n"
                f"You will now receive alerts for User ID: `{user_id}`\n"
                f"Chat ID: `{chat_id}`",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text("❌ **Error:** User not found. Please check your account ID.")
            
    except ValueError:
        await update.message.reply_text("❌ **Error:** Invalid format.")
    except Exception as e:
        LOG.error(f"Telegram Start Error: {e}")
        await update.message.reply_text("❌ **System Error** while linking.")

async def start_telegram_bot_async():
    """Async entry point for main.py integration"""
    global telegram_app

    if not BOT_TOKEN:
        LOG.warning("[TELEGRAM] No Token found (TELEGRAM_BOT_TOKEN). Bot disabled.")
        return

    LOG.info("[TELEGRAM] Initializing Bot...")

    # Build Application
    telegram_app = Application.builder().token(BOT_TOKEN).build()

    # Register Handlers
    telegram_app.add_handler(CommandHandler("start", start_command))

    # Initialize and Start
    await telegram_app.initialize()
    await telegram_app.start()
    
    # Start Polling (Non-blocking way for asyncio loop)
    # Note: execute_polling is blocking. We use start_polling + manual update loop if integrated, 
    # but since main.py is FastAPI, better to run this as a background task.
    # HOWEVER, python-telegram-bot v20+ 'start_polling' is blocking if used directly on updater? 
    # No, application.start() is generic. application.run_polling() is blocking.
    # We want: updater.start_polling() (which creates a Task).
    
    await telegram_app.updater.start_polling(allowed_updates=Update.ALL_TYPES)
    LOG.info(f"[TELEGRAM] Bot verified and listening (@{telegram_app.bot.username})")

def start_telegram_polling():
    """
    Called by main.py in a standard synchronous flow. 
    Ideally, main.py should await the async version on startup.
    But since main.py calls this conditionally, we can try to schedule it on the running event loop 
    if strictly necessary, or just rely on 'bot_runner.py' separate process.
    
    For integrated Mode (e.g. Railway single container):
    We need to grab the current loop or create a thread.
    """
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(start_telegram_bot_async())
    except RuntimeError:
        # No loop running (e.g. called before app startup?)
        # Start a thread? No, database access isn't thread-safe easily with asyncio mixed.
        # Best advice: The user should define TELEGRAM_LISTENER_ENABLED=true and main.py handles it.
        # Check main.py:
        # if os.getenv...: start_telegram_polling()
        # This is called inside 'on_startup', which IS async context in FastAPI? 
        # No, 'def on_startup():' is sync. '@app.on_event("startup") async def...' is async.
        # I should change main.py to be async startup.
        pass
