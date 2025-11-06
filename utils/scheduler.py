"""
Background task scheduler for periodic maintenance tasks.
"""
import asyncio
from datetime import datetime, timedelta
from typing import Optional

from utils.logger import setup_logger
from utils.database_utils import backup_database, optimize_database, cleanup_old_backups
from utils.health_check import health_check, get_bot_metrics
from config import BACKUP_ENABLED, BACKUP_INTERVAL_HOURS, BACKUP_RETENTION_DAYS

logger = setup_logger(__name__)


class TaskScheduler:
    """Scheduler for periodic background tasks."""
    
    def __init__(self):
        self.running = False
        self._tasks: list = []
        self._last_backup: Optional[datetime] = None
    
    async def start(self) -> None:
        """Start the scheduler."""
        if self.running:
            return
        
        self.running = True
        logger.info("Task scheduler started")
        
        # Start background tasks
        self._tasks.append(asyncio.create_task(self._backup_loop()))
        self._tasks.append(asyncio.create_task(self._health_monitor_loop()))
        self._tasks.append(asyncio.create_task(self._optimization_loop()))
    
    async def stop(self) -> None:
        """Stop the scheduler."""
        self.running = False
        for task in self._tasks:
            task.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)
        logger.info("Task scheduler stopped")
    
    async def _backup_loop(self) -> None:
        """Periodic backup task."""
        while self.running:
            try:
                if BACKUP_ENABLED:
                    if (self._last_backup is None or 
                        datetime.now() - self._last_backup >= timedelta(hours=BACKUP_INTERVAL_HOURS)):
                        backup_path = backup_database()
                        if backup_path:
                            self._last_backup = datetime.now()
                            logger.info(f"Scheduled backup completed: {backup_path}")
                        cleanup_old_backups(keep_days=BACKUP_RETENTION_DAYS)
                
                # Wait for next interval
                await asyncio.sleep(BACKUP_INTERVAL_HOURS * 3600)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in backup loop: {e}")
                await asyncio.sleep(3600)  # Wait 1 hour before retry
    
    async def _health_monitor_loop(self) -> None:
        """Periodic health monitoring."""
        while self.running:
            try:
                health = health_check()
                if health['status'] != 'healthy':
                    logger.warning(f"Health check failed: {health}")
                
                # Log metrics every hour
                metrics = get_bot_metrics()
                logger.info(
                    f"Bot metrics - Users: {metrics.get('total_users', 0)}, "
                    f"Likes: {metrics.get('total_likes', 0)}, "
                    f"Matches: {metrics.get('total_matches', 0)}"
                )
                
                await asyncio.sleep(3600)  # Check every hour
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health monitor loop: {e}")
                await asyncio.sleep(3600)
    
    async def _optimization_loop(self) -> None:
        """Periodic database optimization."""
        while self.running:
            try:
                # Optimize database daily
                await asyncio.sleep(24 * 3600)  # Wait 24 hours
                if self.running:
                    optimize_database()
                    logger.info("Scheduled database optimization completed")
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in optimization loop: {e}")


# Global scheduler instance
scheduler = TaskScheduler()

