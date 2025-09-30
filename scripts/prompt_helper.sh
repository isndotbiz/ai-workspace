#!/bin/bash
MODEL="${1:-llama3.1:8b}"
USER_PROMPT="$2"

SYSTEM_PROMPT="You are a professional AI art prompt engineer specializing in FLUX.1 image generation. Transform the user's simple concept into a detailed, cinematic prompt that will produce stunning, photorealistic portraits. Include specific details about lighting, composition, camera settings, and artistic style. Keep it under 200 words but make it vivid and specific."

if [ -z "$USER_PROMPT" ]; then
    echo "Usage: $0 [model] <concept>"
    echo "Example: $0 llama3.1:8b 'mystical forest guardian'"
    exit 1
fi

echo "🧠 Expanding prompt with $MODEL..."
echo "Original concept: $USER_PROMPT"
echo ""
echo "Enhanced FLUX prompt:"
ollama run "$MODEL" "$SYSTEM_PROMPT

User concept: $USER_PROMPT

Enhanced FLUX prompt:"
