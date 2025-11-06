"""
User model for database operations.

This module provides all functions related to user data management.
"""
from typing import Optional, Tuple
import logging

from database import db_manager
from utils.logger import setup_logger

logger = setup_logger(__name__)


def save_user(
    user_id: int,
    name: str,
    age: int,
    department: str,
    bio: str,
    photo_id: str
) -> bool:
    """
    Save or update user profile in database.
    
    Args:
        user_id: Telegram user ID
        name: User's name
        age: User's age
        department: User's department
        bio: User's bio
        photo_id: Telegram photo file ID
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with db_manager.transaction() as cursor:
            cursor.execute('''
                INSERT OR REPLACE INTO users (user_id, name, age, department, bio, photo_id, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, name, age, department, bio, photo_id))
        
        logger.info(f"User {user_id} profile saved/updated")
        return True
    except Exception as e:
        logger.error(f"Error saving user {user_id}: {e}")
        return False


def get_random_user(exclude_id: int, exclude_blocked: bool = True) -> Optional[Tuple]:
    """
    Get a random user excluding the specified user ID and blocked users.
    
    Args:
        exclude_id: User ID to exclude from results
        exclude_blocked: Whether to exclude blocked users
        
    Returns:
        Tuple of user data or None if not found
    """
    try:
        cursor = db_manager.cursor
        if exclude_blocked:
            # Exclude users blocked by exclude_id
            cursor.execute('''
                SELECT u.* FROM users u
                WHERE u.user_id != ?
                AND NOT EXISTS (
                    SELECT 1 FROM blocks b
                    WHERE b.blocker_id = ? AND b.blocked_id = u.user_id
                )
                ORDER BY RANDOM() LIMIT 1
            ''', (exclude_id, exclude_id))
        else:
            cursor.execute(
                'SELECT * FROM users WHERE user_id != ? ORDER BY RANDOM() LIMIT 1',
                (exclude_id,)
            )
        result = cursor.fetchone()
        if result:
            return tuple(result)
        return None
    except Exception as e:
        logger.error(f"Error getting random user: {e}")
        return None


def add_like(liker_id: int, liked_id: int) -> bool:
    """
    Add a like from one user to another.
    
    Args:
        liker_id: ID of user who likes
        liked_id: ID of user being liked
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with db_manager.transaction() as cursor:
            cursor.execute(
                'INSERT OR IGNORE INTO likes (liker_id, liked_id) VALUES (?, ?)',
                (liker_id, liked_id)
            )
        
        logger.debug(f"User {liker_id} liked user {liked_id}")
        return True
    except Exception as e:
        logger.error(f"Error adding like from {liker_id} to {liked_id}: {e}")
        return False


def check_match(user1_id: int, user2_id: int) -> bool:
    """
    Check if two users have matched (both liked each other).
    
    Args:
        user1_id: First user ID
        user2_id: Second user ID
        
    Returns:
        True if they matched, False otherwise
    """
    try:
        cursor = db_manager.cursor
        cursor.execute(
            'SELECT * FROM likes WHERE liker_id = ? AND liked_id = ?',
            (user2_id, user1_id)
        )
        return cursor.fetchone() is not None
    except Exception as e:
        logger.error(f"Error checking match between {user1_id} and {user2_id}: {e}")
        return False


def user_exists(user_id: int) -> bool:
    """
    Check if a user exists in database.
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        True if user exists, False otherwise
    """
    try:
        cursor = db_manager.cursor
        cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
        return cursor.fetchone() is not None
    except Exception as e:
        logger.error(f"Error checking if user {user_id} exists: {e}")
        return False


def get_user(user_id: int) -> Optional[Tuple]:
    """
    Get user data by user ID.
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        Tuple of user data or None if not found
    """
    try:
        cursor = db_manager.cursor
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        if result:
            return tuple(result)
        return None
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {e}")
        return None


def get_user_matches(user_id: int) -> list[Tuple]:
    """
    Get all matches for a user (users who liked each other).
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        List of matched user tuples
    """
    try:
        cursor = db_manager.cursor
        # Get users where both liked each other
        # User A liked User B AND User B liked User A
        cursor.execute('''
            SELECT DISTINCT u.* FROM users u
            WHERE EXISTS (
                SELECT 1 FROM likes l1 
                WHERE l1.liker_id = ? AND l1.liked_id = u.user_id
            )
            AND EXISTS (
                SELECT 1 FROM likes l2 
                WHERE l2.liker_id = u.user_id AND l2.liked_id = ?
            )
            AND u.user_id != ?
        ''', (user_id, user_id, user_id))
        results = cursor.fetchall()
        return [tuple(row) for row in results] if results else []
    except Exception as e:
        logger.error(f"Error getting matches for user {user_id}: {e}")
        return []


