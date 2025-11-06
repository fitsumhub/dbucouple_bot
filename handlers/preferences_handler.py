"""
Preferences handler for filtering and customizing browse options.
"""
from typing import Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.error import TelegramError

from models.user_model import get_users_with_filters
from handlers.menu_handler import get_main_menu
from utils.logger import setup_logger
from config import MIN_AGE, MAX_AGE

logger = setup_logger(__name__)


def get_preferences_menu() -> InlineKeyboardMarkup:
    """
    Get preferences menu with filter options.
    
    Returns:
        InlineKeyboardMarkup with preference buttons
    """
    keyboard = [
        [
            InlineKeyboardButton("🔍 All Ages", callback_data="pref_age_all"),
            InlineKeyboardButton("18-25", callback_data="pref_age_18_25")
        ],
        [
            InlineKeyboardButton("26-30", callback_data="pref_age_26_30"),
            InlineKeyboardButton("31+", callback_data="pref_age_31_plus")
        ],
        [
            InlineKeyboardButton("🎓 All Departments", callback_data="pref_dept_all"),
            InlineKeyboardButton("📚 Computer Science", callback_data="pref_dept_cs")
        ],
        [
            InlineKeyboardButton("📖 Engineering", callback_data="pref_dept_eng"),
            InlineKeyboardButton("💼 Business", callback_data="pref_dept_bus")
        ],
        [
            InlineKeyboardButton("✅ Apply Filters & Browse", callback_data="pref_apply")
        ],
        [
            InlineKeyboardButton("🗑️ Clear All Filters", callback_data="pref_clear"),
            InlineKeyboardButton("❌ Cancel", callback_data="pref_cancel")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


async def show_preferences(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Show preferences menu for filtering.
    
    Args:
        update: Telegram update object
        context: Bot context
    """
    try:
        if not update.message:
            return
            
        # Initialize preferences if not set
        if 'preferences' not in context.user_data:
            context.user_data['preferences'] = {
                'min_age': None,
                'max_age': None,
                'department': None
            }
        
        await update.message.reply_text(
            "⚙️ *Browse Preferences*\n\n"
            "Choose filters to customize your browsing:\n\n"
            "• Age Range: Select age preferences\n"
            "• Department: Filter by department\n"
            "• Click 'Apply Filters & Browse' when done",
            parse_mode='Markdown',
            reply_markup=get_preferences_menu()
        )
        logger.debug(f"Preferences menu shown to user {update.message.from_user.id}")
    except Exception as e:
        logger.error(f"Error showing preferences: {e}")


async def handle_preferences_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle preferences callback queries.
    
    Args:
        update: Telegram update object
        context: Bot context
    """
    try:
        query = update.callback_query
        if not query:
            return
        
        data = query.data
        
        if not data or not data.startswith("pref_"):
            await query.answer("❌ Invalid action")
            return
        
        # Initialize preferences if not set
        if 'preferences' not in context.user_data:
            context.user_data['preferences'] = {
                'min_age': None,
                'max_age': None,
                'department': None
            }
        
        prefs = context.user_data['preferences']
        
        # Handle age preferences
        if data == "pref_age_all":
            prefs['min_age'] = None
            prefs['max_age'] = None
            await query.answer("✅ Age filter: All ages")
        elif data == "pref_age_18_25":
            prefs['min_age'] = 18
            prefs['max_age'] = 25
            await query.answer("✅ Age filter: 18-25")
        elif data == "pref_age_26_30":
            prefs['min_age'] = 26
            prefs['max_age'] = 30
            await query.answer("✅ Age filter: 26-30")
        elif data == "pref_age_31_plus":
            prefs['min_age'] = 31
            prefs['max_age'] = None
            await query.answer("✅ Age filter: 31+")
        
        # Handle department preferences
        elif data == "pref_dept_all":
            prefs['department'] = None
            await query.answer("✅ Department filter: All departments")
        elif data == "pref_dept_cs":
            prefs['department'] = "Computer Science"
            await query.answer("✅ Department filter: Computer Science")
        elif data == "pref_dept_eng":
            prefs['department'] = "Engineering"
            await query.answer("✅ Department filter: Engineering")
        elif data == "pref_dept_bus":
            prefs['department'] = "Business"
            await query.answer("✅ Department filter: Business")
        
        # Apply filters and browse
        elif data == "pref_apply":
            await query.answer("⏳ Applying filters...")
            user_id = query.from_user.id
            min_age = prefs.get('min_age')
            max_age = prefs.get('max_age')
            department = prefs.get('department')
            
            user = get_users_with_filters(user_id, min_age, max_age, department)
            
            if not user:
                await query.answer("❌ No users found with these filters", show_alert=True)
                await query.message.reply_text(
                    "❌ *No users found*\n\n"
                    "Try adjusting your preferences or check back later!",
                    parse_mode='Markdown',
                    reply_markup=get_main_menu()
                )
                return
            
            # Show the filtered profile (keep preferences in context for browsing)
            from handlers.browse_handler import show_next_profile
            await show_next_profile(context, query.message.chat_id, user_id)
            
            # Note: Preferences stay in context for continued browsing
            # They'll be cleared when user starts a new browse session
        
        # Clear all filters
        elif data == "pref_clear":
            context.user_data.pop('preferences', None)
            await query.answer("✅ All filters cleared!", show_alert=True)
            await query.message.reply_text(
                "✅ *All filters cleared!*\n\nYou can now browse all profiles.",
                parse_mode='Markdown',
                reply_markup=get_main_menu()
            )
        
        # Cancel
        elif data == "pref_cancel":
            context.user_data.pop('preferences', None)
            await query.answer("❌ Preferences cancelled")
            await query.message.reply_text(
                "❌ *Preferences cancelled.*",
                parse_mode='Markdown',
                reply_markup=get_main_menu()
            )
            
    except Exception as e:
        logger.error(f"Error handling preferences callback: {e}")
        if query:
            try:
                await query.answer("❌ An error occurred", show_alert=True)
            except:
                pass

