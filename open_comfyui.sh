#!/bin/bash

# ComfyUI Web Interface Launcher
echo "🌐 Opening ComfyUI Web Interface..."
echo "=================================="

# Check if ComfyUI is running
if curl -s http://localhost:8188/system_stats >/dev/null 2>&1; then
    echo "✅ ComfyUI server is running"
else
    echo "❌ ComfyUI server is not running"
    echo "   Run 'comfyui-start' to start the server first"
    exit 1
fi

# Show recent images
echo ""
echo "📸 Your latest generated images:"
ls -latr ComfyUI/output/*.png | tail -5 | while read line; do
    echo "   $line"
done

echo ""
echo "🚀 Launching browsers..."
echo ""
echo "Available URLs:"
echo "   • Main Interface: http://localhost:8188"
echo "   • System Stats: http://localhost:8188/system_stats"
echo "   • Output Folder: ComfyUI/output/"

# Try to open with Firefox first, then Chromium as fallback
if command -v firefox >/dev/null 2>&1; then
    echo "   🦊 Opening Firefox..."
    firefox http://localhost:8188 >/dev/null 2>&1 &
    BROWSER_PID=$!
    echo "   Firefox launched (PID: $BROWSER_PID)"
elif command -v chromium-browser >/dev/null 2>&1; then
    echo "   🌐 Opening Chromium..."
    chromium-browser http://localhost:8188 >/dev/null 2>&1 &
    BROWSER_PID=$!
    echo "   Chromium launched (PID: $BROWSER_PID)"
else
    echo "   ❌ No browser found. Please open http://localhost:8188 manually"
    exit 1
fi

echo ""
echo "💡 Tips:"
echo "   • To view images: Click on 'Queue' tab → 'History' → Select a workflow"
echo "   • To generate new images: Load a workflow and click 'Queue Prompt'"
echo "   • Images are saved to: ComfyUI/output/"
echo ""
echo "✅ Browser launched! ComfyUI should open shortly..."