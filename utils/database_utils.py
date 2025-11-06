"""
Database utility functions for maintenance and backup.
"""
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional

from config import DB_PATH
from database import db_manager
from utils.logger import setup_logger

logger = setup_logger(__name__)


def backup_database(backup_dir: Path = Path("backups")) -> Optional[Path]:
    """
    Create a backup of the database.
    
    Args:
        backup_dir: Directory to save backup
        
    Returns:
        Path to backup file or None if failed
    """
    try:
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"university_connect_{timestamp}.db"
        
        shutil.copy2(DB_PATH, backup_path)
        logger.info(f"Database backed up to {backup_path}")
        return backup_path
    except Exception as e:
        logger.error(f"Error backing up database: {e}")
        return None


def optimize_database() -> bool:
    """
    Optimize database (VACUUM and ANALYZE).
    
    Returns:
        True if successful, False otherwise
    """
    try:
        cursor = db_manager.cursor
        cursor.execute('VACUUM')
        cursor.execute('ANALYZE')
        db_manager.connection.commit()
        logger.info("Database optimized successfully")
        return True
    except Exception as e:
        logger.error(f"Error optimizing database: {e}")
        return False


def get_database_size() -> int:
    """
    Get database file size in bytes.
    
    Returns:
        File size in bytes
    """
    try:
        if DB_PATH.exists():
            return DB_PATH.stat().st_size
        return 0
    except Exception as e:
        logger.error(f"Error getting database size: {e}")
        return 0


def cleanup_old_backups(backup_dir: Path = Path("backups"), keep_days: int = 7) -> int:
    """
    Clean up old backup files.
    
    Args:
        backup_dir: Directory with backups
        keep_days: Number of days to keep backups
        
    Returns:
        Number of files deleted
    """
    try:
        if not backup_dir.exists():
            return 0
        
        cutoff_time = datetime.now().timestamp() - (keep_days * 24 * 60 * 60)
        deleted = 0
        
        for backup_file in backup_dir.glob("*.db"):
            if backup_file.stat().st_mtime < cutoff_time:
                backup_file.unlink()
                deleted += 1
                logger.debug(f"Deleted old backup: {backup_file}")
        
        logger.info(f"Cleaned up {deleted} old backups")
        return deleted
    except Exception as e:
        logger.error(f"Error cleaning up backups: {e}")
        return 0

