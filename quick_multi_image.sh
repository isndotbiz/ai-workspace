#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
. scripts/_log.sh

note "🎨 Multi-Image ComfyUI Quick Start"

# Check if ComfyUI is running
if ! curl -s http://127.0.0.1:8188/system_stats >/dev/null 2>&1; then
    note "Starting ComfyUI..."
    cd ComfyUI
    python main.py --listen 0.0.0.0 --port 8188 > /tmp/comfyui.log 2>&1 &
    cd ..
    
    # Wait for startup
    for i in {1..30}; do
        sleep 2
        if curl -s http://127.0.0.1:8188/system_stats >/dev/null 2>&1; then
            break
        fi
        printf "."
    done
    echo ""
fi

if curl -s http://127.0.0.1:8188/system_stats >/dev/null 2>&1; then
    note "✅ ComfyUI running at http://localhost:8188"
else
    note "❌ Failed to start ComfyUI"
    exit 1
fi

echo ""
echo "🎛️ MULTI-IMAGE WORKFLOW OPTIONS:"
echo "================================="
echo ""
echo "1) 🔗 Multi-Image Chaining (Character consistency across scenes)"
echo "   - Load: ~/ai-workspace/tests/Flux-Kontext-Multi-Image-Chaining.json"
echo "   - Use: Multiple reference images → consistent identity"
echo "   - Settings: CFG 3.0-4.0, Steps 28-36"
echo ""
echo "2) 🧩 Multi-Image Stitching (Complex compositions)"
echo "   - Load: ~/ai-workspace/tests/Flux-Kontext-Multi-Image-Stitching.json" 
echo "   - Use: Combine multiple images → unified composition"
echo "   - Settings: CFG 3.5-4.5, Steps 32-40"
echo ""
echo "3) 🧠 Expand Prompt with AI (Ollama helper)"
read -rp "Select option (1-3): " choice

case "$choice" in
    1)
        note "Opening Multi-Image Chaining workflow..."
        echo "📋 Instructions:"
        echo "   1. Open ComfyUI: http://localhost:8188"
        echo "   2. Load workflow: ~/ai-workspace/tests/Flux-Kontext-Multi-Image-Chaining.json"
        echo "   3. Add multiple 'Load Image' nodes"
        echo "   4. Connect to nodes 3,6,7,8 (your flux-kontext setup)"
        echo "   5. Set CFG: 3.0-4.0, Steps: 28-36"
        ;;
    2)
        note "Opening Multi-Image Stitching workflow..."
        echo "📋 Instructions:"
        echo "   1. Open ComfyUI: http://localhost:8188"
        echo "   2. Load workflow: ~/ai-workspace/tests/Flux-Kontext-Multi-Image-Stitching.json"
        echo "   3. Prepare 2-4 source images (same resolution)"
        echo "   4. Use sequential processing for VRAM efficiency"
        echo "   5. Set CFG: 3.5-4.5, Steps: 32-40"
        ;;
    3)
        echo ""
        read -rp "Model (llama3.1:8b/mistral:7b): " model
        model=${model:-mistral:7b}
        read -rp "Your multi-image prompt idea: " query
        if [ -n "$query" ]; then
            note "🧠 Expanding prompt with $model..."
            scripts/prompt_helper.sh "$model" "$query"
        fi
        ;;
    *)
        note "Invalid choice. See usage guide: ~/ai-workspace/HOW_TO_USE_MULTI_IMAGE.md"
        ;;
esac

echo ""
note "📚 Full documentation: ~/ai-workspace/HOW_TO_USE_MULTI_IMAGE.md"
note "🎛️ Control panel: ./comfyctl.sh"

# Open browser if on desktop environment
if command -v xdg-open >/dev/null 2>&1; then
    note "Opening ComfyUI in browser..."
    xdg-open http://localhost:8188 2>/dev/null || true
fi