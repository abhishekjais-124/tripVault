ADMIN = 'Admin'
MEMBER = 'Member'

ROLE_CHOICES = [(ADMIN, 'Admin'), (MEMBER, 'Member')]

PENDING = 0
ACCEPTED = 1
DECLINED = 2

REQUEST_CHOICES = [(PENDING, 'PENDING'), (ACCEPTED, 'ACCEPTED'), (DECLINED, 'DECLINED')]

SHOW_PENDING_REQUEST_REDIS_KEY = "SHOW_PENDING_REQUEST_REDIS_KEY_{}"