# ⚡ Quick Reference Guide

## 🎯 Core Components

### 1. Main Bot File
**File:** `bot.py`
- Entry point
- Handler registration
- Application setup

### 2. Database
**File:** `database.py`
- SQLite connection
- Schema management
- Transaction support

### 3. User Model
**File:** `models/user_model.py`
- `save_user()` - Save/update profile
- `get_user()` - Get user by ID
- `get_random_user()` - Get random profile
- `add_like()` - Add like
- `check_match()` - Check if matched
- `get_user_matches()` - Get all matches
- `get_users_who_liked_me()` - Get likes received

## 🔘 Button Types

### Inline Buttons (Under Messages)
- **Like:** `callback_data=f"like_{user_id}"`
- **Pass:** `callback_data="pass"`
- **View:** `callback_data=f"view_{user_id}"`
- **Skip:** `callback_data="skip"`
- **Back:** `callback_data="back_menu"`

### Reply Keyboard (Menu)
- Always visible at bottom
- Text-based navigation
- Handled by `handle_menu_buttons()`

## 📝 Adding New Feature Example

### Example: Add "Block User" Feature

**Step 1:** Add to database schema (`database.py`):
```python
cursor.execute('''
    CREATE TABLE IF NOT EXISTS blocks (
        blocker_id INTEGER NOT NULL,
        blocked_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (blocker_id, blocked_id)
    )
''')
```

**Step 2:** Add model function (`models/user_model.py`):
```python
def block_user(blocker_id: int, blocked_id: int) -> bool:
    try:
        with db_manager.transaction() as cursor:
            cursor.execute(
                'INSERT OR IGNORE INTO blocks (blocker_id, blocked_id) VALUES (?, ?)',
                (blocker_id, blocked_id)
            )
        return True
    except Exception as e:
        logger.error(f"Error blocking user: {e}")
        return False
```

**Step 3:** Add button (`handlers/browse_handler.py`):
```python
keyboard = [
    [InlineKeyboardButton("❤️ Like", callback_data=f"like_{uid}"),
     InlineKeyboardButton("❌ Pass", callback_data="pass")],
    [InlineKeyboardButton("🚫 Block", callback_data=f"block_{uid}")]
]
```

**Step 4:** Handle callback (`handlers/browse_handler.py`):
```python
elif data.startswith("block_"):
    blocked_id = int(data.split("_")[1])
    if block_user(user_id, blocked_id):
        await query.answer("🚫 User blocked")
        await show_next_profile(context, query.message.chat_id, user_id)
```

## 🎨 Button Patterns

### Pattern 1: Action with User ID
```python
# Button
InlineKeyboardButton("Action", callback_data=f"action_{user_id}")

# Handler
if data.startswith("action_"):
    target_id = int(data.split("_")[1])
```

### Pattern 2: Simple Action
```python
# Button
InlineKeyboardButton("Action", callback_data="action")

# Handler
elif data == "action":
    # Handle action
```

### Pattern 3: Menu Navigation
```python
# Button
KeyboardButton("Menu Item")

# Handler
if text == "Menu Item":
    await handler_function(update, context)
```

## 📊 Database Query Patterns

### Get User
```python
cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
```

### Get Random User (Excluding Self)
```python
cursor.execute('SELECT * FROM users WHERE user_id != ? ORDER BY RANDOM() LIMIT 1', (exclude_id,))
```

### Check Like
```python
cursor.execute('SELECT * FROM likes WHERE liker_id = ? AND liked_id = ?', (liker_id, liked_id))
```

### Get Matches
```python
cursor.execute('''
    SELECT DISTINCT u.* FROM users u
    WHERE EXISTS (SELECT 1 FROM likes l1 WHERE l1.liker_id = ? AND l1.liked_id = u.user_id)
    AND EXISTS (SELECT 1 FROM likes l2 WHERE l2.liker_id = u.user_id AND l2.liked_id = ?)
''', (user_id, user_id))
```

## 🚀 Handler Registration

**In `bot.py`:**
```python
# Commands
app.add_handler(CommandHandler("command_name", handler_function))

# Callbacks (inline buttons)
app.add_handler(CallbackQueryHandler(callback_handler))

# Messages
app.add_handler(MessageHandler(filters.TEXT, message_handler))
```

## 🔐 Security Best Practices

1. **Rate Limiting:** Already implemented
2. **Input Validation:** All inputs validated
3. **SQL Injection:** Parameterized queries
4. **Error Handling:** Comprehensive try-except
5. **Environment Variables:** Sensitive data in .env

## 📈 Monitoring

- `/health` - Check bot status
- `/admin stats` - View statistics (admin only)
- Logs in `logs/bot.log` or console

---

**Ready to customize! 🎨**

