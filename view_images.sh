#!/bin/bash

# High-Speed AI Image Viewer
echo "📸 High-Speed AI Image Viewer"
echo "============================="

OUTPUT_DIR="ComfyUI/output"

# Check if output directory exists
if [ ! -d "$OUTPUT_DIR" ]; then
    echo "❌ Output directory not found: $OUTPUT_DIR"
    exit 1
fi

# Count images
IMG_COUNT=$(ls $OUTPUT_DIR/*.png 2>/dev/null | wc -l)
if [ $IMG_COUNT -eq 0 ]; then
    echo "❌ No PNG images found in $OUTPUT_DIR"
    exit 1
fi

echo "📊 Found $IMG_COUNT images in $OUTPUT_DIR"
echo ""

# Show recent images
echo "🎨 Latest generated images:"
ls -latr $OUTPUT_DIR/*.png | tail -8 | while read line; do
    echo "   $line"
done
echo ""

# Viewer options
echo "🖼️  Choose your preferred viewer:"
echo "   1) feh - Ultra-fast, keyboard shortcuts, slideshow"
echo "   2) eog - GNOME Image Viewer (Eye of GNOME)"  
echo "   3) gpicview - Lightweight, fast startup"
echo "   4) Open all recent images in feh slideshow"
echo "   5) Open only latest 5 images"

read -p "Enter choice [1-5]: " choice

case $choice in
    1)
        echo "🚀 Opening with feh (ultra-fast)..."
        echo "💡 Keyboard shortcuts: Space/Enter=next, Backspace=prev, Q=quit, F=fullscreen"
        feh $OUTPUT_DIR/*.png &
        ;;
    2)
        echo "🚀 Opening with Eye of GNOME..."
        eog $OUTPUT_DIR/*.png &
        ;;
    3)
        echo "🚀 Opening with gpicview (lightweight)..."
        gpicview $OUTPUT_DIR/*.png &
        ;;
    4)
        echo "🚀 Opening slideshow of recent images with feh..."
        echo "💡 Slideshow mode: Auto-advance every 3 seconds"
        feh --slideshow-delay 3 --fullscreen --auto-zoom $OUTPUT_DIR/*.png &
        ;;
    5)
        echo "🚀 Opening latest 5 images with feh..."
        RECENT_IMAGES=($(ls -t $OUTPUT_DIR/*.png | head -5))
        feh "${RECENT_IMAGES[@]}" &
        ;;
    *)
        echo "❌ Invalid choice. Opening with feh (default)..."
        feh $OUTPUT_DIR/*.png &
        ;;
esac

VIEWER_PID=$!
echo "✅ Image viewer launched (PID: $VIEWER_PID)"
echo ""
echo "🎯 Your beautiful businesswoman images are now displayed!"
echo "📁 Images location: $(pwd)/$OUTPUT_DIR/"