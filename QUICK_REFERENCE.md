# Quick Reference Guide - Post-Refactoring

## 🚀 Quick Start

After refactoring, run these commands:

```bash
# Create migration files for new apps
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Run server
python manage.py runserver

# Test admin
# Visit: http://localhost:8000/admin
```

---

## 📁 Where to Find Things

### User Authentication
```
Location: user/
├── Registration    → user/auth_views.py
├── Login           → Django built-in (user/urls.py)
├── Profile         → user/auth_views.py (UserProfileView)
└── URL             → /user/registration/, /user/login/, /user/profile/
```

### Group Management
```
Location: group/
├── Create group    → group/views.py (GroupView.post())
├── List groups     → group/views.py (GroupView.get())
├── Remove user     → group/views.py (UserGroupView.delete())
├── Models          → group/models.py (Group, UserGroupMapping)
└── URL             → /user/groups/, /user/user_group/
```

### Group Requests
```
Location: group_request/
├── Send request    → group_request/views.py (RequestUserView)
├── Accept request  → group_request/views.py (AcceptUserRequestView)
├── Decline request → group_request/views.py (DeclineUserRequestView)
├── Search users    → group_request/views.py (SearchUserView)
├── List requests   → group_request/views.py (GetPendingRequestsView)
├── Models          → group_request/models.py (UserGroupRequest)
└── URL             → /user/groups/request/*, /user/accept/, /user/decline/
```

### Common Utilities
```
Location: common/
├── Validation      → common/validators.py
├── UID generation  → common/uid_generator.py
├── Avatars         → common/avatar.py
├── Time formatting → common/datetime_utils.py
└── Re-exports      → common/utils.py (for backward compatibility)
```

---

## 📖 Import Reference

### User Management
```python
# User model & profile views
from user.models import User
from user.auth_views import UserProfileView, CustomerRegistrationView
from user.utils import get_user_by_uid, validate

# Example
user = User.objects.get(id=1)
found_user = get_user_by_uid("ABC123DEF4")
is_valid = validate(full_name, email, phone)
```

### Group Management
```python
# Group models & views
from group.models import Group, UserGroupMapping
from group.views import GroupView
from group.utils import create_user_group, get_user_groups

# Example
group = create_user_group("My Trip Group", user)
user_groups = get_user_groups(user)
```

### Group Requests
```python
# Request models & views
from group_request.models import UserGroupRequest
from group_request.views import SearchUserView, RequestUserView
from group_request.utils import (
    create_user_request,
    get_user_group_pending_request,
    accept_request
)

# Example
request = create_user_request(sender, receiver, group_id, "Member")
pending = get_user_group_pending_request(user)
success, msg = accept_request(request_obj)
```

### Common Utilities
```python
# New way (recommended for new code)
from common.validators import validate_email, validate_phone_number
from common.uid_generator import create_random_uid
from common.avatar import random_avatar
from common.datetime_utils import format_time_difference

# Old way (still works - backward compatible)
from common import utils
utils.validate_email("test@example.com")
utils.create_random_uid()
```

---

## 🔄 URL Routing Map

### Authentication Routes
| Path | Method | View | Purpose |
|------|--------|------|---------|
| `/user/registration/` | GET/POST | `CustomerRegistrationView` | Register new user |
| `/user/login/` | GET/POST | Django LoginView | User login |
| `/user/logout/` | POST | Django LogoutView | User logout |
| `/user/profile/` | GET/POST | `UserProfileView` | View/edit profile |
| `/user/notifications/` | GET | `NotificationsView` | View pending requests |

### Group Routes
| Path | Method | View | Purpose |
|------|--------|------|---------|
| `/user/groups/` | GET/POST | `GroupView` | List/create groups |
| `/user/user_group/` | DELETE | `UserGroupView` | Remove user from group |

### Request Routes
| Path | Method | View | Purpose |
|------|--------|------|---------|
| `/user/groups/search/` | GET | `SearchUserView` | Search users to invite |
| `/user/groups/request/<uid>/` | POST | `RequestUserView` | Send join request |
| `/user/groups/pending-requests/` | GET | `GetPendingRequestsView` | List pending requests |
| `/user/accept/` | POST | `AcceptUserRequestView` | Accept request |
| `/user/decline/` | POST | `DeclineUserRequestView` | Decline request |

---

## 🗄️ Database Models

### User Model
```python
User
├── auth_user (OneToOne → Django User)
├── uid (unique, 10 chars)
├── username (unique)
├── email
├── phone_number
├── name
├── icon (avatar URL)
├── is_active
└── timestamps
```

### Group Model
```python
Group
├── uid (unique, 10 chars)
├── name
├── created_by (username)
├── users_count
├── is_active
└── timestamps
```

### UserGroupMapping
```python
UserGroupMapping
├── user (FK → User)
├── group (FK → Group)
├── role (Admin, Member, etc.)
├── is_active
└── timestamps
```

### UserGroupRequest
```python
UserGroupRequest
├── sender (FK → User)
├── receiver (FK → User)
├── group (FK → Group)
├── role_requested (Admin, Member, etc.)
├── status (Pending, Accepted, Declined)
└── timestamps
```

---

