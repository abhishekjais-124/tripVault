# TripVault PWA Setup Guide

This document explains the Progressive Web App (PWA) setup for TripVault, enabling installation on iOS and other platforms.

## ✅ Completed Setup

### 1. PWA Files Created

#### **Manifest File** (`/trip/templates/trip/manifest.json`)
- Defines app metadata: name, icons, colors
- start_url: `/tripvault/`
- scope: `/tripvault/`
- display: `standalone` (full-screen app mode)
- Theme color: `#0f172a` (dark blue matching app design)
- Icons: 192x192 and 512x512 PNG files

#### **Service Worker** (`/trip/static/serviceworker.js`)
- Implements offline caching strategy
- Cache-first with network fallback
- Caches key routes: `/tripvault/`, `/tripvault/plan/`, `/tripvault/saved/`
- Caches static assets (icons)
- Handles install, activate, and fetch events

### 2. Icons
Located in `/trip/static/icons/`:
- `icon-192.png` (192x192) - for Android and general use
- `icon-512.png` (512x512) - for high-res displays

### 3. Django Configuration

#### **URL Routes** (Updated in `tripVault/urls.py` and `trip/urls.py`)
```python
# Main routes now under /tripvault/ prefix:
/tripvault/                    # Home page
/tripvault/manifest.json       # PWA manifest
/tripvault/serviceworker.js    # Service worker
/tripvault/user/login/         # Login page
/tripvault/home/               # Trip pages
/tripvault/expense/            # Expense pages
```

#### **Settings** (Updated in `tripVault/settings.py`)
```python
ALLOWED_HOSTS = ['aj124.com', 'www.aj124.com', 'localhost', '127.0.0.1']
LOGIN_REDIRECT_URL = '/tripvault/'
LOGIN_URL = '/tripvault/user/login/'
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'trip' / 'static']
```

#### **Views** (Updated in `trip/views.py`)
- `ManifestView`: Serves manifest.json with `application/json` content type
- `ServiceWorkerView`: Serves serviceworker.js with `application/javascript` content type

### 4. HTML Templates

Updated both `trip/templates/trip/base.html` and `user/templates/user/base.html` with:

```html
<!-- PWA Meta Tags -->
<link rel="manifest" href="/tripvault/manifest.json">
<meta name="theme-color" content="#0f172a">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="TripVault">
<link rel="apple-touch-icon" href="{% static 'icons/icon-192.png' %}">

<!-- Service Worker Registration -->
<script>
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', () => {
            navigator.serviceWorker.register('/tripvault/serviceworker.js')
                .then((registration) => {
                    console.log('ServiceWorker registered: ', registration);
                })
                .catch((error) => {
                    console.log('ServiceWorker registration failed: ', error);
                });
        });
    }
</script>
```

## 🚀 Deployment Steps

### 1. Configure Web Server (Apache/Nginx)

The app must be served at `https://aj124.com/tripvault/`.

#### **For Apache** (with mod_wsgi):
```apache
<VirtualHost *:443>
    ServerName aj124.com
    
    # SSL Configuration
    SSLEngine on
    SSLCertificateFile /path/to/cert.pem
    SSLCertificateKeyFile /path/to/key.pem
    
    # Static files
    Alias /static/ /path/to/tripVault/staticfiles/
    <Directory /path/to/tripVault/staticfiles>
        Require all granted
    </Directory>
    
    # WSGI Configuration
    WSGIDaemonProcess tripvault python-path=/path/to/tripVault python-home=/path/to/tripVault/venv
    WSGIProcessGroup tripvault
    WSGIScriptAlias /tripvault /path/to/tripVault/tripVault/wsgi.py
    
    <Directory /path/to/tripVault/tripVault>
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>
</VirtualHost>
```

#### **For Nginx + Gunicorn**:
```nginx
server {
    listen 443 ssl;
    server_name aj124.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location /static/ {
        alias /path/to/tripVault/staticfiles/;
    }
    
    location /tripvault/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 2. Collect Static Files

Before deploying to production:
```bash
cd /Users/aj/tripVault
python manage.py collectstatic --noinput
```

This copies all static files (including icons and serviceworker.js) to `staticfiles/` directory.

### 3. Production Settings

For production, update `settings.py`:
```python
DEBUG = False
ALLOWED_HOSTS = ['aj124.com', 'www.aj124.com']
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### 4. Verify HTTPS

