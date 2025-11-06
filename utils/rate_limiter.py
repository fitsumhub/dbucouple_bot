"""
Rate limiting utilities to prevent abuse and spam.
"""
from collections import defaultdict
from time import time
from typing import Dict, Tuple
from utils.logger import setup_logger

logger = setup_logger(__name__)


class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self):
        self._requests: Dict[int, list] = defaultdict(list)
        self._banned: Dict[int, float] = {}
    
    def is_allowed(
        self, 
        user_id: int, 
        max_requests: int = 10, 
        time_window: int = 60,
        ban_duration: int = 300
    ) -> Tuple[bool, str]:
        """
        Check if user is allowed to make a request.
        
        Args:
            user_id: User ID to check
            max_requests: Maximum requests allowed in time window
            time_window: Time window in seconds
            ban_duration: Ban duration in seconds if limit exceeded
            
        Returns:
            Tuple of (is_allowed, reason)
        """
        now = time()
        
        # Check if user is banned
        if user_id in self._banned:
            if now < self._banned[user_id]:
                remaining = int(self._banned[user_id] - now)
                return False, f"Rate limit exceeded. Try again in {remaining} seconds."
            else:
                # Ban expired
                del self._banned[user_id]
        
        # Clean old requests outside time window
        cutoff = now - time_window
        self._requests[user_id] = [
            req_time for req_time in self._requests[user_id] 
            if req_time > cutoff
        ]
        
        # Check if limit exceeded
        if len(self._requests[user_id]) >= max_requests:
            self._banned[user_id] = now + ban_duration
            logger.warning(f"User {user_id} rate limited. Banned for {ban_duration}s")
            return False, f"Too many requests. Please wait {ban_duration} seconds."
        
        # Record request
        self._requests[user_id].append(now)
        return True, ""
    
    def reset(self, user_id: int) -> None:
        """Reset rate limit for a user."""
        if user_id in self._requests:
            del self._requests[user_id]
        if user_id in self._banned:
            del self._banned[user_id]
    
    def get_stats(self, user_id: int) -> Dict:
        """Get rate limit stats for a user."""
        now = time()
        cutoff = now - 60
        recent_requests = [
            req_time for req_time in self._requests.get(user_id, [])
            if req_time > cutoff
        ]
        
        return {
            'requests_last_minute': len(recent_requests),
            'is_banned': user_id in self._banned and now < self._banned[user_id],
            'ban_remaining': int(self._banned[user_id] - now) if user_id in self._banned and now < self._banned[user_id] else 0
        }


# Global rate limiter instance
rate_limiter = RateLimiter()

