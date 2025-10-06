#!/bin/bash

# View wellness poses with feh image viewer
# Shows latest wellness pose images with navigation

echo "🧘 Wellness Poses Viewer"
echo "========================"

WELLNESS_DIR="ComfyUI/output"
WELLNESS_PATTERN="wellness_pose_*.png"

cd /home/jdm/ai-workspace

# Check if wellness images exist
if ! ls ${WELLNESS_DIR}/${WELLNESS_PATTERN} 1> /dev/null 2>&1; then
    echo "❌ No wellness pose images found!"
    echo "🎯 Run: ./generate_wellness_poses.py"
    exit 1
fi

# Count images
WELLNESS_COUNT=$(ls ${WELLNESS_DIR}/${WELLNESS_PATTERN} 2>/dev/null | wc -l)
echo "📸 Found ${WELLNESS_COUNT} wellness pose images"

# Show latest 20 wellness poses
echo "🎨 Viewing latest wellness poses..."
echo "📱 Navigation: ← → arrows, Q to quit, F for fullscreen"
echo

# Get latest wellness images and launch feh
ls -t ${WELLNESS_DIR}/${WELLNESS_PATTERN} | head -20 | feh -f - \
    --title "Wellness Poses Gallery - %f" \
    --geometry 1200x900 \
    --scale-down \
    --auto-zoom \
    --borderless \
    --info "echo '%f - %wx%h - %s bytes'" \
    2>/dev/null

echo "✅ Wellness poses viewer closed"