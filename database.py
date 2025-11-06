"""
Database module for managing SQLite database connections and initialization.

This module provides a database connection singleton and handles all
database schema initialization.
"""
import sqlite3
import logging
from pathlib import Path
from typing import Optional, Tuple
from contextlib import contextmanager

from config import DB_PATH
from utils.logger import setup_logger

logger = setup_logger(__name__)


class DatabaseManager:
    """Manages database connections and operations."""
    
    _instance: Optional['DatabaseManager'] = None
    _connection: Optional[sqlite3.Connection] = None
    
    def __new__(cls):
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize database connection."""
        if self._connection is None:
            self._connect()
    
    def _connect(self) -> None:
        """Establish database connection and initialize schema."""
        try:
            # Ensure database directory exists
            DB_PATH.parent.mkdir(parents=True, exist_ok=True)
            
            self._connection = sqlite3.connect(
                str(DB_PATH),
                check_same_thread=False,
                timeout=10.0
            )
            self._connection.row_factory = sqlite3.Row  # Return rows as dict-like objects
            self._init_schema()
            logger.info(f"Database initialized at {DB_PATH}")
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise
    
    def _init_schema(self) -> None:
        """Initialize database schema."""
        try:
            cursor = self._connection.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    age INTEGER NOT NULL,
                    department TEXT NOT NULL,
                    bio TEXT NOT NULL,
                    photo_id TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Likes table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS likes (
                    liker_id INTEGER NOT NULL,
                    liked_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (liker_id, liked_id),
                    FOREIGN KEY (liker_id) REFERENCES users(user_id),
                    FOREIGN KEY (liked_id) REFERENCES users(user_id)
                )
            ''')
            
            # Matches table (for future use)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS matches (
                    user1_id INTEGER NOT NULL,
                    user2_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user1_id, user2_id),
                    FOREIGN KEY (user1_id) REFERENCES users(user_id),
                    FOREIGN KEY (user2_id) REFERENCES users(user_id)
                )
            ''')
            
            # Blocks table (for blocking users)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS blocks (
                    blocker_id INTEGER NOT NULL,
                    blocked_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (blocker_id, blocked_id),
                    FOREIGN KEY (blocker_id) REFERENCES users(user_id),
                    FOREIGN KEY (blocked_id) REFERENCES users(user_id)
                )
            ''')
            
            # Reports table (for reporting users)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reports (
                    reporter_id INTEGER NOT NULL,
                    reported_id INTEGER NOT NULL,
                    reason TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (reporter_id, reported_id),
                    FOREIGN KEY (reporter_id) REFERENCES users(user_id),
                    FOREIGN KEY (reported_id) REFERENCES users(user_id)
                )
            ''')
            
            # Favorites table (for bookmarking profiles)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS favorites (
                    user_id INTEGER NOT NULL,
                    favorite_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, favorite_id),
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    FOREIGN KEY (favorite_id) REFERENCES users(user_id)
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_likes_liker ON likes(liker_id)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_likes_liked ON likes(liked_id)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_blocks_blocker ON blocks(blocker_id)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_reports_reported ON reports(reported_id)
            ''')
            
            self._connection.commit()
            logger.debug("Database schema initialized successfully")
        except sqlite3.Error as e:
            logger.error(f"Schema initialization error: {e}")
            self._connection.rollback()
            raise
    
    @property
    def connection(self) -> sqlite3.Connection:
        """Get database connection."""
        if self._connection is None:
            self._connect()
        return self._connection
    
    @property
    def cursor(self) -> sqlite3.Cursor:
        """Get database cursor."""
        return self.connection.cursor()
    
    @contextmanager
    def transaction(self):
        """Context manager for database transactions."""
        try:
            yield self.cursor
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Transaction error: {e}")
            raise
    
    def close(self) -> None:
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.info("Database connection closed")


# Initialize database manager singleton
db_manager = DatabaseManager()
conn = db_manager.connection
cursor = db_manager.cursor