PWAs **require HTTPS**. Ensure your SSL certificate is valid:
```bash
openssl s_client -connect aj124.com:443 -servername aj124.com
```

## 📱 iOS Installation Instructions (for users)

1. Open Safari on iPhone/iPad
2. Navigate to `https://aj124.com/tripvault`
3. Tap the **Share** button (box with arrow)
4. Scroll down and tap **"Add to Home Screen"**
5. Customize the name if desired, then tap **"Add"**
6. TripVault icon appears on Home Screen
7. Tap icon to launch app in standalone mode (full-screen, no browser UI)

## 🧪 Testing Locally

### Test with Django Development Server:
```bash
python manage.py runserver
# Visit: http://localhost:8000/tripvault/
```

### Test PWA Features:
1. Open Chrome DevTools (F12)
2. Go to **Application** tab
3. Check:
   - **Manifest**: Should show TripVault manifest with icons
   - **Service Workers**: Should show serviceworker.js registered
   - **Cache Storage**: After visiting pages, should show cached resources

### Lighthouse Audit:
1. Open Chrome DevTools
2. Go to **Lighthouse** tab
3. Select **Progressive Web App** category
4. Run audit
5. Should score 100/100 with all PWA checks passing

## 📋 PWA Requirements Checklist

✅ **HTTPS** - Required for service workers and PWA installation  
✅ **Manifest** - `/tripvault/manifest.json` with valid configuration  
✅ **Service Worker** - `/tripvault/serviceworker.js` registered on all pages  
✅ **Icons** - 192x192 and 512x512 PNG icons  
✅ **Start URL** - `/tripvault/` configured in manifest  
✅ **Display Mode** - `standalone` for full-screen experience  
✅ **Theme Color** - `#0f172a` for status bar  
✅ **Apple Meta Tags** - iOS-specific tags for optimal experience  
✅ **Offline Support** - Service worker caches key resources  

## 🔧 Troubleshooting

### Service Worker Not Registering
- Check browser console for errors
- Verify `/tripvault/serviceworker.js` is accessible
- Ensure HTTPS is enabled (service workers won't work over HTTP except localhost)

### Manifest Not Found
- Check `/tripvault/manifest.json` is accessible
- Verify Django is serving the file with `application/json` content type
- Check browser Network tab for 404 errors

### Icons Not Loading
- Run `python manage.py collectstatic`
- Verify icons exist in `/trip/static/icons/`
- Check STATIC_URL and STATICFILES_DIRS in settings.py

### App Not Installable on iOS
- Must use Safari browser (Chrome on iOS doesn't support PWA installation)
- Must be served over HTTPS (not HTTP)
- Manifest must be valid JSON
- Icons must be accessible

### Changes Not Reflecting
- Service worker caches aggressively
- Update CACHE_NAME version in serviceworker.js (e.g., `tripvault-v2`)
- Or clear service workers in browser DevTools
- Hard refresh: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)

## 🎨 Customization

### Update Theme Colors
Edit `trip/templates/trip/manifest.json`:
```json
{
  "theme_color": "#0f172a",
  "background_color": "#0f172a"
}
```

### Update Cached Resources
Edit `trip/static/serviceworker.js`:
```javascript
const urlsToCache = [
  `${BASE_PATH}/`,
  `${BASE_PATH}/plan/`,
  `${BASE_PATH}/saved/`,
  // Add more routes to cache
];
```

### Update Icons
Replace files in `/trip/static/icons/`:
- `icon-192.png` (192x192 pixels)
- `icon-512.png` (512x512 pixels)

Then run `python manage.py collectstatic`.

## 📚 Additional Resources

- [MDN PWA Guide](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps)
- [Web App Manifest Spec](https://www.w3.org/TR/appmanifest/)
- [Service Worker API](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)
- [iOS PWA Support](https://developer.apple.com/documentation/webkit/progressive_web_apps)

---

**Note**: For production deployment, remember to:
1. Set `DEBUG = False` in settings.py
2. Use environment variables for sensitive data
3. Configure proper SSL certificates
4. Run `collectstatic` before deploying
5. Test on actual iOS device for full PWA experience
