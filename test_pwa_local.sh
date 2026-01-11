#!/bin/bash

# TripVault PWA Local Testing Script
# This script helps test PWA features locally

echo "================================================"
echo "TripVault PWA Local Testing"
echo "================================================"
echo ""

# Check if Django is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed"
    exit 1
fi

echo "✅ Python3 found"

# Check if in correct directory
if [ ! -f "manage.py" ]; then
    echo "❌ Please run this script from the TripVault root directory"
    exit 1
fi

echo "✅ In correct directory"

# Run verification
echo ""
echo "Running PWA setup verification..."
echo ""
python3 verify_pwa_setup.py

echo ""
echo "================================================"
echo "Starting Django Development Server..."
echo "================================================"
echo ""
echo "🌐 Server will start at: http://localhost:8000/tripvault/"
echo ""
echo "📱 To test PWA features:"
echo "   1. Open Chrome and visit: http://localhost:8000/tripvault/"
echo "   2. Open DevTools (F12 or Cmd+Option+I)"
echo "   3. Go to Application tab"
echo "   4. Check Manifest and Service Workers"
echo ""
echo "⚠️  Note: Service Workers work on localhost even without HTTPS"
echo "    But iOS installation requires actual HTTPS deployment"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start Django development server
python3 manage.py runserver
