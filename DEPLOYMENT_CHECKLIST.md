# TripVault PWA - Deployment Checklist

## Pre-Deployment Tasks

### Local Verification
- [x] PWA files created (manifest, service worker, icons)
- [x] Django configuration updated (settings, URLs)
- [x] Templates updated with PWA meta tags
- [x] Service worker registration script added
- [ ] Run verification script: `python3 verify_pwa_setup.py`
- [ ] Test locally: `python3 manage.py runserver`
- [ ] Check manifest at: http://localhost:8000/tripvault/manifest.json
- [ ] Check service worker at: http://localhost:8000/tripvault/serviceworker.js
- [ ] Verify icons display correctly
- [ ] Test service worker registration in Chrome DevTools

### Code Review
- [ ] Review all URL changes (ensure /tripvault/ prefix)
- [ ] Review login_url paths (should be /tripvault/user/login/)
- [ ] Review static file paths
- [ ] Check for hardcoded URLs in templates
- [ ] Verify manifest.json syntax (valid JSON)
- [ ] Verify serviceworker.js syntax

### Static Files
- [ ] Run: `python3 manage.py collectstatic --noinput`
- [ ] Verify icons copied to staticfiles/icons/
- [ ] Verify serviceworker.js in staticfiles/
- [ ] Check file permissions (readable by web server)

## Production Settings

### settings.py Updates
```python
# Production settings to add/update:

DEBUG = False

ALLOWED_HOSTS = ['aj124.com', 'www.aj124.com']

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Static files
STATIC_ROOT = '/path/to/staticfiles/'
STATIC_URL = '/static/'
```

**Checklist:**
- [ ] Set DEBUG = False
- [ ] Update ALLOWED_HOSTS
- [ ] Add security headers
- [ ] Configure STATIC_ROOT for production path
- [ ] Remove development-only settings

### Environment Variables (Recommended)
- [ ] Move SECRET_KEY to environment variable
- [ ] Move database credentials to environment
- [ ] Move Redis credentials to environment
- [ ] Create .env file (and add to .gitignore)

## Server Configuration

### SSL Certificate
- [ ] Valid SSL certificate installed
- [ ] Certificate not expired
- [ ] Covers both aj124.com and www.aj124.com
- [ ] Test: `openssl s_client -connect aj124.com:443`
- [ ] HTTPS redirects working (HTTP → HTTPS)

### Web Server (Apache/Nginx)

#### Apache Configuration
```apache
- [ ] WSGIDaemonProcess configured
- [ ] WSGIProcessGroup configured
- [ ] WSGIScriptAlias set to /tripvault
- [ ] Static files alias configured
- [ ] SSL configured (port 443)
- [ ] HTTP to HTTPS redirect configured
```

#### Nginx Configuration
```nginx
- [ ] location /tripvault/ block configured
- [ ] location /static/ block configured
- [ ] SSL configured
- [ ] Proxy headers set correctly
- [ ] Upstream to Gunicorn configured
```

### File Permissions
- [ ] Django files readable by web server user
- [ ] Static files readable by web server user
- [ ] Log directory writable by web server user
- [ ] Database file writable (if using SQLite)

## Deployment Steps

