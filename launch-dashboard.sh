#!/bin/bash
#
# HIBP Dashboard Launcher
# This script launches the dashboard and opens the browser
#

set -e

# Navigate to dashboard directory
cd /raid0/ClaudeCodeProjects/hibp-project/dashboard

# Check if dashboard is already running
if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "Dashboard is already running!"
    echo "Opening browser..."
    xdg-open http://127.0.0.1:5000
    echo ""
    echo "Press Enter to close this window..."
    read
    exit 0
fi

# Start the dashboard in background
echo "Starting HIBP Dashboard..."
./start-dashboard.sh &
DASHBOARD_PID=$!

# Wait for dashboard to start
echo "Waiting for dashboard to start..."
sleep 3

# Open browser
echo "Opening browser..."
xdg-open http://127.0.0.1:5000

echo ""
echo "Dashboard is running at: http://127.0.0.1:5000"
echo "Dashboard PID: $DASHBOARD_PID"
echo ""
echo "Press Enter to stop the dashboard and close this window..."
read

# Stop dashboard
kill $DASHBOARD_PID 2>/dev/null || true
echo "Dashboard stopped."
