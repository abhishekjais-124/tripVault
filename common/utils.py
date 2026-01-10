"""
Common utilities module - re-exports from specialized modules for convenience.

New code should import directly from the specialized modules:
- common.validators for validation functions
- common.uid_generator for UID generation
- common.avatar for avatar utilities
- common.datetime_utils for datetime formatting
"""

# Re-export for backward compatibility
from .validators import validate_phone_number, validate_email
from .uid_generator import create_random_uid
from .avatar import random_avatar
from .datetime_utils import format_time_difference

__all__ = [
    'validate_phone_number',
    'validate_email',
    'create_random_uid',
    'random_avatar',
    'format_time_difference',
]
