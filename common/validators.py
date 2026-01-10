"""
Validation utilities for common data types.
"""
import re


def validate_phone_number(phone_number):
    """
    Validate a phone number (must be 10 digits).
    
    Args:
        phone_number (str): Phone number to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    return re.match(r'^\d{10}$', phone_number) is not None


def validate_email(email):
    """
    Validate an email address.
    
    Args:
        email (str): Email to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email) is not None
