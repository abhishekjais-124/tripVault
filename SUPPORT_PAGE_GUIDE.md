# Support Page & Email Setup Guide

## Overview
The Support page is a comprehensive help center that includes:
- **FAQ Section**: Frequently asked questions about using TripVault
- **Contact Form**: Users can submit support requests
- **Support Info Cards**: Display support response time and availability

## Email Integration

### Current Setup
The contact form uses a **dual-layer approach**:
1. **Primary**: emailJS (client-side email service)
2. **Fallback**: Django backend endpoint (if emailJS is not configured)

### emailJS Configuration (Service ID: service_1)

To enable emailJS email sending with your personal email:

#### Step 1: Create emailJS Account
1. Visit [emailjs.com](https://www.emailjs.com)
2. Sign up for a free account
3. Note your **User ID** (found in account settings)

#### Step 2: Add Email Service
1. Go to "Email Services" in the dashboard
2. Choose your email provider (Gmail, Outlook, etc.)
3. Follow the provider-specific setup (may require app password)
4. Name the service: `service_1` (or note the actual service ID)

#### Step 3: Create Email Template
1. Go to "Email Templates"
2. Create a new template named: `template_contact`
3. Configure the template:

**Template Variables:**
```
- from_name: {{from_name}}
- from_email: {{from_email}}
- subject: {{subject}}
- message: {{message}}
- to_email: {{to_email}}
```

**Template Content Example:**
```
From: {{from_name}} <{{from_email}}>
Subject: {{subject}}

Message:
{{message}}

---
This message was sent from the TripVault Support Form
```

4. Set the **To Email** to: `{{to_email}}` (which will be support@tripvault.com)
5. Update **Email Subject** to: `[TripVault Support] {{subject}}`

#### Step 4: Update Code
Update the initialization in [user/templates/user/support.html](user/templates/user/support.html):
```javascript
emailjs.init('YOUR_PUBLIC_KEY');  // Get from emailJS dashboard
```

### Backend Fallback
If emailJS template is not configured:
- The form automatically falls back to a Django endpoint
- The endpoint is located at `/user/support/send-email/`
- Currently logs the contact request (Django email sending is commented out)

**To enable Django email sending:**
1. Configure `EMAIL_BACKEND` in [tripVault/settings.py](tripVault/settings.py)
2. Uncomment the `send_mail()` code in [SendContactEmailView](user/auth_views.py)
3. Set `DEFAULT_FROM_EMAIL` in settings.py

### Features

#### FAQ Section
- **Interactive toggle** - Click to expand/collapse answers
- **5 Common questions** about:
  - Creating groups
  - Adding expenses
  - Balance calculation
  - Friends feature
  - Group invitations

#### Contact Form
- **Required Fields**: Name, Email, Subject, Message
- **Form Validation**: Client-side validation before submission
- **Status Messages**: Success/error feedback with visual indicators
- **Loading State**: Button shows "Sending..." while processing
- **Auto-dismiss**: Success message hides after 5 seconds

#### Responsive Design
- Works on desktop and mobile devices
- Grid layout adapts to screen size
- Mobile-friendly form inputs

## File Structure

```
user/
├── auth_views.py              # SupportView, SendContactEmailView
├── urls.py                    # support routes
└── templates/user/
    └── support.html           # Support page template
common/
└── templates/common/
    └── navbar.html            # Support link in navigation
```

## Testing

### Local Testing
1. Start Django development server
2. Navigate to http://localhost:8000/user/support/
3. Test FAQ toggles - click questions to expand/collapse
4. Test contact form:
   - Fill in all fields
   - Click "Send Message"
   - If emailJS is not configured, form will use Django backend
   - Should see success message

### Production Deployment
1. Configure emailJS with your Service ID and template
2. Update User ID in support.html
3. Or configure Django email backend in settings.py
4. Test form submission

## Navigation
Support is accessible from:
- **Desktop navbar** - "Support" link in main menu
- **Mobile navbar** - "Support" link in mobile menu
- **URL**: `/user/support/`

## Customization

### Adding More FAQ Items
Edit the FAQ section in [support.html](user/templates/user/support.html):
```html
<div class="border-b border-gray-700 pb-4">
    <button class="faq-toggle w-full text-left..." onclick="toggleFAQ(this)">
        <span>Your Question?</span>
        <i class="fas fa-chevron-down..."></i>
    </button>
    <p class="faq-content hidden text-gray-400 mt-3">
        Your answer here.
    </p>
</div>
```

### Changing Contact Email
Update the `to_email` in the contact form script in support.html:
```javascript
to_email: 'your-email@example.com'
```

## Styling
The page uses:
- **Tailwind CSS** for layout and responsive design
- **Gradient backgrounds** for visual appeal
- **Glass-morphism effect** for glass-like panels
- **Smooth transitions** for interactive elements
- **Font Awesome icons** for visual elements

## Accessibility
- Proper semantic HTML
- Keyboard navigation support
- Clear focus states
- ARIA labels where appropriate

## Security
- CSRF protection on backend form endpoint
- JSON validation on server-side
- No sensitive data exposed in client-side code
- Email address validation before processing
