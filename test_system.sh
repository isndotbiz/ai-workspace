#!/bin/bash
cd /home/jdm/ai-workspace
source venv/bin/activate

echo "🧪 Running comprehensive system tests..."

# Test 1: Check if ComfyUI starts
echo "Test 1: ComfyUI startup..."
cd ComfyUI
timeout 30s python main.py --cpu &
PID=$!
sleep 10
if kill -0 $PID 2>/dev/null; then
    echo "✅ ComfyUI starts successfully"
    kill $PID
else
    echo "❌ ComfyUI failed to start"
fi

# Test 2: Check models
echo "Test 2: Model files..."
required_files=(
    "models/unet/flux1-dev-Q3_K_S.gguf"
    "models/clip/clip_l.safetensors"
    "models/clip/t5xxl_fp16.safetensors"
    "models/vae/ae.safetensors"
    "models/loras/Hyper-FLUX.1-dev-8steps-lora.safetensors"
    "models/loras/flux-RealismLora.safetensors"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        size=$(du -h "$file" | cut -f1)
        echo "✅ $file ($size)"
    else
        echo "❌ Missing: $file"
    fi
done

# Test 3: Ollama
echo "Test 3: Ollama service..."
if command -v ollama >/dev/null 2>&1; then
    if ollama list | grep -q llama3.1; then
        echo "✅ Ollama + llama3.1:8b ready"
    else
        echo "⚠️  Ollama installed but models missing"
    fi
else
    echo "❌ Ollama not installed"
fi

echo "🏁 System test complete!"
