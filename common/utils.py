import random
import string
import re
from datetime import datetime, timedelta, timezone

def create_random_uid(size=10, chars=string.digits + string.ascii_uppercase):
    return ''.join(random.choice(chars) for _ in range(size))

def validate_phone_number(phone_number):
    return re.match(r'^\d{10}$', phone_number) is not None

def validate_email(email):
    return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email) is not None

def random_avatar():
    num = random.randint(1,7)
    return f"https://bootdey.com/img/Content/avatar/avatar{num}.png"


def format_time_difference(created_at):
    now = datetime.now(timezone.utc)
    created_at_utc = created_at.astimezone(timezone.utc)

    difference = now - created_at_utc

    seconds = difference.total_seconds()
    minutes = seconds / 60
    hours = minutes / 60
    days = hours / 24

    if seconds < 60:
        return f"{singular_or_plural(seconds, 'seconds')} ago"
    elif minutes < 60:
        return f"{singular_or_plural(minutes, 'minutes')} ago"
    elif hours < 24:
        return f"{singular_or_plural(hours, 'hours')} ago"
    else:
        return f"{singular_or_plural(days, 'days')} ago"


def singular_or_plural(count, unit):
    if int(count) == 1:
        return f"{int(count)} {unit[:-1]}"
    else:
        return f"{int(count)} {unit}"
