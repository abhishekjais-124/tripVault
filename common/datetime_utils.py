"""
Date/time formatting utilities.
"""
from datetime import datetime, timezone


def format_time_difference(created_at):
    """
    Format the time difference between now and a given datetime.
    
    Args:
        created_at (datetime): The datetime to compare against now
        
    Returns:
        str: Human-readable time difference (e.g., "2 days ago")
    """
    now = datetime.now(timezone.utc)
    created_at_utc = created_at.astimezone(timezone.utc)

    difference = now - created_at_utc

    seconds = difference.total_seconds()
    minutes = seconds / 60
    hours = minutes / 60
    days = hours / 24

    if seconds < 60:
        return f"{_singular_or_plural(seconds, 'seconds')} ago"
    elif minutes < 60:
        return f"{_singular_or_plural(minutes, 'minutes')} ago"
    elif hours < 24:
        return f"{_singular_or_plural(hours, 'hours')} ago"
    else:
        return f"{_singular_or_plural(days, 'days')} ago"


def _singular_or_plural(count, unit):
    """
    Convert a count to singular or plural form.
    
    Args:
        count (float): The count
        unit (str): The unit name (plural form)
        
    Returns:
        str: Formatted count with correct singular/plural form
    """
    if int(count) == 1:
        return f"{int(count)} {unit[:-1]}"
    else:
        return f"{int(count)} {unit}"
