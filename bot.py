"""
Main entry point for the University Connect Telegram Bot.

This module initializes and runs the Telegram bot with all handlers.
"""
import asyncio
import signal
import sys
from typing import Optional

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)
from telegram.error import TelegramError

from config import BOT_TOKEN, LOG_LEVEL, LOG_FILE
from handlers.start_handler import start, handle_registration
from handlers.browse_handler import browse, handle_callback
from handlers.menu_handler import show_menu, handle_menu_buttons, handle_inline_menu_callback
from handlers.preferences_handler import handle_preferences_callback
from handlers.admin_handler import admin_command
from utils.rate_limiter import rate_limiter
from utils.health_check import health_check, get_bot_metrics
from utils.database_utils import backup_database, optimize_database, cleanup_old_backups
from utils.scheduler import scheduler
from config import RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW, RATE_LIMIT_BAN_DURATION
from config import BACKUP_ENABLED, BACKUP_INTERVAL_HOURS
from utils.logger import setup_logger
from database import db_manager

# Setup logging
logger = setup_logger(__name__, log_level=LOG_LEVEL, log_file=LOG_FILE)


def error_handler(update: object, context) -> None:
    """
    Global error handler for unhandled exceptions.
    
    Args:
        update: Telegram update object (may be None)
        context: Bot context with error information
    """
    logger.error(
        f"Exception while handling an update: {context.error}",
        exc_info=context.error
    )
    
    # Try to send error message to user if update is available
    if update and hasattr(update, 'effective_message') and update.effective_message:
        try:
            update.effective_message.reply_text(
                "❌ An unexpected error occurred. Please try again later."
            )
        except Exception:
            pass  # Ignore errors when sending error messages


async def post_init(application: Application) -> None:
    """
    Called after the application is initialized.
    
    Args:
        application: Bot application instance
    """
    logger.info("Bot initialized successfully")
    logger.info(f"Bot token: {BOT_TOKEN[:10]}...{BOT_TOKEN[-5:]}")
    
    # Perform health check
    health = health_check()
    if health['status'] == 'healthy':
        logger.info("✅ Health check passed")
    else:
        logger.warning(f"⚠️ Health check issues: {health}")
    
    # Optimize database on startup
    optimize_database()
    
    # Cleanup old backups
    cleanup_old_backups()
    
    # Create initial backup if enabled
    if BACKUP_ENABLED:
        backup_path = backup_database()
        if backup_path:
            logger.info(f"✅ Initial backup created: {backup_path}")
    
    # Start background scheduler
    await scheduler.start()
    logger.info("✅ Background scheduler started")


async def post_shutdown(application: Application) -> None:
    """
    Called before the application shuts down.
    
    Args:
        application: Bot application instance
    """
    logger.info("Bot shutting down...")
    
    # Stop scheduler
    await scheduler.stop()
    
    # Final backup
    if BACKUP_ENABLED:
        backup_database()
    
    # Close database
    db_manager.close()
    logger.info("Bot shutdown complete")


async def health_check_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /health command."""
    try:
        if not update.message:
            return
        
        health = health_check()
        metrics = get_bot_metrics()
        
        status_emoji = "✅" if health['status'] == 'healthy' else "⚠️"
        
        health_text = (
            f"{status_emoji} *Bot Health Status*\n\n"
            f"*Status:* {health['status'].upper()}\n"
            f"*Timestamp:* {health['timestamp']}\n\n"
            f"*Metrics:*\n"
            f"👥 Users: {metrics.get('total_users', 0)}\n"
            f"❤️ Likes: {metrics.get('total_likes', 0)}\n"
            f"💘 Matches: {metrics.get('total_matches', 0)}\n"
            f"📈 Match Rate: {metrics.get('match_rate', 0):.1f}%"
        )
        
        await update.message.reply_text(health_text, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error in health check command: {e}")


def setup_handlers(application: Application) -> None:
    """
    Set up all bot handlers.
    
    Args:
        application: Bot application instance
    """
    # Commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("browse", browse))
    application.add_handler(CommandHandler("menu", show_menu))
    application.add_handler(CommandHandler("testmenu", show_menu))  # Test command
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CommandHandler("health", health_check_command))
    
    # Callback queries (inline buttons)
    # Handle preferences callbacks first, then menu callbacks, then browse callbacks
    application.add_handler(
        CallbackQueryHandler(handle_preferences_callback, pattern="^pref_"),
        group=0
    )
    application.add_handler(
        CallbackQueryHandler(handle_inline_menu_callback, pattern="^menu_"),
        group=1
    )
    application.add_handler(CallbackQueryHandler(handle_callback), group=2)
    
    # Message handlers (registration has priority, then menu buttons)
    application.add_handler(
        MessageHandler(filters.TEXT | filters.PHOTO, handle_registration),
        group=1
    )
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu_buttons),
        group=2
    )
    
    # Global error handler
    application.add_error_handler(error_handler)
    
    logger.info("All handlers registered")


def main() -> None:
    """Main function to run the bot."""
    try:
        logger.info("Starting University Connect Bot...")
        
        # Create application
        application = (
            Application.builder()
            .token(BOT_TOKEN)
            .post_init(post_init)
            .post_shutdown(post_shutdown)
            .build()
        )
        
        # Setup handlers
        setup_handlers(application)
        
        # Setup signal handlers for graceful shutdown
        def signal_handler(signum, frame):
            """Handle shutdown signals."""
            logger.info(f"Received signal {signum}, shutting down gracefully...")
            asyncio.create_task(application.stop())
            asyncio.create_task(application.shutdown())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Run the bot
        logger.info("🤖 University Connect Bot is running...")
        logger.info("Press Ctrl+C to stop the bot")
        application.run_polling(
            allowed_updates=["message", "callback_query"],
            drop_pending_updates=True
        )
        
    except TelegramError as e:
        logger.error(f"Telegram API error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("Bot process terminated")


if __name__ == "__main__":
    main()
