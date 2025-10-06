#!/bin/bash

# Quick Power Poses Viewer - Latest Businesswoman Images
echo "💼 POWER POSES GALLERY - Latest Businesswoman Images"
echo "==================================================="

OUTPUT_DIR="ComfyUI/output"

# Get the latest businesswoman images (last 10 generated)
echo "🎨 Loading your latest powerful businesswoman portraits..."
LATEST_IMAGES=($(ls -t $OUTPUT_DIR/flux_kontext_turbo_*.png | head -10))

if [ ${#LATEST_IMAGES[@]} -eq 0 ]; then
    echo "❌ No businesswoman images found"
    exit 1
fi

echo "📊 Found ${#LATEST_IMAGES[@]} latest power pose images:"
for img in "${LATEST_IMAGES[@]}"; do
    echo "   📸 $(basename "$img")"
done
echo ""

echo "🚀 Opening in feh image viewer..."
echo "💡 Controls:"
echo "   • Space/Enter = Next image"
echo "   • Backspace = Previous image" 
echo "   • F = Toggle fullscreen"
echo "   • Q = Quit viewer"
echo "   • + / - = Zoom in/out"
echo ""

# Launch feh with the latest businesswoman images
feh --auto-zoom --borderless --geometry 1200x800 "${LATEST_IMAGES[@]}" &
VIEWER_PID=$!

echo "✅ Power poses gallery launched (PID: $VIEWER_PID)"
echo "🎯 Viewing your stunning late-20s businesswoman portfolio!"
echo ""
echo "📁 Images are located in: $(pwd)/$OUTPUT_DIR/"