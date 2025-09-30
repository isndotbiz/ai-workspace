#!/bin/bash
cd /home/jdm/ai-workspace

concepts=(
    "Ukrainian wealth goddess"
    "Cyberpunk street artist"
    "Renaissance portrait master"
    "Mystical forest guardian"
    "Film noir detective"
    "Space explorer princess"
    "Vintage fashion model"
    "Bohemian artist muse"
)

echo "🎨 Generating super prompts for portrait series..."
echo ""

for concept in "${concepts[@]}"; do
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🎭 CONCEPT: $concept"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    ./scripts/prompt_helper.sh llama3.1:8b "$concept"
    echo ""
    echo ""
done

echo "✨ Super prompt generation complete!"
echo "💡 Use these prompts in your ComfyUI workflows for stunning results!"