### 1. Upload Code
- [ ] Upload Django project to server
- [ ] Verify all files present
- [ ] Check .gitignore (don't upload venv, db, etc.)

### 2. Install Dependencies
```bash
- [ ] Create virtual environment
- [ ] Activate venv
- [ ] pip install -r requirements.txt
- [ ] Install any additional packages
```

### 3. Database Setup
```bash
- [ ] python manage.py makemigrations
- [ ] python manage.py migrate
- [ ] Create superuser if needed
```

### 4. Collect Static Files
```bash
- [ ] python manage.py collectstatic --noinput
- [ ] Verify staticfiles/ directory populated
- [ ] Check icons copied correctly
- [ ] Check serviceworker.js copied
```

### 5. Web Server Configuration
- [ ] Configure Apache/Nginx
- [ ] Reload web server
- [ ] Check error logs for issues
- [ ] Test configuration: `apache2ctl configtest` or `nginx -t`

### 6. Start Application
- [ ] Start Django/Gunicorn process
- [ ] Verify process running: `ps aux | grep gunicorn`
- [ ] Check application logs

## Post-Deployment Testing

### Basic Connectivity
- [ ] Visit: https://aj124.com/tripvault/
- [ ] Home page loads correctly
- [ ] No SSL warnings
- [ ] Static files loading (check DevTools Network tab)
- [ ] Images and icons display

### PWA Verification
- [ ] Visit: https://aj124.com/tripvault/manifest.json
  - [ ] Returns JSON (not 404)
  - [ ] Content-Type: application/json
  - [ ] Valid JSON structure
  - [ ] Icons paths correct

- [ ] Visit: https://aj124.com/tripvault/serviceworker.js
  - [ ] Returns JavaScript (not 404)
  - [ ] Content-Type: application/javascript
  - [ ] No syntax errors

- [ ] Check Icons:
  - [ ] https://aj124.com/static/icons/icon-192.png
  - [ ] https://aj124.com/static/icons/icon-512.png

### Browser DevTools (Chrome)
- [ ] Open DevTools (F12)
- [ ] Application tab → Manifest
  - [ ] Manifest displays correctly
  - [ ] Icons show up
  - [ ] No errors in console
  
- [ ] Application tab → Service Workers
  - [ ] Service worker registers successfully
  - [ ] Status: "activated and running"
  - [ ] Scope: https://aj124.com/tripvault/
  
- [ ] Application tab → Cache Storage
  - [ ] tripvault-v1 cache created
  - [ ] Resources cached after browsing

### Lighthouse Audit
- [ ] Open Chrome DevTools → Lighthouse
- [ ] Select "Progressive Web App"
- [ ] Run audit
- [ ] Score 100/100 (or close)
- [ ] All PWA checks pass:
  - [ ] Installable
  - [ ] Service worker registered
  - [ ] Responds with 200 when offline
  - [ ] Has viewport meta tag
  - [ ] Has apple-touch-icon
  - [ ] Themed address bar

### Functional Testing
- [ ] User can login
- [ ] Login redirects to /tripvault/
- [ ] All navigation links work
- [ ] Forms submit correctly
- [ ] CSRF protection working
- [ ] Session management working

### iOS Testing (Critical for PWA)
**On iPhone/iPad with Safari:**

- [ ] Visit https://aj124.com/tripvault/
- [ ] No certificate warnings
- [ ] Page loads correctly
- [ ] Tap Share button
- [ ] "Add to Home Screen" option appears
- [ ] Tap "Add to Home Screen"
- [ ] Customize name (optional)
- [ ] Tap "Add"
- [ ] Icon appears on Home Screen with correct image
- [ ] Tap icon to launch
- [ ] App opens in standalone mode (no Safari UI)
- [ ] Status bar uses theme color
- [ ] Navigation works within app
- [ ] Can close and reopen app

### Android Testing
**On Android device with Chrome:**

- [ ] Visit https://aj124.com/tripvault/
- [ ] Install banner appears (or ⋮ menu → "Install app")
- [ ] Tap "Install"
- [ ] App installs
- [ ] Icon appears in app drawer
- [ ] Tap icon to launch
- [ ] Opens in standalone mode
- [ ] Navigation works

### Offline Testing
- [ ] Visit several pages while online
- [ ] Enable airplane mode / disconnect WiFi
- [ ] Reload app
- [ ] Previously visited pages should load
- [ ] Service worker serves from cache
- [ ] Check console for cache hits

### Performance Testing
- [ ] Page load speed acceptable
- [ ] Time to interactive < 3 seconds
- [ ] Images optimized
- [ ] No console errors
- [ ] No 404 errors in Network tab

## Monitoring & Maintenance

### Initial Monitoring (First 24 hours)
- [ ] Monitor server logs for errors
- [ ] Check service worker registration rate
- [ ] Monitor for 404s
- [ ] Watch for SSL errors
- [ ] Check cache storage usage

### User Feedback
- [ ] Instruct test users how to install
- [ ] Collect feedback on installation process
- [ ] Check if standalone mode works correctly
- [ ] Verify offline functionality
- [ ] Test on multiple devices/browsers

### Error Tracking
- [ ] Set up error logging/monitoring
- [ ] Monitor Django error logs
- [ ] Monitor web server error logs
- [ ] Check browser console errors
- [ ] Set up alerts for critical errors

## Troubleshooting Guide

### Service Worker Not Registering
- [ ] Check HTTPS is enabled
- [ ] Verify serviceworker.js is accessible
- [ ] Check for JavaScript errors in console
- [ ] Clear browser cache and retry
- [ ] Check service worker scope

### Manifest Not Loading
- [ ] Verify manifest.json URL is correct
- [ ] Check Content-Type header
- [ ] Validate JSON syntax
- [ ] Check file permissions

### Icons Not Displaying
- [ ] Run collectstatic again
- [ ] Verify icon paths in manifest
- [ ] Check static files configuration
- [ ] Verify web server serves /static/

### "Add to Home Screen" Not Available (iOS)
- [ ] Must use Safari (not Chrome on iOS)
- [ ] HTTPS required (not HTTP)
- [ ] Manifest must be valid
- [ ] Icons must be accessible

### App Not Opening in Standalone Mode
- [ ] Check manifest display: "standalone"
- [ ] Verify apple-mobile-web-app-capable meta tag
- [ ] Clear app and reinstall
- [ ] Check start_url in manifest

### Login Redirects to Wrong URL
- [ ] Check LOGIN_URL in settings.py
- [ ] Check LOGIN_REDIRECT_URL
- [ ] Check @login_required decorators
- [ ] Verify all use /tripvault/ prefix

## Rollback Plan

### If Issues Occur
- [ ] Keep backup of previous working version
- [ ] Document rollback steps
- [ ] Test rollback in staging first
- [ ] Have database backup
- [ ] Know how to revert web server config

### Rollback Steps
1. [ ] Stop application
2. [ ] Restore previous code version
3. [ ] Restore database if needed
4. [ ] Restore web server config
5. [ ] Restart application
6. [ ] Verify functionality
7. [ ] Notify users if needed

## Documentation

### User Documentation
- [ ] Create installation guide for users
- [ ] Add "Install App" button on website
- [ ] Create tutorial/help page
- [ ] Document offline capabilities
- [ ] Provide screenshots

### Developer Documentation
- [ ] Document any custom configurations
- [ ] Note any production-specific settings
- [ ] Document deployment process
- [ ] Keep this checklist updated
- [ ] Document common issues and fixes

## Success Criteria

### Must Have (Critical)
- [x] HTTPS working
- [ ] Service worker registers successfully
- [ ] Manifest accessible and valid
- [ ] Icons display correctly
- [ ] Installable on iOS Safari
- [ ] Installable on Android Chrome
- [ ] Standalone mode works
- [ ] Basic offline functionality

### Nice to Have
- [ ] Lighthouse PWA score 100/100
- [ ] Fast page load times
- [ ] Comprehensive offline support
- [ ] Push notifications (future)
- [ ] Background sync (future)

## Sign-Off

- [ ] Development complete
- [ ] Testing complete
- [ ] Documentation complete
- [ ] Security review done
- [ ] Performance acceptable
- [ ] User acceptance testing passed
- [ ] Ready for production

**Deployed by:** _________________  
**Date:** _________________  
**Version:** _________________  
**Sign-off:** _________________  

---

## Quick Commands Reference

```bash
# Verify setup
python3 verify_pwa_setup.py

# Collect static files
python3 manage.py collectstatic --noinput

# Run development server
python3 manage.py runserver

# Check Django for errors
python3 manage.py check

# Test database connection
python3 manage.py dbshell

# View migrations
python3 manage.py showmigrations

# Create superuser
python3 manage.py createsuperuser

# Restart web server (Apache)
sudo systemctl restart apache2

# Restart web server (Nginx)
sudo systemctl restart nginx

# View logs (Apache)
tail -f /var/log/apache2/error.log

# View logs (Nginx)
tail -f /var/log/nginx/error.log

# View Django logs
tail -f logs/errors.log
```

---

**Remember:** 
- Always test in staging before production
- Keep backups before making changes
- Monitor closely after deployment
- Have rollback plan ready

**TripVault PWA is ready to deploy! 🚀**
