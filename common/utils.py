import random
import string
import re

def create_random_uid(size=10, chars=string.digits + string.ascii_uppercase):
    return ''.join(random.choice(chars) for _ in range(size))

def validate_phone_number(phone_number):
    return re.match(r'^\d{10}$', phone_number) is not None

def validate_email(email):
    return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email) is not None

def random_avatar():
    num = random.randint(1,7)
    return f"https://bootdey.com/img/Content/avatar/avatar{num}.png"
