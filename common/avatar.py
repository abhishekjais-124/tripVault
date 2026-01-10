"""
User avatar utilities.
"""
import random


def random_avatar():
    """
    Get a random avatar image URL.
    
    Returns:
        str: URL to a random avatar image
    """
    num = random.randint(1, 7)
    return f"https://bootdey.com/img/Content/avatar/avatar{num}.png"
