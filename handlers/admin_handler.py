"""
Admin commands handler for bot management.
"""
import os
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TelegramError

from database import db_manager
from models.user_model import get_user, user_exists
from utils.logger import setup_logger
from utils.rate_limiter import rate_limiter

logger = setup_logger(__name__)

# Admin user IDs (set in environment or config)
ADMIN_IDS = [int(uid) for uid in os.getenv("ADMIN_IDS", "").split(",") if uid.strip()]


def is_admin(user_id: int) -> bool:
    """Check if user is an admin."""
    return user_id in ADMIN_IDS


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle admin commands.
    
    Available commands:
    /admin_stats - Bot statistics
    /admin_users - User count
    /admin_user <user_id> - Get user info
    /admin_reset <user_id> - Reset user rate limit
    """
    try:
        if not update.message:
            return
        
        user_id = update.message.from_user.id
        
        if not is_admin(user_id):
            await update.message.reply_text("❌ Access denied. Admin only.")
            return
        
        command = context.args[0] if context.args else None
        
        if command == "stats":
            await show_admin_stats(update, context)
        elif command == "users":
            await show_user_count(update, context)
        elif command == "user" and len(context.args) > 1:
            target_id = int(context.args[1])
            await show_user_info(update, context, target_id)
        elif command == "reset" and len(context.args) > 1:
            target_id = int(context.args[1])
            rate_limiter.reset(target_id)
            await update.message.reply_text(f"✅ Rate limit reset for user {target_id}")
        else:
            await update.message.reply_text(
                "📊 *Admin Commands*\n\n"
                "• /admin stats - Bot statistics\n"
                "• /admin users - User count\n"
                "• /admin user <user_id> - Get user info\n"
                "• /admin reset <user_id> - Reset rate limit\n",
                parse_mode='Markdown'
            )
    except Exception as e:
        logger.error(f"Error in admin command: {e}")
        if update.message:
            await update.message.reply_text("❌ Error executing admin command.")


async def show_admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show bot statistics."""
    try:
        cursor = db_manager.cursor
        
        # Total users
        cursor.execute('SELECT COUNT(*) FROM users')
        total_users = cursor.fetchone()[0]
        
        # Total likes
        cursor.execute('SELECT COUNT(*) FROM likes')
        total_likes = cursor.fetchone()[0]
        
        # Total matches
        cursor.execute('SELECT COUNT(*) FROM matches')
        total_matches = cursor.fetchone()[0]
        
        # Active users (with likes)
        cursor.execute('SELECT COUNT(DISTINCT liker_id) FROM likes')
        active_users = cursor.fetchone()[0]
        
        stats_text = (
            f"📊 *Bot Statistics*\n\n"
            f"👥 Total Users: {total_users}\n"
            f"❤️ Total Likes: {total_likes}\n"
            f"💘 Total Matches: {total_matches}\n"
            f"🔥 Active Users: {active_users}\n"
            f"📈 Match Rate: {(total_matches/total_likes*100 if total_likes > 0 else 0):.1f}%"
        )
        
        await update.message.reply_text(stats_text, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error showing admin stats: {e}")


async def show_user_count(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show user count."""
    try:
        cursor = db_manager.cursor
        cursor.execute('SELECT COUNT(*) FROM users')
        count = cursor.fetchone()[0]
        await update.message.reply_text(f"👥 Total registered users: {count}")
    except Exception as e:
        logger.error(f"Error showing user count: {e}")


async def show_user_info(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int) -> None:
    """Show information about a specific user."""
    try:
        if not user_exists(user_id):
            await update.message.reply_text(f"❌ User {user_id} not found.")
            return
        
        user = get_user(user_id)
        if user:
            uid, name, age, dept, bio, photo_id = user[:6]
            
            # Get user stats
            cursor = db_manager.cursor
            cursor.execute('SELECT COUNT(*) FROM likes WHERE liker_id = ?', (user_id,))
            likes_given = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM likes WHERE liked_id = ?', (user_id,))
            likes_received = cursor.fetchone()[0]
            
            from models.user_model import get_user_matches
            matches = get_user_matches(user_id)
            
            info_text = (
                f"👤 *User Info*\n\n"
                f"*ID:* {uid}\n"
                f"*Name:* {name}\n"
                f"*Age:* {age}\n"
                f"*Department:* {dept}\n"
                f"*Bio:* {bio[:50]}...\n\n"
                f"*Stats:*\n"
                f"❤️ Likes Given: {likes_given}\n"
                f"💌 Likes Received: {likes_received}\n"
                f"💘 Matches: {len(matches)}"
            )
            
            await update.message.reply_text(info_text, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error showing user info: {e}")

