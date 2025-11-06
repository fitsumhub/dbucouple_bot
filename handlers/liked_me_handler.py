"""
Handler for viewing users who liked the current user.
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.error import TelegramError

from models.user_model import get_users_who_liked_me
from handlers.menu_handler import get_main_menu
from utils.logger import setup_logger

logger = setup_logger(__name__)


async def show_liked_me(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Show users who liked the current user.
    
    Args:
        update: Telegram update object
        context: Bot context
    """
    try:
        if not update.message:
            return
            
        user_id = update.message.from_user.id
        liked_me = get_users_who_liked_me(user_id)
        
        if not liked_me:
            await update.message.reply_text(
                "💌 *Liked Me*\n\n"
                "No one has liked you yet! 😢\n\n"
                "Keep browsing and improving your profile! ❤️",
                parse_mode='Markdown',
                reply_markup=get_main_menu()
            )
            return
        
        await update.message.reply_text(
            f"💌 *Liked Me* ({len(liked_me)})\n\n"
            "These users liked your profile! Like them back to match! 💘",
            parse_mode='Markdown',
            reply_markup=get_main_menu()
        )
        
        # Show each user who liked you
        for user in liked_me:
            try:
                uid, name, age, dept, bio, photo_id = user[:6]
                
                keyboard = [
                    [
                        InlineKeyboardButton("❤️ Like Back", callback_data=f"like_{uid}"),
                        InlineKeyboardButton("❌ Pass", callback_data="pass")
                    ],
                    [
                        InlineKeyboardButton("👤 View Full Profile", callback_data=f"view_{uid}")
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await context.bot.send_photo(
                    chat_id=update.message.chat_id,
                    photo=photo_id,
                    caption=(
                        f"💌 *{name}* liked your profile!\n\n"
                        f"*{name}*, {age}\n"
                        f"📚 *Department:* {dept}\n\n"
                        f"{bio}"
                    ),
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
            except Exception as e:
                logger.error(f"Error showing user {user[0] if user else 'unknown'} who liked you: {e}")
                continue
        
        logger.info(f"Showed {len(liked_me)} users who liked user {user_id}")
    except TelegramError as e:
        logger.error(f"Telegram error showing liked me: {e}")
        if update.message:
            await update.message.reply_text(
                "❌ An error occurred while loading profiles.",
                reply_markup=get_main_menu()
            )
    except Exception as e:
        logger.error(f"Error showing liked me: {e}")
        if update.message:
            await update.message.reply_text(
                "❌ An unexpected error occurred.",
                reply_markup=get_main_menu()
            )