## 🔍 Common Tasks

### Creating a New Group
```python
from group.utils import create_user_group

group, mapping = create_user_group("My Group", user)
# group: Group instance
# mapping: UserGroupMapping instance (user as ADMIN)
```

### Getting User's Groups
```python
from group.utils import get_user_groups

group_ids = get_user_groups(user)
# Returns: list of group IDs
```

### Searching for Users
```python
from group_request.views import SearchUserView
# Or directly:
from user.utils import search_users_by_username

results = search_users_by_username("john", exclude_ids=[1,2,3])
# Returns: QuerySet of User objects
```

### Sending a Join Request
```python
from group_request.utils import create_user_request

request = create_user_request(sender, receiver, group_id, "Member")
# Creates UserGroupRequest with PENDING status
```

### Accepting a Request
```python
from group_request.utils import accept_request

success, message = accept_request(request_obj)
# Updates status to ACCEPTED
# Creates/reactivates UserGroupMapping
```

### Formatting Time Difference
```python
from common.datetime_utils import format_time_difference

time_str = format_time_difference(datetime_obj)
# Returns: "2 days ago", "5 minutes ago", etc.
```

### Validating Email
```python
from common.validators import validate_email

is_valid = validate_email("test@example.com")
# Returns: True/False
```

---

## ❌ Common Mistakes

### ❌ WRONG: Old import path for Group
```python
from user.models import Group  # ❌ THIS NO LONGER WORKS
```

### ✅ CORRECT: New import path
```python
from group.models import Group  # ✅ USE THIS
```

---

### ❌ WRONG: Using old view name
```python
from user.views import UserProfile  # ❌ OLD NAME

view = UserProfile.as_view()
```

### ✅ CORRECT: Using new view name
```python
from user.auth_views import UserProfileView  # ✅ NEW NAME

view = UserProfileView.as_view()
```

---

### ❌ WRONG: Old requests model name
```python
from user.models import UserGroupRequests  # ❌ OLD (plural)
```

### ✅ CORRECT: New model name
```python
from group_request.models import UserGroupRequest  # ✅ NEW (singular)
```

---

### ❌ WRONG: Getting all pending requests
```python
from user.utils import get_user_group_all_pending_request

pending = get_user_group_all_pending_request(user)  # ❌ OLD LOCATION
```

### ✅ CORRECT: New location
```python
from group_request.utils import get_user_group_all_pending_request

pending = get_user_group_all_pending_request(user)  # ✅ CORRECT
```

---

## 📝 Admin Interface

### Accessing Django Admin
```
URL: http://localhost:8000/admin
```

### Available Models
- **Auth**
  - Users (Django built-in)
  - Groups (Django built-in)
  
- **User App**
  - User (custom user profile)
  
- **Group App**
  - Groups (custom groups)
  - User Group Mappings
  
- **Group Request App**
  - User Group Requests

### Admin Features
- List view with filtering
- Search functionality
- Read-only fields (created_at, updated_at, uid)
- Related model navigation

---

## 🧪 Testing

### Test User Registration
```bash
curl http://localhost:8000/user/registration/
```

### Test Group Creation
```bash
# POST to /user/groups/ with form data
curl -X POST http://localhost:8000/user/groups/ \
  -H "Cookie: sessionid=YOUR_SESSION" \
  -d "groupName=Test Group"
```

### Test Request Sending
```bash
# POST to /user/groups/request/{uid}/ with JSON
curl -X POST http://localhost:8000/user/groups/request/ABC123DEF4/ \
  -H "Content-Type: application/json" \
  -d '{"groupId": 1, "role": "Member"}'
```

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `CODE_ORGANIZATION.md` | Comprehensive architecture guide |
| `REFACTORING_NOTES.md` | Detailed migration information |
| `REFACTORING_SUMMARY.md` | Executive summary of changes |
| `ARCHITECTURE_VISUAL_GUIDE.md` | Visual diagrams and flows |
| `QUICK_REFERENCE.md` | This file! |

---

## 🆘 Troubleshooting

### Issue: ImportError
```
ModuleNotFoundError: No module named 'group'
```
**Solution:** 
- Ensure `INSTALLED_APPS` has `'group'` and `'group_request'`
- Check settings.py

### Issue: Table doesn't exist
```
ProgrammingError: table "group_group" doesn't exist
```
**Solution:**
```bash
python manage.py makemigrations
python manage.py migrate
```

### Issue: View not found
```
AttributeError: module 'user.views' has no attribute 'SearchUser'
```
**Solution:** Check the view location:
- `SearchUserView` is now in `group_request.views`
- Import from: `from group_request.views import SearchUserView`

---

## 🎯 Next Steps

1. **Test all views thoroughly**
2. **Update any custom imports** in your code
3. **Run migrations** if you haven't yet
4. **Check admin interface** for all models
5. **Review documentation** for more details

---

## 📞 Quick Help

- For view locations: Check `QUICK_REFERENCE.md` "Where to Find Things"
- For import paths: Check "Import Reference" section
- For URL routes: Check "URL Routing Map"
- For model structure: Check "Database Models"
- For errors: Check "Troubleshooting"

---

**Happy coding! 🚀**
