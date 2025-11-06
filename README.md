# University Connect Bot

A professional Tinder-style Telegram bot for connecting university students - built with Python and python-telegram-bot.

## 🎯 Features

- ✅ **User Registration** - Complete profile creation with validation
- ✅ **Browse Profiles** - Swipe through student profiles
- ✅ **Like & Match** - Like profiles and get matched when both like each other
- ✅ **Match Notifications** - Get notified when you match
- ✅ **Filter System** - Filter by age and department
- ✅ **Statistics** - View your activity stats
- ✅ **Liked Me** - See who liked your profile
- ✅ **Admin Commands** - Bot management tools
- ✅ **Rate Limiting** - Prevents abuse
- ✅ **Auto Backups** - Automatic database backups
- ✅ **Health Monitoring** - Bot health checks
- ✅ **Professional Architecture** - Clean, modular, scalable code

## Features

- 🔐 **User Registration** - Easy profile creation with validation
- 🔍 **Browse Profiles** - Swipe through student profiles
- ❤️ **Like & Match** - Like profiles and get matched
- 📱 **Menu Navigation** - Intuitive button-based interface
- 📊 **Database Management** - SQLite with proper indexing
- 📝 **Logging** - Comprehensive logging system
- 🛡️ **Error Handling** - Robust error handling throughout

## Project Structure

```
university_connect_bot/
├── bot.py                 # Main entry point
├── config.py              # Configuration management
├── database.py             # Database connection & schema
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore rules
│
├── handlers/              # Bot command handlers
│   ├── __init__.py
│   ├── start_handler.py   # Registration flow
│   ├── browse_handler.py  # Browse & match functionality
│   ├── menu_handler.py    # Menu navigation
│   └── chat_handler.py    # Chat functionality (future)
│
├── models/                # Data models
│   ├── __init__.py
│   └── user_model.py      # User database operations
│
└── utils/                 # Utility functions
    ├── __init__.py
    ├── logger.py          # Logging configuration
    └── validators.py      # Input validation
```

## Installation

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Telegram Bot Token from [@BotFather](https://t.me/BotFather)

### Setup Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/university_connect_bot.git
   cd university_connect_bot
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   
   Copy the example environment file:
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` and add your bot token:
   ```env
   BOT_TOKEN=your_actual_bot_token_here
   DB_PATH=university_connect.db
   LOG_LEVEL=INFO
   ```

4. **Run the bot:**
   ```bash
   python bot.py
   ```

## Configuration

The bot uses environment variables for configuration. Create a `.env` file with the following variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `BOT_TOKEN` | Telegram bot token (required) | - |
| `DB_PATH` | Database file path | `university_connect.db` |
| `LOG_LEVEL` | Logging level (DEBUG/INFO/WARNING/ERROR) | `INFO` |
| `LOG_FILE` | Log file path (optional) | `logs/bot.log` |
| `MIN_AGE` | Minimum allowed age | `16` |
| `MAX_AGE` | Maximum allowed age | `100` |
| `MIN_BIO_LENGTH` | Minimum bio length | `10` |
| `MAX_BIO_LENGTH` | Maximum bio length | `500` |

## Usage

### Commands

- `/start` - Begin registration or view main menu
- `/browse` - Browse through available profiles
- `/menu` - Show/hide the main menu

### User Flow

1. User sends `/start`
2. Bot guides through registration (name, age, department, bio, photo)
3. User receives menu buttons
4. User can browse profiles, view their profile, or access settings

## Development

### Code Quality

- Type hints throughout the codebase
- Comprehensive error handling
- Logging for debugging and monitoring
- Input validation for user data
- Database transactions for data integrity

### Adding New Features

1. Create handler in `handlers/` directory
2. Add database operations in `models/` if needed
3. Register handler in `bot.py`
4. Update documentation

### Database Schema

The bot uses SQLite with the following tables:

- **users**: User profiles
- **likes**: Like relationships
- **matches**: Matched pairs (for future use)

## Logging

Logs are written to:
- Console (stdout)
- File (if `LOG_FILE` is configured)

Log levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`

## Security

- Bot token stored in environment variables (never commit `.env`)
- Input validation on all user inputs
- SQL injection protection via parameterized queries
- Database connection timeout configured

## Troubleshooting

### Bot not responding

1. Check if bot token is correct in `.env`
2. Verify bot is running (`python bot.py`)
3. Check logs for errors

### Database errors

1. Ensure database file permissions are correct
2. Check disk space
3. Review logs for specific errors

### Import errors

1. Ensure all dependencies are installed: `pip install -r requirements.txt`
2. Verify Python version: `python --version` (should be 3.9+)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues and questions, please open an issue on GitHub.

---

Built with ❤️ using Python and python-telegram-bot
