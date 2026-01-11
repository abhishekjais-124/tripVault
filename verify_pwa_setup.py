#!/usr/bin/env python3
"""
PWA Setup Verification Script for TripVault
Run this to verify all PWA components are in place.
"""

import os
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def check_file_exists(file_path, description):
    """Check if a file exists and print result."""
    full_path = BASE_DIR / file_path
    exists = full_path.exists()
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {file_path}")
    return exists

def check_manifest_content():
    """Verify manifest.json has correct structure."""
    manifest_path = BASE_DIR / "trip/templates/trip/manifest.json"
    try:
        with open(manifest_path, 'r') as f:
            data = json.load(f)
        
        required_fields = ['name', 'short_name', 'start_url', 'scope', 'display', 
                          'theme_color', 'background_color', 'icons']
        
        all_present = all(field in data for field in required_fields)
        status = "✅" if all_present else "❌"
        print(f"{status} Manifest has all required fields")
        
        if data.get('start_url') == '/tripvault/' and data.get('scope') == '/tripvault/':
            print(f"✅ Manifest paths correctly set to /tripvault/")
        else:
            print(f"❌ Manifest paths need to be /tripvault/")
            
        return all_present
    except Exception as e:
        print(f"❌ Error reading manifest: {e}")
        return False

def check_service_worker_content():
    """Verify serviceworker.js has required event listeners."""
    sw_path = BASE_DIR / "trip/static/serviceworker.js"
    try:
        with open(sw_path, 'r') as f:
            content = f.read()
        
        required_events = ['install', 'activate', 'fetch']
        all_present = all(f"addEventListener('{event}'" in content for event in required_events)
        
        status = "✅" if all_present else "❌"
        print(f"{status} Service worker has all required event listeners")
        
        has_tripvault = '/tripvault' in content
        status = "✅" if has_tripvault else "❌"
        print(f"{status} Service worker configured for /tripvault/ path")
        
        return all_present and has_tripvault
    except Exception as e:
        print(f"❌ Error reading service worker: {e}")
        return False

def check_settings():
    """Check key settings configurations."""
    print("\n📋 Django Settings Check:")
    settings_path = BASE_DIR / "tripVault/settings.py"
    try:
        with open(settings_path, 'r') as f:
            content = f.read()
        
        checks = [
            ('ALLOWED_HOSTS', 'aj124.com' in content),
            ('LOGIN_URL', "LOGIN_URL = '/tripvault/user/login/'" in content),
            ('LOGIN_REDIRECT_URL', "LOGIN_REDIRECT_URL = '/tripvault/'" in content),
            ('STATIC_URL', "STATIC_URL = '/static/'" in content),
            ('STATICFILES_DIRS', "STATICFILES_DIRS" in content),
        ]
        
        for check_name, result in checks:
            status = "✅" if result else "❌"
            print(f"{status} {check_name} configured")
            
    except Exception as e:
        print(f"❌ Error reading settings: {e}")

def check_urls():
    """Check URL configurations."""
    print("\n🔗 URL Configuration Check:")
    urls_path = BASE_DIR / "tripVault/urls.py"
    try:
        with open(urls_path, 'r') as f:
            content = f.read()
        
        checks = [
            ('tripvault/ prefix', "path('tripvault/" in content),
            ('manifest.json route', "manifest.json" in content),
            ('serviceworker.js route', "serviceworker.js" in content),
        ]
        
        for check_name, result in checks:
            status = "✅" if result else "❌"
            print(f"{status} {check_name}")
            
    except Exception as e:
        print(f"❌ Error reading URLs: {e}")

def main():
    print("=" * 60)
    print("TripVault PWA Setup Verification")
    print("=" * 60)
    
    print("\n📁 File Structure Check:")
    files = [
        ("trip/templates/trip/manifest.json", "PWA Manifest"),
        ("trip/static/serviceworker.js", "Service Worker"),
        ("trip/static/icons/icon-192.png", "Icon 192x192"),
        ("trip/static/icons/icon-512.png", "Icon 512x512"),
        ("tripVault/settings.py", "Django Settings"),
        ("tripVault/urls.py", "Main URL Config"),
        ("trip/urls.py", "Trip URL Config"),
        ("trip/views.py", "Trip Views"),
    ]
    
    all_exist = True
    for file_path, description in files:
        exists = check_file_exists(file_path, description)
        all_exist = all_exist and exists
    
    print("\n📝 Content Verification:")
    manifest_ok = check_manifest_content()
    sw_ok = check_service_worker_content()
    
    check_settings()
    check_urls()
    
    print("\n" + "=" * 60)
    if all_exist and manifest_ok and sw_ok:
        print("✅ PWA Setup Complete! All checks passed.")
        print("\n📱 Next Steps:")
        print("   1. Run: python manage.py collectstatic")
        print("   2. Deploy to https://aj124.com/tripvault/")
        print("   3. Test on iOS Safari: Share → Add to Home Screen")
    else:
        print("❌ Some checks failed. Please review the output above.")
    print("=" * 60)

if __name__ == "__main__":
    main()
