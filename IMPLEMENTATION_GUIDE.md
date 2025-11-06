# 🎯 Complete Tinder-Style Telegram Bot Implementation Guide

## 📁 Full Project Structure

```
university_connect_bot/
│
├── bot.py                      # Main entry point - runs the bot
├── config.py                   # Configuration (tokens, settings)
├── database.py                 # Database connection & schema
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
│
├── handlers/                   # Command and message handlers
│   ├── __init__.py
│   ├── start_handler.py        # Registration flow (/start)
│   ├── browse_handler.py       # Browse profiles & like/pass
│   ├── menu_handler.py         # Main menu & navigation
│   ├── matches_handler.py      # View matches
│   ├── liked_me_handler.py    # View who liked you
│   ├── preferences_handler.py  # Filter settings
│   └── admin_handler.py        # Admin commands
│
├── models/                     # Data models
│   ├── __init__.py
│   └── user_model.py           # User database operations
│
└── utils/                      # Utility functions
    ├── __init__.py
    ├── logger.py               # Logging configuration
    ├── validators.py           # Input validation
    ├── rate_limiter.py         # Rate limiting
    ├── health_check.py         # Health monitoring
    ├── database_utils.py       # Database utilities
    └── scheduler.py            # Background tasks
```

## 🚀 Quick Start

### 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file (optional)
cp env.example .env
# Edit .env and add your BOT_TOKEN
```

### 2. Run the Bot

```bash
python bot.py
```

## 📝 Code Structure Explanation

### 1. Main Entry Point (`bot.py`)

**Purpose:** Initializes and runs the bot with all handlers.

**Key Features:**
- Application setup with token
- Handler registration
- Error handling
- Graceful shutdown
- Health checks
- Background scheduler

**Handler Registration Order:**
1. Commands (start, browse, menu, admin, health)
2. Callback queries (inline buttons)
3. Message handlers (registration, menu buttons)
4. Error handler

### 2. Database Layer (`database.py`)

**Purpose:** Manages SQLite database connections and schema.

**Features:**
- Singleton pattern for connection management
- Transaction support
- Automatic schema initialization
- Connection pooling
- Error handling

**Tables:**
- `users` - User profiles
- `likes` - Like relationships
- `matches` - Matched pairs

### 3. Handlers (`handlers/`)

Each handler manages specific functionality:

#### `start_handler.py`
- `/start` command
- Multi-step registration flow
- Input validation
- Profile creation

#### `browse_handler.py`
- `/browse` command
- Profile display with inline buttons
- Like/Pass actions
- Match detection
- View profile functionality

#### `menu_handler.py`
- Main menu display
- Reply keyboard buttons
- Statistics display
- Help information

#### `matches_handler.py`
- Display all matches
- View match profiles

#### `liked_me_handler.py`
- Show users who liked you
- Like back functionality

#### `preferences_handler.py`
- Filter settings
- Age/department filters
- Apply filters

## 🔘 Button Implementation

### Inline Buttons (CallbackQueryHandler)

**Location:** `handlers/browse_handler.py`

**Example:**
```python
keyboard = [
    [
        InlineKeyboardButton("❤️ Like", callback_data=f"like_{uid}"),
        InlineKeyboardButton("❌ Pass", callback_data="pass")
    ],
    [
        InlineKeyboardButton("👤 View Full Profile", callback_data=f"view_{uid}"),
        InlineKeyboardButton("🔄 Skip", callback_data="skip")
    ],
    [
        InlineKeyboardButton("🔙 Back to Menu", callback_data="back_menu")
    ]
]
reply_markup = InlineKeyboardMarkup(keyboard)
```

**Handler:**
```python
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Acknowledge callback
    data = query.data
    
    if data.startswith("like_"):
        liked_id = int(data.split("_")[1])
        # Handle like action
    elif data == "pass":
        # Handle pass action
```

### Reply Keyboard Buttons (Menu)

**Location:** `handlers/menu_handler.py`

**Example:**
```python
keyboard = [
    [KeyboardButton("🔍 Browse Profiles"), KeyboardButton("👤 My Profile")],
    [KeyboardButton("💕 My Matches"), KeyboardButton("💌 Liked Me")],
    [KeyboardButton("📊 Statistics"), KeyboardButton("⚙️ Settings")],
    [KeyboardButton("ℹ️ Help")]
]
return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
```

**Handler:**
```python
async def handle_menu_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "🔍 Browse Profiles":
        await browse(update, context)
    elif text == "👤 My Profile":
        await show_profile(update, context)
    # ... etc
```

## 🎨 Adding New Buttons

### Adding a New Inline Button

1. **Add button to keyboard:**
```python
keyboard = [
    [InlineKeyboardButton("🆕 New Action", callback_data="new_action")]
]
```

2. **Handle in callback handler:**
```python
async def handle_callback(update, context):
    if data == "new_action":
        await query.answer("Action executed!")
        # Your action code here
```

### Adding a New Menu Button

1. **Add to menu keyboard:**
```python
keyboard = [
    [KeyboardButton("🆕 New Feature")],
    # ... existing buttons
]
```

2. **Add handler:**
```python
async def handle_menu_buttons(update, context):
    if text == "🆕 New Feature":
        await new_feature_handler(update, context)
