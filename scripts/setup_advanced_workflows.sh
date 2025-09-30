#!/bin/bash
# Advanced Workflow Setup: Upscaling, Face Detail & Multi-Image Kontext
# For RTX 4060 Ti 16GB optimized workflows

set -e

WORKSPACE_ROOT="/home/jdm/ai-workspace"
COMFYUI_ROOT="$WORKSPACE_ROOT/ComfyUI"
MODELS_ROOT="$COMFYUI_ROOT/models"

echo "======================================================================="
echo "🚀 Advanced Workflow Setup for ComfyUI"
echo "======================================================================="
echo ""
echo "This will install:"
echo "  ✓ Upscaling models (ESRGAN, RealESRGAN)"
echo "  ✓ Face restoration models (GFPGAN, CodeFormer)"
echo "  ✓ Face detection models"
echo "  ✓ Example workflows for advanced techniques"
echo ""

# Create necessary directories
echo "📁 Creating model directories..."
mkdir -p "$MODELS_ROOT/upscale_models"
mkdir -p "$MODELS_ROOT/facerestore_models"
mkdir -p "$MODELS_ROOT/facedetection"
mkdir -p "$MODELS_ROOT/insightface"
mkdir -p "$WORKSPACE_ROOT/workflows/advanced"

# Function to download model if not exists
download_model() {
    local url=$1
    local output_path=$2
    local name=$3
    
    if [ -f "$output_path" ]; then
        echo "✓ $name already exists, skipping..."
    else
        echo "⬇️  Downloading $name..."
        wget -q --show-progress "$url" -O "$output_path" || {
            echo "❌ Failed to download $name"
            return 1
        }
        echo "✅ $name downloaded successfully"
    fi
}

# Download upscaling models
echo ""
echo "📥 Downloading Upscaling Models..."
echo "-------------------------------------------------------------------"

# 4x-UltraSharp (best general purpose)
download_model \
    "https://huggingface.co/Kim2091/UltraSharp/resolve/main/4x-UltraSharp.pth" \
    "$MODELS_ROOT/upscale_models/4x-UltraSharp.pth" \
    "4x-UltraSharp"

# RealESRGAN x4plus (photorealistic)
download_model \
    "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth" \
    "$MODELS_ROOT/upscale_models/RealESRGAN_x4plus.pth" \
    "RealESRGAN_x4plus"

# RealESRGAN x4plus anime
download_model \
    "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.2.4/RealESRGAN_x4plus_anime_6B.pth" \
    "$MODELS_ROOT/upscale_models/RealESRGAN_x4plus_anime_6B.pth" \
    "RealESRGAN_x4plus_anime_6B"

# Download face restoration models
echo ""
echo "📥 Downloading Face Restoration Models..."
echo "-------------------------------------------------------------------"

# GFPGAN v1.4 (balanced quality/speed)
download_model \
    "https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth" \
    "$MODELS_ROOT/facerestore_models/GFPGANv1.4.pth" \
    "GFPGANv1.4"

# CodeFormer (high quality with fidelity control)
download_model \
    "https://github.com/sczhou/CodeFormer/releases/download/v0.1.0/codeformer.pth" \
    "$MODELS_ROOT/facerestore_models/codeformer.pth" \
    "CodeFormer"

# Detection model weights for MediaPipe/YOLO (if needed by Impact Pack)
echo ""
echo "📥 Face detection models (via Impact Pack dependencies)..."
echo "Note: Impact Pack will download these automatically on first use"

# Create model info file
echo ""
echo "📄 Creating model inventory..."
cat > "$WORKSPACE_ROOT/ADVANCED_MODELS_INFO.md" << 'EOF'
# Advanced Workflow Models Inventory

## Upscaling Models (ComfyUI/models/upscale_models/)

### 4x-UltraSharp.pth (~67MB)
- **Best for:** General purpose, photorealistic images
- **Upscale factor:** 4x
- **Use case:** Portraits, landscapes, product photography
- **Recommended tile size:** 512-1024px

### RealESRGAN_x4plus.pth (~64MB)
- **Best for:** Realistic photographs
- **Upscale factor:** 4x  
- **Use case:** Photo enhancement, face details
- **Recommended tile size:** 512px

### RealESRGAN_x4plus_anime_6B.pth (~18MB)
- **Best for:** Anime, manga, illustrations
- **Upscale factor:** 4x
- **Use case:** Anime artwork, stylized content
- **Recommended tile size:** 512-1024px

