#!/bin/bash

# Ukrainian Flower Hat Gallery Viewer
echo "🌻 UKRAINIAN FLOWER HAT GALLERY 🌻"
echo "=================================="

OUTPUT_DIR="ComfyUI/output"

# Get the latest Ukrainian flower hat images
echo "🎨 Loading your beautiful Ukrainian flower hat collection..."
FLOWER_HAT_IMAGES=($(ls -t $OUTPUT_DIR/flux_kontext_turbo_000{36..43}*.png 2>/dev/null))

if [ ${#FLOWER_HAT_IMAGES[@]} -eq 0 ]; then
    echo "❌ No flower hat images found"
    exit 1
fi

echo "📊 Found ${#FLOWER_HAT_IMAGES[@]} beautiful Ukrainian flower hat portraits:"
for img in "${FLOWER_HAT_IMAGES[@]}"; do
    echo "   🌺 $(basename "$img")"
done
echo ""

echo "🎯 Collection Features:"
echo "   • Traditional Ukrainian flower hats"
echo "   • Light summer clothing for warm weather"
echo "   • Vibrant floral elements"
echo "   • Elegant countryside settings"
echo "   • Beautiful late-20s Ukrainian women"
echo ""

echo "🚀 Opening flower hat gallery in feh viewer..."
echo "💡 Controls:"
echo "   • Space/Enter = Next beautiful portrait"
echo "   • Backspace = Previous portrait" 
echo "   • F = Toggle fullscreen"
echo "   • Q = Quit viewer"
echo "   • + / - = Zoom in/out"
echo ""

# Launch feh with the flower hat collection
feh --auto-zoom --borderless --geometry 1200x800 "${FLOWER_HAT_IMAGES[@]}" &
VIEWER_PID=$!

echo "✅ Ukrainian flower hat gallery launched (PID: $VIEWER_PID)"
echo "🌻 Viewing your stunning Ukrainian women with traditional flower hats!"
echo ""
echo "📁 Images are located in: $(pwd)/$OUTPUT_DIR/"
echo "🎨 Perfect for warm weather - light, airy, and beautiful!"