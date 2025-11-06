"""
Configuration module for the University Connect Bot.

Loads configuration from environment variables with fallback to defaults.
"""
import logging
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Bot Configuration
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "8367540809:AAHZpsEhSsc1HdF2hXycC7qXC8i2fYNKpnQ")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is required!")

# Database Configuration
DB_PATH: Path = Path(os.getenv("DB_PATH", "university_connect.db"))

# Logging Configuration
LOG_LEVEL_STR: str = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_LEVEL: int = getattr(logging, LOG_LEVEL_STR, logging.INFO)
LOG_FILE: Optional[Path] = Path(os.getenv("LOG_FILE", "logs/bot.log")) if os.getenv("LOG_FILE") else None

# Bot Settings
MAX_BIO_LENGTH: int = int(os.getenv("MAX_BIO_LENGTH", "500"))
MIN_BIO_LENGTH: int = int(os.getenv("MIN_BIO_LENGTH", "10"))
MIN_AGE: int = int(os.getenv("MIN_AGE", "16"))
MAX_AGE: int = int(os.getenv("MAX_AGE", "100"))

# Rate Limiting
RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "10"))
RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
RATE_LIMIT_BAN_DURATION: int = int(os.getenv("RATE_LIMIT_BAN_DURATION", "300"))

# Admin Settings
ADMIN_IDS: list[int] = [
    int(uid) for uid in os.getenv("ADMIN_IDS", "").split(",") 
    if uid.strip().isdigit()
]

# Backup Settings
BACKUP_ENABLED: bool = os.getenv("BACKUP_ENABLED", "true").lower() == "true"
BACKUP_INTERVAL_HOURS: int = int(os.getenv("BACKUP_INTERVAL_HOURS", "24"))
BACKUP_RETENTION_DAYS: int = int(os.getenv("BACKUP_RETENTION_DAYS", "7"))