```

3. **Register handler in `bot.py`:**
```python
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu_buttons))
```

## 📚 Complete Code Examples

### Example 1: Adding a "Report User" Button

**Step 1:** Add button to browse handler:
```python
# In handlers/browse_handler.py
keyboard = [
    [InlineKeyboardButton("❤️ Like", callback_data=f"like_{uid}"),
     InlineKeyboardButton("❌ Pass", callback_data="pass")],
    [InlineKeyboardButton("🚫 Report", callback_data=f"report_{uid}")]
]
```

**Step 2:** Handle in callback:
```python
async def handle_callback(update, context):
    if data.startswith("report_"):
        reported_id = int(data.split("_")[1])
        await query.answer("🚫 User reported")
        # Save report to database
        # Notify admins
```

### Example 2: Adding a "Super Like" Feature

**Step 1:** Add to database:
```python
# In database.py
cursor.execute('''
    CREATE TABLE IF NOT EXISTS super_likes (
        liker_id INTEGER,
        liked_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (liker_id, liked_id)
    )
''')
```

**Step 2:** Add button:
```python
keyboard = [
    [InlineKeyboardButton("⭐ Super Like", callback_data=f"super_like_{uid}"),
     InlineKeyboardButton("❤️ Like", callback_data=f"like_{uid}")]
]
```

**Step 3:** Handle action:
```python
if data.startswith("super_like_"):
    liked_id = int(data.split("_")[2])
    # Save super like
    # Show special notification
```

## 🔧 Command Usage Examples

### User Commands

```
/start          - Register or edit profile
/browse         - Browse profiles
/menu           - Show main menu
/health         - Check bot health (public)
```

### Admin Commands

```
/admin stats    - Bot statistics
/admin users    - User count
/admin user <id> - User information
/admin reset <id> - Reset rate limit
```

## 💡 Key Implementation Patterns

### 1. Callback Data Pattern

**Format:** `action_userid` or `action`

**Examples:**
- `like_123456` - Like user with ID 123456
- `view_123456` - View user with ID 123456
- `pass` - Pass current profile

**Parsing:**
```python
if data.startswith("like_"):
    user_id = int(data.split("_")[1])
```

### 2. Multi-Step Registration

**Pattern:** Use `context.user_data` to track steps

```python
context.user_data['step'] = 'name'
context.user_data['step'] = 'age'
# ... etc
```

### 3. Match Detection

**Logic:**
```python
# User A likes User B
add_like(user_a, user_b)

# Check if User B already liked User A
if check_match(user_a, user_b):
    # It's a match!
    save_match(user_a, user_b)
```

## 🎯 Professional Features Included

✅ **Rate Limiting** - Prevents abuse
✅ **Error Handling** - Comprehensive error management
✅ **Logging** - Structured logging system
✅ **Health Checks** - Bot monitoring
✅ **Database Backups** - Automatic backups
✅ **Admin Commands** - Management tools
✅ **Input Validation** - Data validation
✅ **Type Hints** - Code documentation
✅ **Background Tasks** - Scheduled maintenance
✅ **Security** - Environment variables, rate limiting

## 📖 Complete Workflow

### User Registration Flow

1. User sends `/start`
2. Bot asks for name → user enters name
3. Bot asks for age → user enters age
4. Bot asks for department → user enters department
5. Bot asks for bio → user enters bio
6. Bot asks for photo → user sends photo
7. Profile saved → menu buttons appear

### Browsing Flow

1. User clicks "🔍 Browse Profiles"
2. Bot shows random profile with buttons
3. User clicks "❤️ Like" or "❌ Pass"
4. If like:
   - Check for match
   - If match: notify both users
   - Show next profile
5. If pass: show next profile

### Match Flow

1. User A likes User B
2. User B likes User A
3. System detects match
4. Both users notified
5. Match saved to database
6. Users can view matches in "💕 My Matches"

## 🛠️ Customization Guide

### Changing Button Layout

**Edit:** `handlers/menu_handler.py` → `get_main_menu()`

### Adding New Filters

**Edit:** `handlers/preferences_handler.py` → `get_preferences_menu()`

### Modifying Registration Steps

**Edit:** `handlers/start_handler.py` → `handle_registration()`

### Customizing Messages

**Edit:** Each handler file contains message text

## 📊 Database Schema

```sql
-- Users table
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    age INTEGER NOT NULL,
    department TEXT NOT NULL,
    bio TEXT NOT NULL,
    photo_id TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Likes table
CREATE TABLE likes (
    liker_id INTEGER NOT NULL,
    liked_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (liker_id, liked_id)
);

-- Matches table
CREATE TABLE matches (
    user1_id INTEGER NOT NULL,
    user2_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user1_id, user2_id)
);
```

## 🚨 Error Handling

All handlers include:
- Try-except blocks
- User-friendly error messages
- Logging for debugging
- Graceful degradation

## 📈 Performance Optimizations

- Database indexes on frequently queried columns
- Connection pooling
- Rate limiting
- Efficient queries
- Background task scheduling

---

**Your bot is production-ready! 🎉**

All code is fully functional and can be run directly. The implementation follows professional Python development practices with proper error handling, logging, and documentation.

