#!/bin/bash

# Warp Terminal Notification Fix Script
echo "🔧 Fixing Warp Terminal Notifications on Linux"
echo "================================================="

# 1. Check if notification daemon is running
echo "1. Checking notification daemon..."
if pgrep -x "dunst" >/dev/null; then
    echo "   ✅ dunst is running"
else
    echo "   🔄 Starting dunst..."
    nohup dunst >/dev/null 2>&1 &
    sleep 2
fi

# 2. Set environment variables for Warp
echo "2. Setting environment variables..."
export DISPLAY=:0
export DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$(id -u)/bus"

# 3. Test notification
echo "3. Testing notification system..."
if notify-send "Warp Test" "Notification system working!" --urgency=normal 2>/dev/null; then
    echo "   ✅ Notifications working"
else
    echo "   ❌ Notification test failed"
fi

# 4. Create Warp-specific notification script
echo "4. Creating Warp notification helper..."
cat > ~/.local/bin/warp-notify << 'EOF'
#!/bin/bash
export DISPLAY=:0
export DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$(id -u)/bus"
notify-send "$@"
EOF

chmod +x ~/.local/bin/warp-notify

# 5. Add to shell profile
echo "5. Adding to shell profile..."
if ! grep -q "WARP NOTIFICATIONS" ~/.bashrc; then
    cat >> ~/.bashrc << 'EOF'

# WARP NOTIFICATIONS FIX
export DISPLAY=:0
export DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$(id -u)/bus"

# Start notification daemon if not running
if ! pgrep -x "dunst" >/dev/null; then
    nohup dunst >/dev/null 2>&1 &
fi
EOF
    echo "   ✅ Added to ~/.bashrc"
else
    echo "   ✅ Already configured in ~/.bashrc"
fi

# 6. Test final notification
echo "6. Final notification test..."
sleep 1
notify-send "🎉 Warp Notifications Fixed!" "Your Warp terminal should now show notifications" --icon=dialog-information --urgency=normal

echo ""
echo "✅ SETUP COMPLETE!"
echo "   - Restart Warp terminal to ensure all changes take effect"
echo "   - Notifications should now work in Warp"
echo "   - If issues persist, run: source ~/.bashrc"