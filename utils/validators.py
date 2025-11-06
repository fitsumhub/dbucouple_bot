"""Validation functions for user input."""
from typing import Optional


def validate_age(age_str: str) -> tuple[bool, Optional[int]]:
    """
    Validate age input.
    
    Args:
        age_str: Age as string
        
    Returns:
        Tuple of (is_valid, age_int or None)
    """
    try:
        age = int(age_str.strip())
        if 16 <= age <= 100:
            return True, age
        return False, None
    except (ValueError, AttributeError):
        return False, None


def validate_text_length(text: str, min_length: int = 1, max_length: int = 500) -> bool:
    """
    Validate text length.
    
    Args:
        text: Text to validate
        min_length: Minimum length
        max_length: Maximum length
        
    Returns:
        True if valid, False otherwise
    """
    if not text or not isinstance(text, str):
        return False
    return min_length <= len(text.strip()) <= max_length


def validate_name(name: str) -> bool:
    """
    Validate name input.
    
    Args:
        name: Name to validate
        
    Returns:
        True if valid, False otherwise
    """
    return validate_text_length(name, min_length=2, max_length=50)


def validate_bio(bio: str) -> bool:
    """
    Validate bio input.
    
    Args:
        bio: Bio to validate
        
    Returns:
        True if valid, False otherwise
    """
    return validate_text_length(bio, min_length=10, max_length=500)


def validate_department(dept: str) -> bool:
    """
    Validate department input.
    
    Args:
        dept: Department to validate
        
    Returns:
        True if valid, False otherwise
    """
    return validate_text_length(dept, min_length=2, max_length=100)

