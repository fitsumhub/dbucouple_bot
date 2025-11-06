"""
Bot diagnostic script to check for issues.
"""
import sys

print("🔍 Diagnosing bot...\n")

# Check Python version
print(f"✓ Python version: {sys.version}")

# Check imports
print("\n📦 Checking imports...")
try:
    from telegram import Update
    from telegram.ext import Application
    print("✓ python-telegram-bot imported")
except ImportError as e:
    print(f"✗ Error importing telegram: {e}")
    sys.exit(1)

try:
    from config import BOT_TOKEN, DB_PATH
    print(f"✓ Config imported (Token: {BOT_TOKEN[:10]}...{BOT_TOKEN[-5:]})")
    print(f"✓ DB path: {DB_PATH}")
except Exception as e:
    print(f"✗ Error importing config: {e}")
    sys.exit(1)

try:
    from database import db_manager
    print("✓ Database manager imported")
except Exception as e:
    print(f"✗ Error importing database: {e}")
    sys.exit(1)

# Check handlers
print("\n🎮 Checking handlers...")
handlers = [
    ("handlers.start_handler", ["start", "handle_registration"]),
    ("handlers.browse_handler", ["browse", "handle_callback", "show_next_profile"]),
    ("handlers.menu_handler", ["show_menu", "handle_menu_buttons", "get_main_menu"]),
    ("handlers.preferences_handler", ["show_preferences", "handle_preferences_callback"]),
    ("handlers.matches_handler", ["show_matches"]),
    ("handlers.liked_me_handler", ["show_liked_me"]),
    ("handlers.admin_handler", ["admin_command"]),
]

for module_name, functions in handlers:
    try:
        module = __import__(module_name, fromlist=functions)
        for func in functions:
            if hasattr(module, func):
                print(f"✓ {module_name}.{func}")
            else:
                print(f"✗ {module_name}.{func} - NOT FOUND")
    except Exception as e:
        print(f"✗ {module_name} - Error: {e}")

# Check models
print("\n📊 Checking models...")
try:
    from models.user_model import (
        save_user, get_user, get_random_user, add_like, 
        check_match, user_exists, get_user_matches
    )
    print("✓ All user model functions imported")
except Exception as e:
    print(f"✗ Error importing models: {e}")

# Check utils
print("\n🛠️ Checking utilities...")
utils = [
    "utils.logger",
    "utils.validators",
    "utils.rate_limiter",
    "utils.health_check",
    "utils.database_utils",
]
for util in utils:
    try:
        __import__(util)
        print(f"✓ {util}")
    except Exception as e:
        print(f"✗ {util} - Error: {e}")

# Check database
print("\n💾 Checking database...")
try:
    cursor = db_manager.cursor
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    required_tables = ['users', 'likes', 'matches']
    for table in required_tables:
        if table in tables:
            print(f"✓ Table '{table}' exists")
        else:
            print(f"✗ Table '{table}' MISSING")
except Exception as e:
    print(f"✗ Database error: {e}")

# Check bot.py structure
print("\n🤖 Checking bot.py structure...")
try:
    with open("bot.py", "r") as f:
        content = f.read()
        if "def main()" in content:
            print("✓ main() function found")
        if "setup_handlers" in content:
            print("✓ setup_handlers() found")
        if "Application.builder()" in content:
            print("✓ Application builder found")
        if "run_polling" in content:
            print("✓ run_polling() found")
except Exception as e:
    print(f"✗ Error reading bot.py: {e}")

print("\n✅ Diagnosis complete!")

