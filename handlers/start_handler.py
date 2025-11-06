"""
Start handler for user registration and profile creation.
"""
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TelegramError

from models.user_model import save_user, user_exists
from handlers.menu_handler import get_main_menu
from utils.logger import setup_logger
from utils.validators import (
    validate_name, validate_age, validate_department, validate_bio
)
from config import MIN_AGE, MAX_AGE

logger = setup_logger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /start command - show menu immediately for all users.
    
    Args:
        update: Telegram update object
        context: Bot context
    """
    try:
        if not update.message:
            return
        
        user_id = update.message.from_user.id
        
        # Always show menu immediately
        if user_exists(user_id):
            # Registered user - show full menu
            menu_text = (
                "👋 Welcome back to *University Connect Bot*!\n\n"
                "Use the menu buttons below to explore:\n\n"
                "• 🔍 Browse Profiles - Discover other students\n"
                "• 👤 My Profile - View your profile\n"
                "• 💕 My Matches - See your matches\n"
                "• 💌 Liked Me - Who liked you\n"
                "• 📊 Statistics - Your stats\n"
                "• ⚙️ Settings - Preferences\n"
                "• ℹ️ Help - Get help\n"
                "• 📱 Menu - Inline menu"
            )
        else:
            # New user - show menu and start registration
            menu_text = (
                "👋 Welcome to *University Connect Bot*!\n\n"
                "Let's build your profile to start connecting!\n\n"
                "*Menu Options:*\n"
                "• 🔍 Browse Profiles - Discover students\n"
                "• 👤 My Profile - View/Edit profile\n"
                "• 💕 My Matches - See matches\n"
                "• 💌 Liked Me - Who liked you\n"
                "• 📊 Statistics - Your stats\n"
                "• ⚙️ Settings - Preferences\n"
                "• ℹ️ Help - Get help\n"
                "• 📱 Menu - Inline menu\n\n"
                "📝 *To complete your profile, please enter your name:*"
            )
            # Start registration process
            context.user_data['step'] = 'name'
        
        # Always send menu with buttons
        await update.message.reply_text(
            menu_text,
            reply_markup=get_main_menu(),
            parse_mode='Markdown'
        )
        
        # Clear any old registration state if user exists
        if user_exists(user_id):
            context.user_data.clear()
        
        logger.info(f"User {user_id} accessed bot via /start - menu shown")
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        if update.message:
            try:
                # Fallback: send menu without markdown
                await update.message.reply_text(
                    "👋 Welcome to University Connect Bot!\n\nUse the menu buttons below:",
                    reply_markup=get_main_menu()
                )
            except:
                pass


async def handle_registration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle user registration flow step by step.
    
    Args:
        update: Telegram update object
        context: Bot context
    """
    try:
        if not update.message:
            return
            
        step = context.user_data.get('step', '')
        
        # Skip if not in registration and text is a menu button
        if not step and update.message.text:
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
            if update.message.text in menu_buttons:
                return  # Let menu handler process it
        
        # Handle photo uploads during registration
        if step == 'photo' and update.message.photo:
            photo_id = update.message.photo[-1].file_id
            user_id = update.message.from_user.id
            
            # Retrieve stored data
            name = context.user_data.get('name')
            age_str = context.user_data.get('age')
            dept = context.user_data.get('department')
            bio = context.user_data.get('bio')
            
            # Validate all data exists
            if not all([name, age_str, dept, bio]):
                await update.message.reply_text(
                    "❌ Registration data incomplete. Please use /start to begin again."
                )
                context.user_data.clear()
                return
            
            # Validate age
            is_valid, age = validate_age(age_str)
            if not is_valid:
                await update.message.reply_text(
                    f"❌ Invalid age. Please use /start to begin again."
                )
                context.user_data.clear()
                return
            
            # Save user profile
            if save_user(user_id, name, age, dept, bio, photo_id):
                menu_text = (
                    "✅ *Profile created successfully!*\n\n"
                    "Use the menu buttons below to explore:\n\n"
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
                context.user_data.clear()
                logger.info(f"User {user_id} completed registration")
            else:
                await update.message.reply_text(
                    "❌ Failed to save profile. Please try again later."
                )
            return
        
        # Skip non-text messages during text steps
        if not update.message.text:
            return

        # Handle text-based registration steps
        if step == 'name':
            if not validate_name(update.message.text):
                await update.message.reply_text(
                    "❌ Invalid name. Please enter a name (2-50 characters):"
                )
                return
            context.user_data['name'] = update.message.text.strip()
            context.user_data['step'] = 'age'
            await update.message.reply_text("Enter your age:")
            
        elif step == 'age':
            is_valid, age = validate_age(update.message.text)
            if not is_valid:
                await update.message.reply_text(
                    f"❌ Invalid age. Please enter a number between {MIN_AGE} and {MAX_AGE}:"
                )
                return
            context.user_data['age'] = str(age)
            context.user_data['step'] = 'department'
            await update.message.reply_text("Enter your department:")
            
        elif step == 'department':
            if not validate_department(update.message.text):
                await update.message.reply_text(
                    "❌ Invalid department. Please enter a valid department name (2-100 characters):"
                )
                return
            context.user_data['department'] = update.message.text.strip()
            context.user_data['step'] = 'bio'
            await update.message.reply_text("Write a short bio (10-500 characters):")
            
        elif step == 'bio':
            if not validate_bio(update.message.text):
                await update.message.reply_text(
                    "❌ Bio too short or too long. Please write a bio between 10-500 characters:"
                )
                return
            context.user_data['bio'] = update.message.text.strip()
            context.user_data['step'] = 'photo'
            await update.message.reply_text("📸 Send your photo:")
            
    except TelegramError as e:
        logger.error(f"Telegram error in registration: {e}")
        if update.message:
            await update.message.reply_text(
                "❌ An error occurred. Please try again."
            )
    except Exception as e:
        logger.error(f"Error in registration handler: {e}")
        if update.message:
            await update.message.reply_text(
                "❌ An unexpected error occurred. Please use /start to begin again."
            )
