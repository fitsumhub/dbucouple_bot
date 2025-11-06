"""
Menu handler for managing the main menu and navigation buttons.
"""
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.error import TelegramError

from models.user_model import user_exists, get_user
from utils.logger import setup_logger

logger = setup_logger(__name__)


def get_main_menu() -> ReplyKeyboardMarkup:
    """
    Returns the main menu keyboard.
    
    Returns:
        ReplyKeyboardMarkup with menu buttons
    """
    keyboard = [
        [KeyboardButton("🔍 Browse Profiles"), KeyboardButton("👤 My Profile")],
        [KeyboardButton("💕 My Matches"), KeyboardButton("💌 Liked Me")],
        [KeyboardButton("📊 Statistics"), KeyboardButton("⚙️ Settings")],
        [KeyboardButton("ℹ️ Help"), KeyboardButton("📱 Menu")]
    ]
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )


def get_inline_menu() -> InlineKeyboardMarkup:
    """
    Returns the inline menu keyboard with all options as buttons.
    
    Returns:
        InlineKeyboardMarkup with menu buttons
    """
    keyboard = [
        [
            InlineKeyboardButton("🔍 Browse", callback_data="menu_browse"),
            InlineKeyboardButton("👤 My Profile", callback_data="menu_profile")
        ],
        [
            InlineKeyboardButton("💕 My Matches", callback_data="menu_matches"),
            InlineKeyboardButton("💌 Liked Me", callback_data="menu_liked_me")
        ],
        [
            InlineKeyboardButton("📊 Statistics", callback_data="menu_stats"),
            InlineKeyboardButton("⚙️ Settings", callback_data="menu_settings")
        ],
        [
            InlineKeyboardButton("ℹ️ Help", callback_data="menu_help"),
            InlineKeyboardButton("🔄 Refresh Menu", callback_data="menu_refresh")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Show the main menu to the user.
    
    Args:
        update: Telegram update object
        context: Bot context
    """
    try:
        if not update.message:
            return
            
        user_id = update.message.from_user.id
        
        if not user_exists(user_id):
            await update.message.reply_text(
                "⚠️ You need to complete your profile first!\n\nUse /start to begin registration.",
                reply_markup=ReplyKeyboardRemove()
            )
            return
        
        # Always send menu with reply_markup
        menu_text = (
            "📱 *Main Menu*\n\n"
            "Choose an option from the buttons below:\n\n"
            "• 🔍 Browse Profiles - Discover other students\n"
            "• 👤 My Profile - View your profile\n"
            "• 💕 My Matches - See your matches\n"
            "• 💌 Liked Me - Who liked you\n"
            "• 📊 Statistics - Your stats\n"
            "• ⚙️ Settings - Preferences\n"
            "• ℹ️ Help - Get help\n"
            "• 📱 Menu - Inline menu"
        )
        
        await update.message.reply_text(
            menu_text,
            reply_markup=get_main_menu(),
            parse_mode='Markdown'
        )
        logger.info(f"Menu shown to user {user_id}")
    except TelegramError as e:
        logger.error(f"Telegram error showing menu: {e}")
        if update.message:
            try:
                # Try sending without markdown as fallback
                await update.message.reply_text(
                    "📱 Main Menu\n\nChoose an option:",
                    reply_markup=get_main_menu()
                )
            except:
                pass
    except Exception as e:
        logger.error(f"Error showing menu: {e}")
        if update.message:
            try:
                await update.message.reply_text(
                    "📱 Main Menu\n\nChoose an option:",
                    reply_markup=get_main_menu()
                )
            except:
                pass


async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Show user's own profile.
    
    Args:
        update: Telegram update object
        context: Bot context
    """
    try:
        if not update.message:
            return
            
        user_id = update.message.from_user.id
        user = get_user(user_id)
        
        if not user:
            await update.message.reply_text(
                "⚠️ Profile not found. Use /start to create one.",
                reply_markup=get_main_menu()
            )
            return
        
        uid, name, age, dept, bio, photo_id = user[:6]  # Get first 6 fields
        
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        keyboard = [
            [InlineKeyboardButton("✏️ Edit Profile", callback_data="edit_profile")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.send_photo(
            chat_id=update.message.chat_id,
            photo=photo_id,
            caption=(
                f"👤 *Your Profile*\n\n"
                f"*Name:* {name}\n"
                f"*Age:* {age}\n"
                f"*Department:* {dept}\n"
                f"*Bio:* {bio}"
            ),
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
        await update.message.reply_text(
            "Use the button below to edit your profile, or use the menu buttons:",
            reply_markup=get_main_menu()
        )
        logger.debug(f"Profile shown to user {user_id}")
    except TelegramError as e:
        logger.error(f"Telegram error showing profile: {e}")
        if update.message:
            await update.message.reply_text(
                "❌ An error occurred while loading your profile.",
                reply_markup=get_main_menu()
            )
    except Exception as e:
        logger.error(f"Error showing profile: {e}")


async def handle_menu_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle menu button clicks.
    
    Args:
        update: Telegram update object
        context: Bot context
    """
    try:
        # Skip if user is in registration process
        if context.user_data.get('step'):
            return
        
        if not update.message or not update.message.text:
            return
        
        text = update.message.text
        
        # Only handle known menu buttons
        menu_buttons = [
            "🔍 Browse Profiles", 
            "👤 My Profile", 
            "💕 My Matches",
            "💌 Liked Me",
            "📊 Statistics",
            "⚙️ Settings",
            "ℹ️ Help",
            "📱 Menu"
        ]
        if text not in menu_buttons:
            return  # Not a menu button
        
        if text == "🔍 Browse Profiles":
            from handlers.browse_handler import browse
            await browse(update, context)
        elif text == "👤 My Profile":
            await show_profile(update, context)
        elif text == "💕 My Matches":
            from handlers.matches_handler import show_matches
            await show_matches(update, context)
        elif text == "💌 Liked Me":
            from handlers.liked_me_handler import show_liked_me
            await show_liked_me(update, context)
        elif text == "📊 Statistics":
            await show_statistics(update, context)
        elif text == "⚙️ Settings":
            from handlers.preferences_handler import show_preferences
            await show_preferences(update, context)
        elif text == "ℹ️ Help":
            await show_help(update, context)
        elif text == "📱 Menu":
            await show_inline_menu(update, context)
    except Exception as e:
        logger.error(f"Error handling menu button: {e}")


async def show_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Show user statistics.
    
    Args:
        update: Telegram update object
        context: Bot context
    """
    try:
        if not update.message:
            return
            
        user_id = update.message.from_user.id
        
        from database import db_manager
        cursor = db_manager.cursor
        
        # Get likes given
        cursor.execute('SELECT COUNT(*) FROM likes WHERE liker_id = ?', (user_id,))
        likes_given = cursor.fetchone()[0]
        
        # Get likes received
        cursor.execute('SELECT COUNT(*) FROM likes WHERE liked_id = ?', (user_id,))
        likes_received = cursor.fetchone()[0]
        
        # Get matches
        from models.user_model import get_user_matches
        matches = get_user_matches(user_id)
        matches_count = len(matches)
        
        # Get profile views (approximate - based on likes received)
        profile_views = likes_received
        
        await update.message.reply_text(
            f"📊 *Your Statistics*\n\n"
            f"❤️ *Likes Given:* {likes_given}\n"
            f"💌 *Likes Received:* {likes_received}\n"
            f"💘 *Matches:* {matches_count}\n"
            f"👀 *Profile Views:* ~{profile_views}\n\n"
            f"Keep connecting! 🚀",
            parse_mode='Markdown',
            reply_markup=get_main_menu()
        )
        logger.debug(f"Statistics shown to user {user_id}")
    except Exception as e:
        logger.error(f"Error showing statistics: {e}")
        if update.message:
            await update.message.reply_text(
                "❌ An error occurred while loading statistics.",
                reply_markup=get_main_menu()
            )


async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Show help information.
    
    Args:
        update: Telegram update object
        context: Bot context
    """
    try:
        if not update.message:
            return
            
        help_text = (
            "ℹ️ *University Connect Bot - Help*\n\n"
            "*Commands:*\n"
            "• /start - Create or edit your profile\n"
            "• /browse - Browse profiles\n"
            "• /menu - Show main menu\n\n"
            "*Menu Buttons:*\n"
            "• 🔍 Browse Profiles - See other students\n"
            "• 👤 My Profile - View your profile\n"
            "• 💕 My Matches - View your matches\n"
            "• 💌 Liked Me - See who liked you\n"
            "• 📊 Statistics - View your stats\n"
            "• ⚙️ Settings - Set filters & preferences\n"
            "• ℹ️ Help - Show this help\n"
            "• 📱 Menu - Show inline menu buttons\n\n"
            "*How to Use:*\n"
            "1. Complete your profile with /start\n"
            "2. Browse profiles and like/pass\n"
            "3. When someone likes you back, it's a match! 💘\n"
            "4. Use Settings to filter by age/department\n\n"
            "*Tips:*\n"
            "• Add a great photo and bio\n"
            "• Be active - browse regularly\n"
            "• Use filters to find your type\n"
            "• Respect other users\n\n"
            "Need more help? Contact support!"
        )
        
        await update.message.reply_text(
            help_text,
            parse_mode='Markdown',
            reply_markup=get_main_menu()
        )
        logger.debug(f"Help shown to user {update.message.from_user.id}")
    except Exception as e:
        logger.error(f"Error showing help: {e}")


async def show_inline_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Show inline menu with button options.
    
    Args:
        update: Telegram update object
        context: Bot context
    """
    try:
        if not update.message:
            return
            
        user_id = update.message.from_user.id
        
        if not user_exists(user_id):
            await update.message.reply_text(
                "⚠️ You need to complete your profile first!\n\nUse /start to begin registration.",
                reply_markup=ReplyKeyboardRemove()
            )
            return
        
        await update.message.reply_text(
            "📱 *Quick Menu*\n\nChoose an option using the buttons below:",
            parse_mode='Markdown',
            reply_markup=get_inline_menu()
        )
        logger.debug(f"Inline menu shown to user {user_id}")
    except TelegramError as e:
        logger.error(f"Telegram error showing inline menu: {e}")
    except Exception as e:
        logger.error(f"Error showing inline menu: {e}")


async def handle_inline_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle inline menu button callbacks.
    
    Args:
        update: Telegram update object
        context: Bot context
    """
    query = None
    try:
        query = update.callback_query
        if not query:
            return
        
        data = query.data
        user_id = query.from_user.id
        
        if not data or not data.startswith("menu_"):
            return
        
        # Check if user exists
        if not user_exists(user_id):
            await query.answer("⚠️ Please complete your profile first with /start", show_alert=True)
            return
        
        action = data.replace("menu_", "")
        chat_id = query.message.chat_id
        
        if action == "browse":
            await query.answer("🔍 Opening browse...")
            from handlers.browse_handler import show_next_profile
            await show_next_profile(context, chat_id, user_id)
            
        elif action == "profile":
            await query.answer("👤 Loading your profile...")
            user = get_user(user_id)
            if user:
                uid, name, age, dept, bio, photo_id = user[:6]
                keyboard = [
                    [InlineKeyboardButton("✏️ Edit Profile", callback_data="edit_profile")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await context.bot.send_photo(
                    chat_id=chat_id,
                    photo=photo_id,
                    caption=(
                        f"👤 *Your Profile*\n\n"
                        f"*Name:* {name}\n"
                        f"*Age:* {age}\n"
                        f"*Department:* {dept}\n"
                        f"*Bio:* {bio}"
                    ),
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
            else:
                await query.answer("❌ Profile not found", show_alert=True)
            
        elif action == "matches":
            await query.answer("💕 Loading matches...")
            from models.user_model import get_user_matches
            matches = get_user_matches(user_id)
            if not matches:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=(
                        "💕 *My Matches*\n\n"
                        "You don't have any matches yet! 😢\n\n"
                        "Keep browsing to find your match! ❤️"
                    ),
                    parse_mode='Markdown',
                    reply_markup=get_main_menu()
                )
            else:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"💕 *My Matches* ({len(matches)})\n\nHere are your matches:",
                    parse_mode='Markdown',
                    reply_markup=get_main_menu()
                )
                for match in matches:
                    try:
                        uid, name, age, dept, bio, photo_id = match[:6]
                        keyboard = [
                            [InlineKeyboardButton("👤 View Full Profile", callback_data=f"view_match_{uid}")]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        await context.bot.send_photo(
                            chat_id=chat_id,
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
                        logger.error(f"Error showing match: {e}")
                        continue
            
        elif action == "liked_me":
            await query.answer("💌 Loading who liked you...")
            from models.user_model import get_users_who_liked_me
            liked_me = get_users_who_liked_me(user_id)
            if not liked_me:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=(
                        "💌 *Liked Me*\n\n"
                        "No one has liked you yet! 😢\n\n"
                        "Keep browsing and improving your profile! ❤️"
                    ),
                    parse_mode='Markdown',
                    reply_markup=get_main_menu()
                )
            else:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=(
                        f"💌 *Liked Me* ({len(liked_me)})\n\n"
                        "These users liked your profile! Like them back to match! 💘"
                    ),
                    parse_mode='Markdown',
                    reply_markup=get_main_menu()
                )
                for user in liked_me:
                    try:
                        uid, name, age, dept, bio, photo_id = user[:6]
                        keyboard = [
                            [
                                InlineKeyboardButton("❤️ Like Back", callback_data=f"like_{uid}"),
                                InlineKeyboardButton("❌ Pass", callback_data="pass")
                            ],
                            [InlineKeyboardButton("👤 View Full Profile", callback_data=f"view_{uid}")]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        await context.bot.send_photo(
                            chat_id=chat_id,
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
                        logger.error(f"Error showing user who liked you: {e}")
                        continue
            
        elif action == "stats":
            await query.answer("📊 Loading statistics...")
            from database import db_manager
            cursor = db_manager.cursor
            cursor.execute('SELECT COUNT(*) FROM likes WHERE liker_id = ?', (user_id,))
            likes_given = cursor.fetchone()[0]
            cursor.execute('SELECT COUNT(*) FROM likes WHERE liked_id = ?', (user_id,))
            likes_received = cursor.fetchone()[0]
            from models.user_model import get_user_matches
            matches = get_user_matches(user_id)
            matches_count = len(matches)
            profile_views = likes_received
            await context.bot.send_message(
                chat_id=chat_id,
                text=(
                    f"📊 *Your Statistics*\n\n"
                    f"❤️ *Likes Given:* {likes_given}\n"
                    f"💌 *Likes Received:* {likes_received}\n"
                    f"💘 *Matches:* {matches_count}\n"
                    f"👀 *Profile Views:* ~{profile_views}\n\n"
                    f"Keep connecting! 🚀"
                ),
                parse_mode='Markdown',
                reply_markup=get_main_menu()
            )
            
        elif action == "settings":
            await query.answer("⚙️ Opening settings...")
            from handlers.preferences_handler import get_preferences_menu
            await context.bot.send_message(
                chat_id=chat_id,
                text=(
                    "⚙️ *Settings*\n\n"
                    "Set your preferences to filter profiles:\n\n"
                    "• Age range\n"
                    "• Department\n\n"
                    "Choose your filters:"
                ),
                parse_mode='Markdown',
                reply_markup=get_preferences_menu()
            )
            
        elif action == "help":
            await query.answer("ℹ️ Showing help...")
            help_text = (
                "ℹ️ *University Connect Bot - Help*\n\n"
                "*Commands:*\n"
                "• /start - Create or edit your profile\n"
                "• /browse - Browse profiles\n"
                "• /menu - Show main menu\n\n"
                "*Menu Buttons:*\n"
                "• 🔍 Browse Profiles - See other students\n"
                "• 👤 My Profile - View your profile\n"
                "• 💕 My Matches - View your matches\n"
                "• 💌 Liked Me - See who liked you\n"
                "• 📊 Statistics - View your stats\n"
                "• ⚙️ Settings - Set filters & preferences\n"
                "• ℹ️ Help - Show this help\n"
                "• 📱 Menu - Show inline menu buttons\n\n"
                "*How to Use:*\n"
                "1. Complete your profile with /start\n"
                "2. Browse profiles and like/pass\n"
                "3. When someone likes you back, it's a match! 💘\n"
                "4. Use Settings to filter by age/department\n\n"
                "*Tips:*\n"
                "• Add a great photo and bio\n"
                "• Be active - browse regularly\n"
                "• Use filters to find your type\n"
                "• Respect other users\n\n"
                "Need more help? Contact support!"
            )
            await context.bot.send_message(
                chat_id=chat_id,
                text=help_text,
                parse_mode='Markdown',
                reply_markup=get_main_menu()
            )
            
        elif action == "refresh":
            await query.answer("🔄 Refreshing menu...")
            await query.message.edit_text(
                "📱 *Quick Menu*\n\nChoose an option using the buttons below:",
                parse_mode='Markdown',
                reply_markup=get_inline_menu()
            )
            
    except TelegramError as e:
        logger.error(f"Telegram error handling inline menu callback: {e}")
        if query:
            try:
                await query.answer("❌ An error occurred", show_alert=True)
            except:
                pass
    except Exception as e:
        logger.error(f"Error handling inline menu callback: {e}")
        if query:
            try:
                await query.answer("❌ An error occurred", show_alert=True)
            except:
                pass