## Face Restoration Models (ComfyUI/models/facerestore_models/)

### GFPGANv1.4.pth (~348MB)
- **Best for:** Balanced quality and speed
- **Restoration strength:** 0.5-0.8 recommended
- **Use case:** Portrait enhancement, face detail recovery
- **Works with:** FaceDetailer node (Impact Pack)

### codeformer.pth (~376MB)
- **Best for:** High quality with fidelity control
- **Fidelity range:** 0.5 (more natural) to 1.0 (more accurate)
- **Use case:** Professional portrait restoration
- **Works with:** CodeFormer nodes

## Face Detection Models

Automatically downloaded by Impact Pack on first use:
- **yolov5_face**: Fast, accurate multi-face detection
- **MediaPipe**: Lightweight real-time detection
- **RetinaFace**: High accuracy detection

## Usage Recommendations by Hardware

### RTX 4060 Ti 16GB (Your System)
- **Upscale tile size:** 1024px (safe), 2048px (with memory management)
- **Batch processing:** 1-2 images at a time
- **Face detail + Upscale:** Use sequential processing
- **Multi-image Kontext:** 2-3 reference images optimal

### Workflow Selection
- **Fast Mode:** 512px tiles, 20 steps, single pass
- **Quality Mode:** 1024px tiles, 30-40 steps, multi-stage
- **Ultra Mode:** 2048px tiles, 50 steps, face detail + upscale

## Model Combinations

### Best Portrait Enhancement
1. Generate with FLUX Kontext FP8
2. Face restore with GFPGANv1.4 (strength 0.7)
3. Upscale with 4x-UltraSharp (denoise 0.3)

### Best Anime/Illustration
1. Generate with FLUX
2. Upscale with RealESRGAN_x4plus_anime_6B
3. Optional: Light face detail with CodeFormer (fidelity 0.5)

### Best Multi-Image Composition
1. FLUX Kontext with 2-3 reference images
2. Face detail on main subject (GFPGANv1.4)
3. Selective upscale on focal areas

## Troubleshooting

**Out of VRAM:**
- Reduce tile size to 512px
- Use --lowvram flag in ComfyUI
- Process images sequentially

**Blurry upscale:**
- Increase denoise (0.4-0.5)
- Try different upscale model
- Use multi-stage upscaling (2x → 2x)

**Over-processed faces:**
- Lower restoration strength (0.4-0.6)
- Use CodeFormer with lower fidelity
- Reduce denoise in face detail step

**Faces not detected:**
- Lower detection threshold (0.3-0.4)
- Try different detection model
- Check image resolution (faces too small?)

EOF

echo "✅ Model inventory created: ADVANCED_MODELS_INFO.md"

# Check installed custom nodes
echo ""
echo "🔍 Checking installed custom nodes..."
echo "-------------------------------------------------------------------"

cd "$COMFYUI_ROOT/custom_nodes"

if [ -d "ComfyUI-Impact-Pack" ]; then
    echo "✅ ComfyUI-Impact-Pack: Installed"
else
    echo "⚠️  ComfyUI-Impact-Pack: NOT FOUND"
    echo "   Installing now..."
    git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack.git
    cd ComfyUI-Impact-Pack && python install.py
fi

if [ -d "ComfyUI_UltimateSDUpscale" ]; then
    echo "✅ ComfyUI_UltimateSDUpscale: Installed"
else
    echo "⚠️  ComfyUI_UltimateSDUpscale: NOT FOUND"
    echo "   Installing now..."
    git clone https://github.com/ssitu/ComfyUI_UltimateSDUpscale.git
fi

echo ""
echo "======================================================================="
echo "✅ Advanced Workflow Setup Complete!"
echo "======================================================================="
echo ""
echo "📦 Installed Models:"
ls -lh "$MODELS_ROOT/upscale_models/" | grep -E "\.pth$" | wc -l | xargs echo "  Upscaling models:"
ls -lh "$MODELS_ROOT/facerestore_models/" | grep -E "\.pth$" | wc -l | xargs echo "  Face restoration models:"
echo ""
echo "📚 Documentation:"
echo "  - ADVANCED_MODELS_INFO.md - Model details and usage guide"
echo ""
echo "🎯 Next Steps:"
echo "  1. Restart ComfyUI to load new models"
echo "  2. Check example workflows in workflows/advanced/"
echo "  3. Run: python scripts/create_advanced_workflows.py"
echo ""
echo "🚀 Ready to create advanced workflows!"
echo "======================================================================="