"""
Browse handler for browsing and interacting with user profiles.
"""
from typing import Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.error import TelegramError

from models.user_model import (
    get_random_user, add_like, check_match, user_exists, save_match,
    block_user, report_user, add_favorite, remove_favorite, is_favorited, is_blocked
)
from handlers.menu_handler import get_main_menu
from utils.logger import setup_logger
from utils.rate_limiter import rate_limiter
from config import RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW, RATE_LIMIT_BAN_DURATION

logger = setup_logger(__name__)


async def show_next_profile(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    user_id: int
) -> None:
    """
    Show the next random profile to the user.
    
    Args:
        context: Bot context
        chat_id: Chat ID to send message to
        user_id: User ID to exclude from results
    """
    try:
        # Check if user has preferences set
        prefs = context.user_data.get('preferences', {})
        if prefs and any(prefs.values()):
            from models.user_model import get_users_with_filters
            user = get_users_with_filters(
                user_id,
                prefs.get('min_age'),
                prefs.get('max_age'),
                prefs.get('department')
            )
        else:
            user = get_random_user(user_id)
        if not user:
            await context.bot.send_message(
                chat_id=chat_id,
                text="No more users found right now 😢\n\nCheck back later for new profiles!"
            )
            return

        uid, name, age, dept, bio, photo_id = user[:6]  # Get first 6 fields
        
        # Check if user is favorited
        is_fav = is_favorited(user_id, uid)
        favorite_btn_text = "⭐ Unfavorite" if is_fav else "⭐ Favorite"
        favorite_btn_data = f"unfavorite_{uid}" if is_fav else f"favorite_{uid}"
        
        keyboard = [
            [
                InlineKeyboardButton("❤️ Like", callback_data=f"like_{uid}"),
                InlineKeyboardButton("❌ Pass", callback_data="pass")
            ],
            [
                InlineKeyboardButton("👤 View Full Profile", callback_data=f"view_{uid}"),
                InlineKeyboardButton(favorite_btn_text, callback_data=favorite_btn_data)
            ],
            [
                InlineKeyboardButton("🔄 Refresh", callback_data="refresh"),
                InlineKeyboardButton("🚫 Report", callback_data=f"report_{uid}")
            ],
            [
                InlineKeyboardButton("🔙 Back to Menu", callback_data="back_menu")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_photo(
            chat_id=chat_id,
            photo=photo_id,
            caption=f"*{name}*, {age}\n📚 *Department:* {dept}\n\n{bio}",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        logger.debug(f"Showed profile {uid} to user {user_id}")
    except TelegramError as e:
        logger.error(f"Telegram error showing profile to user {user_id}: {e}")
        await context.bot.send_message(
            chat_id=chat_id,
            text="❌ An error occurred while loading the profile. Please try again."
        )
    except Exception as e:
        logger.error(f"Error showing profile to user {user_id}: {e}")
        await context.bot.send_message(
            chat_id=chat_id,
            text="❌ An unexpected error occurred. Please try again later."
        )


async def browse(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /browse command to start browsing profiles.
    
    Args:
        update: Telegram update object
        context: Bot context
    """
    try:
        if not update.message:
            return
            
        user_id = update.message.from_user.id
        
        # Rate limiting check
        allowed, reason = rate_limiter.is_allowed(
            user_id, 
            RATE_LIMIT_REQUESTS, 
            RATE_LIMIT_WINDOW,
            RATE_LIMIT_BAN_DURATION
        )
        if not allowed:
            await update.message.reply_text(f"⚠️ {reason}")
            return
        
        if not user_exists(user_id):
            await update.message.reply_text(
                "⚠️ You need to complete your profile first!\n\nUse /start to begin registration.",
                reply_markup=get_main_menu()
            )
            return
        
        await show_next_profile(context, update.message.chat_id, user_id)
        logger.info(f"User {user_id} started browsing")
    except Exception as e:
        logger.error(f"Error in browse command: {e}")
        if update.message:
            await update.message.reply_text(
                "❌ An error occurred. Please try again later."
            )


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle callback queries from inline buttons.
    
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

        if not data:
            await query.answer("❌ Invalid action")
            return

        # Handle like action
        if data.startswith("like_"):
            try:
                liked_id = int(data.split("_")[1])
                
                if add_like(user_id, liked_id):
                    if check_match(user_id, liked_id):
                        # Save match to database
                        save_match(user_id, liked_id)
                        await query.answer("💘 It's a match!", show_alert=True)
                        await query.message.reply_text(
                            "💘 *It's a match!* You both liked each other! 🎉\n\n"
                            "Check '💕 My Matches' to see all your matches!",
                            parse_mode='Markdown'
                        )
                        logger.info(f"Match between {user_id} and {liked_id}")
                    else:
                        await query.answer("❤️ Liked!")
                        await query.message.reply_text("❤️ You liked this profile!")
                    
                    # Show next profile after liking
                    await show_next_profile(context, query.message.chat_id, user_id)
                else:
                    await query.answer("❌ Failed to save like. Please try again.", show_alert=True)
            except (ValueError, IndexError) as e:
                logger.error(f"Invalid like callback data: {data}, error: {e}")
                await query.answer("❌ Invalid action", show_alert=True)
                
        # Handle pass action
        elif data == "pass":
            await query.answer("⏭ Passed!")
            # Show next profile after passing
            await show_next_profile(context, query.message.chat_id, user_id)
            
        # Handle skip action
        elif data == "skip":
            await query.answer("⏭ Skipped!")
            # Show next profile immediately
            await show_next_profile(context, query.message.chat_id, user_id)
            
        # Handle back to menu
        elif data == "back_menu":
            await query.answer("🔙 Returning to menu...")
            from handlers.menu_handler import get_main_menu
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text="📱 *Main Menu*\n\nChoose an option:",
                parse_mode='Markdown',
                reply_markup=get_main_menu()
            )
        # Handle view match profile action FIRST (more specific)
        elif data.startswith("view_match_"):
            try:
                match_id = int(data.split("_")[2])
                await query.answer("⏳ Loading match profile...")
                
                from models.user_model import get_user
                match_user = get_user(match_id)
                if match_user:
                    uid, name, age, dept, bio, photo_id = match_user[:6]
                    await context.bot.send_photo(
                        chat_id=query.message.chat_id,
                        photo=photo_id,
                        caption=(
                            f"💘 *{name}*, {age}\n"
                            f"📚 *Department:* {dept}\n\n"
                            f"*Bio:*\n{bio}"
                        ),
                        parse_mode='Markdown'
                    )
                else:
                    await query.answer("❌ Match profile not found", show_alert=True)
            except (ValueError, IndexError) as e:
                logger.error(f"Error viewing match profile: {e}")
                await query.answer("❌ Error loading match", show_alert=True)
        
        # Handle view profile action (general view)
        elif data.startswith("view_"):
            try:
                view_id = int(data.split("_")[1])
                await query.answer("⏳ Loading profile...")
                
                from models.user_model import get_user
                view_user = get_user(view_id)
                if view_user:
                    uid, name, age, dept, bio, photo_id = view_user[:6]
                    
                    # Check if this is a match
                    is_match = check_match(user_id, view_id)
                    match_text = "💘 *Your Match!*\n\n" if is_match else ""
                    
                    await context.bot.send_photo(
                        chat_id=query.message.chat_id,
                        photo=photo_id,
                        caption=(
                            f"{match_text}"
                            f"👤 *{name}*, {age}\n"
                            f"📚 *Department:* {dept}\n\n"
                            f"*Bio:*\n{bio}"
                        ),
                        parse_mode='Markdown'
                    )
                    
                    # Show action buttons for full profile view
                    keyboard = [
                        [
                            InlineKeyboardButton("❤️ Like", callback_data=f"like_{view_id}"),
                            InlineKeyboardButton("❌ Pass", callback_data="pass")
                        ]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await context.bot.send_message(
                        chat_id=query.message.chat_id,
                        text="What would you like to do?",
                        reply_markup=reply_markup
                    )
                else:
                    await query.answer("❌ Profile not found", show_alert=True)
            except (ValueError, IndexError) as e:
                logger.error(f"Error viewing profile: {e}")
                await query.answer("❌ Error loading profile", show_alert=True)
        
        # Handle refresh
        elif data == "refresh":
            await query.answer("🔄 Refreshing...")
            await show_next_profile(context, query.message.chat_id, user_id)
        
        # Handle favorite
        elif data.startswith("favorite_"):
            try:
                favorite_id = int(data.split("_")[1])
                if add_favorite(user_id, favorite_id):
                    await query.answer("⭐ Added to favorites!")
                    await query.message.reply_text("⭐ Profile saved to favorites!")
                else:
                    await query.answer("❌ Failed to add favorite", show_alert=True)
            except (ValueError, IndexError) as e:
                logger.error(f"Error favoriting user: {e}")
                await query.answer("❌ Error", show_alert=True)
        
        # Handle unfavorite
        elif data.startswith("unfavorite_"):
            try:
                favorite_id = int(data.split("_")[1])
                if remove_favorite(user_id, favorite_id):
                    await query.answer("⭐ Removed from favorites!")
                    await query.message.reply_text("⭐ Removed from favorites!")
                else:
                    await query.answer("❌ Failed to remove favorite", show_alert=True)
            except (ValueError, IndexError) as e:
                logger.error(f"Error unfavoriting user: {e}")
                await query.answer("❌ Error", show_alert=True)
        
        # Handle report
        elif data.startswith("report_"):
            try:
                reported_id = int(data.split("_")[1])
                await query.answer("🚫 Reporting user...")
                
                # Ask for report reason
                context.user_data['reporting_id'] = reported_id
                context.user_data['step'] = 'report_reason'
                
                keyboard = [
                    [
                        InlineKeyboardButton("❌ Cancel", callback_data="cancel_report")
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.message.reply_text(
                    "🚫 *Report User*\n\n"
                    "Please provide a reason for reporting this user:\n"
                    "(e.g., Inappropriate content, Spam, Fake profile, etc.)",
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
            except (ValueError, IndexError) as e:
                logger.error(f"Error reporting user: {e}")
                await query.answer("❌ Error", show_alert=True)
        
        # Handle cancel report
        elif data == "cancel_report":
            context.user_data.pop('reporting_id', None)
            context.user_data.pop('step', None)
            await query.answer("❌ Report cancelled")
            await query.message.reply_text("Report cancelled.")
        
        # Handle block user
        elif data.startswith("block_"):
            try:
                blocked_id = int(data.split("_")[1])
                if block_user(user_id, blocked_id):
                    await query.answer("🚫 User blocked", show_alert=True)
                    await query.message.reply_text(
                        "🚫 *User Blocked*\n\n"
                        "This user's profile will no longer appear in your browse results.",
                        parse_mode='Markdown'
                    )
                    # Show next profile
                    await show_next_profile(context, query.message.chat_id, user_id)
                else:
                    await query.answer("❌ Failed to block user", show_alert=True)
            except (ValueError, IndexError) as e:
                logger.error(f"Error blocking user: {e}")
                await query.answer("❌ Error", show_alert=True)
        
        # Handle edit profile
        elif data == "edit_profile":
            await query.answer("✏️ Starting profile edit...")
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text="👋 Let's update your profile!\n\nPlease enter your name:",
                parse_mode='Markdown'
            )
            context.user_data['step'] = 'name'
            
    except TelegramError as e:
        logger.error(f"Telegram error handling callback: {e}")
        if query:
            try:
                await query.answer("❌ An error occurred", show_alert=True)
            except:
                pass
    except Exception as e:
        logger.error(f"Error handling callback: {e}")
        if query:
            try:
                await query.answer("❌ An error occurred", show_alert=True)
            except:
                pass
