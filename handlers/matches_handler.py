"""
Matches handler for viewing and managing user matches.
"""
from typing import List, Tuple
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.error import TelegramError

from models.user_model import get_user_matches, get_user
from handlers.menu_handler import get_main_menu
from utils.logger import setup_logger

logger = setup_logger(__name__)


async def show_matches(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Show all matches for the user.
    
    Args:
        update: Telegram update object
        context: Bot context
    """
    try:
        if not update.message:
            return
            
        user_id = update.message.from_user.id
        matches = get_user_matches(user_id)
        
        if not matches:
            await update.message.reply_text(
                "💕 *My Matches*\n\n"
                "You don't have any matches yet! 😢\n\n"
                "Keep browsing to find your match! ❤️",
                parse_mode='Markdown',
                reply_markup=get_main_menu()
            )
            return
        
        await update.message.reply_text(
            f"💕 *My Matches* ({len(matches)})\n\n"
            "Here are your matches:",
            parse_mode='Markdown',
            reply_markup=get_main_menu()
        )
        
        # Show each match
        for match in matches:
            try:
                uid, name, age, dept, bio, photo_id = match[:6]
                
                keyboard = [
                    [InlineKeyboardButton("👤 View Full Profile", callback_data=f"view_match_{uid}")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await context.bot.send_photo(
                    chat_id=update.message.chat_id,
                    photo=photo_id,
                    caption=(
                        f"💘 *{name}*, {age}\n"
                        f"📚 *Department:* {dept}\n\n"
                        f"{bio}"
                    ),
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
            except Exception as e:
                logger.error(f"Error showing match {match[0] if match else 'unknown'}: {e}")
                continue
        
        logger.info(f"Showed {len(matches)} matches to user {user_id}")
    except TelegramError as e:
        logger.error(f"Telegram error showing matches: {e}")
        if update.message:
            await update.message.reply_text(
                "❌ An error occurred while loading matches.",
                reply_markup=get_main_menu()
            )
    except Exception as e:
        logger.error(f"Error showing matches: {e}")
        if update.message:
            await update.message.reply_text(
                "❌ An unexpected error occurred.",
                reply_markup=get_main_menu()
            )

