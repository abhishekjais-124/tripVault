"""
UID (Unique Identifier) generation utilities.
"""
import random
import string


def create_random_uid(size=10, chars=string.digits + string.ascii_uppercase):
    """
    Create a random unique identifier.
    
    Args:
        size (int): Length of the UID (default: 10)
        chars (str): Character set to use (default: digits + uppercase letters)
        
    Returns:
        str: A random UID string
    """
    return ''.join(random.choice(chars) for _ in range(size))