def save_match(user1_id: int, user2_id: int) -> bool:
    """
    Save a match between two users in the matches table.
    
    Args:
        user1_id: First user ID
        user2_id: Second user ID
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with db_manager.transaction() as cursor:
            # Save match in both directions (user1-user2 and user2-user1)
            cursor.execute(
                'INSERT OR IGNORE INTO matches (user1_id, user2_id) VALUES (?, ?)',
                (min(user1_id, user2_id), max(user1_id, user2_id))
            )
        logger.info(f"Match saved between {user1_id} and {user2_id}")
        return True
    except Exception as e:
        logger.error(f"Error saving match: {e}")
        return False


def get_users_who_liked_me(user_id: int) -> list[Tuple]:
    """
    Get users who liked the current user (but haven't matched yet).
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        List of user tuples who liked this user
    """
    try:
        cursor = db_manager.cursor
        # Get users who liked this user, but exclude those who are already matches
        cursor.execute('''
            SELECT DISTINCT u.* FROM users u
            INNER JOIN likes l ON l.liker_id = u.user_id
            WHERE l.liked_id = ?
            AND NOT EXISTS (
                SELECT 1 FROM likes l2 
                WHERE l2.liker_id = ? AND l2.liked_id = u.user_id
            )
            AND u.user_id != ?
        ''', (user_id, user_id, user_id))
        results = cursor.fetchall()
        return [tuple(row) for row in results] if results else []
    except Exception as e:
        logger.error(f"Error getting users who liked {user_id}: {e}")
        return []


def block_user(blocker_id: int, blocked_id: int) -> bool:
    """
    Block a user (hide their profile from blocker).
    
    Args:
        blocker_id: ID of user doing the blocking
        blocked_id: ID of user being blocked
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with db_manager.transaction() as cursor:
            cursor.execute(
                'INSERT OR IGNORE INTO blocks (blocker_id, blocked_id) VALUES (?, ?)',
                (blocker_id, blocked_id)
            )
        logger.info(f"User {blocker_id} blocked user {blocked_id}")
        return True
    except Exception as e:
        logger.error(f"Error blocking user: {e}")
        return False


def is_blocked(blocker_id: int, blocked_id: int) -> bool:
    """
    Check if a user is blocked.
    
    Args:
        blocker_id: ID of potential blocker
        blocked_id: ID of potentially blocked user
        
    Returns:
        True if blocked, False otherwise
    """
    try:
        cursor = db_manager.cursor
        cursor.execute(
            'SELECT * FROM blocks WHERE blocker_id = ? AND blocked_id = ?',
            (blocker_id, blocked_id)
        )
        return cursor.fetchone() is not None
    except Exception as e:
        logger.error(f"Error checking block: {e}")
        return False


def report_user(reporter_id: int, reported_id: int, reason: Optional[str] = None) -> bool:
    """
    Report a user.
    
    Args:
        reporter_id: ID of user reporting
        reported_id: ID of user being reported
        reason: Optional reason for report
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with db_manager.transaction() as cursor:
            cursor.execute(
                'INSERT OR IGNORE INTO reports (reporter_id, reported_id, reason) VALUES (?, ?, ?)',
                (reporter_id, reported_id, reason)
            )
        logger.warning(f"User {reported_id} reported by user {reporter_id}. Reason: {reason}")
        return True
    except Exception as e:
        logger.error(f"Error reporting user: {e}")
        return False


def add_favorite(user_id: int, favorite_id: int) -> bool:
    """
    Add a user to favorites (bookmark).
    
    Args:
        user_id: ID of user adding favorite
        favorite_id: ID of user being favorited
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with db_manager.transaction() as cursor:
            cursor.execute(
                'INSERT OR IGNORE INTO favorites (user_id, favorite_id) VALUES (?, ?)',
                (user_id, favorite_id)
            )
        logger.debug(f"User {user_id} favorited user {favorite_id}")
        return True
    except Exception as e:
        logger.error(f"Error adding favorite: {e}")
        return False


def remove_favorite(user_id: int, favorite_id: int) -> bool:
    """
    Remove a user from favorites.
    
    Args:
        user_id: ID of user removing favorite
        favorite_id: ID of user being unfavorited
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with db_manager.transaction() as cursor:
            cursor.execute(
                'DELETE FROM favorites WHERE user_id = ? AND favorite_id = ?',
                (user_id, favorite_id)
            )
        return True
    except Exception as e:
        logger.error(f"Error removing favorite: {e}")
        return False


def get_favorites(user_id: int) -> list[Tuple]:
    """
    Get all favorite users for a user.
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        List of favorited user tuples
    """
    try:
        cursor = db_manager.cursor
        cursor.execute('''
            SELECT u.* FROM users u
            INNER JOIN favorites f ON f.favorite_id = u.user_id
            WHERE f.user_id = ?
        ''', (user_id,))
        results = cursor.fetchall()
        return [tuple(row) for row in results] if results else []
    except Exception as e:
        logger.error(f"Error getting favorites: {e}")
        return []


def is_favorited(user_id: int, favorite_id: int) -> bool:
    """
    Check if a user is favorited.
    
    Args:
        user_id: ID of user checking
        favorite_id: ID of potentially favorited user
        
    Returns:
        True if favorited, False otherwise
    """
    try:
        cursor = db_manager.cursor
        cursor.execute(
            'SELECT * FROM favorites WHERE user_id = ? AND favorite_id = ?',
            (user_id, favorite_id)
        )
        return cursor.fetchone() is not None
    except Exception as e:
        logger.error(f"Error checking favorite: {e}")
        return False


def get_users_with_filters(
    exclude_id: int,
    min_age: Optional[int] = None,
    max_age: Optional[int] = None,
    department: Optional[str] = None
) -> Optional[Tuple]:
    """
    Get a random user with optional filters.
    
    Args:
        exclude_id: User ID to exclude
        min_age: Minimum age filter
        max_age: Maximum age filter
        department: Department filter
        
    Returns:
        Tuple of user data or None
    """
    try:
        cursor = db_manager.cursor
        query = 'SELECT * FROM users WHERE user_id != ?'
        params = [exclude_id]
        
        if min_age is not None:
            query += ' AND age >= ?'
            params.append(min_age)
        if max_age is not None:
            query += ' AND age <= ?'
            params.append(max_age)
        if department:
            query += ' AND department LIKE ?'
            params.append(f'%{department}%')
        
        query += ' ORDER BY RANDOM() LIMIT 1'
        
        cursor.execute(query, tuple(params))
        result = cursor.fetchone()
        if result:
            return tuple(result)
        return None
    except Exception as e:
        logger.error(f"Error getting filtered user: {e}")
        return None
