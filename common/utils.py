import random
import string

def create_random_uid(size=10, chars=string.digits + string.ascii_uppercase):
    return ''.join(random.choice(chars) for _ in range(size))
