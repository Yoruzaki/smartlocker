#!/bin/bash

# Disable screen saver and power management
xset s noblank
xset s off
xset -dpms

# Hide mouse cursor (requires 'unclutter' package)
unclutter -idle 0 &

# Start Chromium in Kiosk Mode
chromium --noerrdialogs --disable-infobars --kiosk http://localhost:5000 --check-for-update-interval=31536000
