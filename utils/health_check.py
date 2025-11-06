"""
Health check utilities for monitoring bot status.
"""
from datetime import datetime
from typing import Dict, Any

from database import db_manager
from utils.logger import setup_logger

logger = setup_logger(__name__)


def health_check() -> Dict[str, Any]:
    """
    Perform comprehensive health check.
    
    Returns:
        Dictionary with health status and metrics
    """
    health_status = {
        'timestamp': datetime.now().isoformat(),
        'status': 'healthy',
        'checks': {}
    }
    
    try:
        # Database connection check
        try:
            cursor = db_manager.cursor
            cursor.execute('SELECT 1')
            health_status['checks']['database'] = {
                'status': 'ok',
                'message': 'Database connection successful'
            }
        except Exception as e:
            health_status['checks']['database'] = {
                'status': 'error',
                'message': f'Database error: {str(e)}'
            }
            health_status['status'] = 'unhealthy'
        
        # Database tables check
        try:
            cursor = db_manager.cursor
            tables = ['users', 'likes', 'matches']
            for table in tables:
                cursor.execute(f'SELECT COUNT(*) FROM {table}')
                count = cursor.fetchone()[0]
                health_status['checks'][f'table_{table}'] = {
                    'status': 'ok',
                    'count': count
                }
        except Exception as e:
            health_status['checks']['tables'] = {
                'status': 'error',
                'message': f'Table check error: {str(e)}'
            }
        
        # Connection pool check
        try:
            conn = db_manager.connection
            if conn:
                health_status['checks']['connection_pool'] = {
                    'status': 'ok',
                    'message': 'Connection pool active'
                }
        except Exception as e:
            health_status['checks']['connection_pool'] = {
                'status': 'error',
                'message': f'Connection pool error: {str(e)}'
            }
            health_status['status'] = 'unhealthy'
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        health_status['status'] = 'error'
        health_status['error'] = str(e)
    
    return health_status


def get_bot_metrics() -> Dict[str, Any]:
    """
    Get bot performance metrics.
    
    Returns:
        Dictionary with metrics
    """
    try:
        cursor = db_manager.cursor
        
        metrics = {
            'total_users': 0,
            'total_likes': 0,
            'total_matches': 0,
            'active_users_24h': 0,
            'avg_likes_per_user': 0,
            'match_rate': 0
        }
        
        cursor.execute('SELECT COUNT(*) FROM users')
        metrics['total_users'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM likes')
        metrics['total_likes'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM matches')
        metrics['total_matches'] = cursor.fetchone()[0]
        
        if metrics['total_users'] > 0:
            metrics['avg_likes_per_user'] = metrics['total_likes'] / metrics['total_users']
        
        if metrics['total_likes'] > 0:
            metrics['match_rate'] = (metrics['total_matches'] / metrics['total_likes']) * 100
        
        return metrics
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        return {}

