#!/bin/bash
cd /home/jdm/ai-workspace

echo "🎨 AI Workspace Launcher"
echo "======================="
echo ""
echo "Available commands:"
echo "1. Start ComfyUI:        ./start_comfyui.sh"
echo "2. Generate super prompts: ./super_prompts.sh"
echo "3. Test system:          ./test_system.sh"
echo "4. Prompt helper:        ./scripts/prompt_helper.sh"
echo "5. Face swap prep:       ./prepare_face_swap.sh"
echo ""
echo "ComfyUI will be available at: http://localhost:8188"
echo ""

# Start Ollama if not running
if ! pgrep -x "ollama" > /dev/null; then
    echo "Starting Ollama service..."
    ollama serve &
    sleep 2
fi

read -p "Start ComfyUI now? [Y/n]: " choice
if [[ "${choice:-Y}" =~ ^[Yy]$ ]]; then
    ./start_comfyui.sh
fi
