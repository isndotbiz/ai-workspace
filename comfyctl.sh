#!/usr/bin/env bash
set -euo pipefail
. ~/ai-workspace/scripts/_log.sh

ROOT=~/ai-workspace
COMFY="$ROOT/ComfyUI"
MODELS="$COMFY/models"
CHECK="$MODELS/checkpoints"
DIFFUSION="$MODELS/diffusion_models"
LORAS="$MODELS/loras"
CLIP="$MODELS/clip"
VAE="$MODELS/vae"
TESTS="$ROOT/tests"

ensure_dirs(){ 
    mkdir -p "$CHECK" "$DIFFUSION" "$LORAS" "$CLIP" "$VAE" "$TESTS"
    note "Directory structure verified"
}

install_ff8(){
    ensure_dirs
    note "Installing Flux.1 Kontext FP8 (ComfyUI optimized version)"
    cd "$DIFFUSION"
    
    # Check if we already have the FP8 model
    if [ -f "flux1-dev-kontext_fp8_scaled.safetensors" ]; then
        note "FP8 model already present ($(du -h flux1-dev-kontext_fp8_scaled.safetensors | cut -f1))"
        return 0
    fi
    
    # Download using Python (already authenticated)
    python << 'EOF'
from huggingface_hub import hf_hub_download
import os

try:
    print("🔗 Downloading FLUX.1-Kontext FP8 from Comfy-Org...")
    downloaded_path = hf_hub_download(
        repo_id="Comfy-Org/flux1-kontext-dev_ComfyUI",
        filename="split_files/diffusion_models/flux1-dev-kontext_fp8_scaled.safetensors",
        local_dir=".",
        local_dir_use_symlinks=False
    )
    
    # Move to correct location
    import shutil
    src = "split_files/diffusion_models/flux1-dev-kontext_fp8_scaled.safetensors"
    dst = "flux1-dev-kontext_fp8_scaled.safetensors"
    
    if os.path.exists(src):
        shutil.move(src, dst)
        shutil.rmtree("split_files", ignore_errors=True)
        
        size_gb = os.path.getsize(dst) / (1024**3)
        print(f"✅ Downloaded FP8 model: {size_gb:.1f} GB")
    else:
        print("❌ Download failed")
        exit(1)
        
except Exception as e:
    print(f"❌ Download failed: {e}")
    exit(1)
EOF
    
    note "FF8 model installed successfully"
}

install_turbo_lora(){
    ensure_dirs
    note "Installing FLUX.1-Turbo-Alpha LoRA from camenduru collection"
    cd "$LORAS"
    
    # Check if already present
    if [ -f "FLUX.1-Turbo-Alpha.safetensors" ]; then
        note "Turbo LoRA already present ($(du -h FLUX.1-Turbo-Alpha.safetensors | cut -f1))"
        return 0
    fi
    
    python << 'EOF'
from huggingface_hub import hf_hub_download
import os

try:
    print("🚀 Downloading FLUX.1-Turbo-Alpha LoRA...")
    downloaded_path = hf_hub_download(
        repo_id="camenduru/FLUX.1-dev",
        filename="FLUX.1-Turbo-Alpha.safetensors",
        local_dir=".",
        local_dir_use_symlinks=False
    )
    
    if os.path.exists("FLUX.1-Turbo-Alpha.safetensors"):
        size_mb = os.path.getsize("FLUX.1-Turbo-Alpha.safetensors") / (1024*1024)
        print(f"✅ Downloaded Turbo LoRA: {size_mb:.1f} MB")
    else:
        print("❌ Download failed")
        exit(1)
        
except Exception as e:
    print(f"❌ Download failed: {e}")
    exit(1)
EOF
    
    note "Turbo LoRA installed successfully"
}

install_face_detailer(){
    ensure_dirs
    note "Installing Face Detailer workflow + required assets"
    
    # Download face detailer workflow
    cd "$TESTS"
    if [ ! -f "Face-Enhancer-Ultra.json" ]; then
        curl -L -o "Face-Enhancer-Ultra.json" "https://cdn.nextdiffusion.ai/workflows/face-enhancer-ultra.json" || {
            note "Face detailer workflow not available, creating placeholder"
            echo '{"note": "Face detailer workflow placeholder - import manually from ComfyUI examples"}' > "Face-Enhancer-Ultra.json"
        }
    fi
    
    # Ensure required encoders/VAE are present
    cd "$CLIP"
    [ -f "t5xxl_fp8_e4m3fn.safetensors" ] || {
        note "Downloading T5-XXL FP8 encoder..."
        wget -c "https://huggingface.co/Comfy-Org/flux1-dev/resolve/main/t5xxl_fp8_e4m3fn.safetensors" || 
        note "Manual download required for T5-XXL encoder"
    }
    
    [ -f "clip_l.safetensors" ] || {
        note "Downloading CLIP-L encoder..."
        wget -c "https://huggingface.co/Comfy-Org/flux1-dev/resolve/main/clip_l.safetensors" ||
        note "Manual download required for CLIP-L encoder"
    }
    
    cd "$VAE"
    [ -f "ae.safetensors" ] || {
        note "Downloading VAE..."
        wget -c "https://huggingface.co/black-forest-labs/flux-vae/resolve/main/ae.safetensors" ||
        note "Manual download required for VAE"
    }
    
    note "Face detailer assets setup complete"
}

install_multi_image_workflows(){
    ensure_dirs
    note "Installing Multi-Image Kontext workflows"
    cd "$TESTS"
    
    # Create multi-image workflows (placeholders for real workflow JSONs)
    cat > "Flux-Kontext-Multi-Image-Chaining.json" << 'EOF'
{
    "workflow_name": "Flux Kontext Multi-Image Chaining",
    "description": "Chain multiple reference images for identity + background control",
    "note": "Import from ComfyUI community or NextDiffusion examples",
    "recommended_settings": {
        "steps": "28-36",
        "guidance": "3.0-4.0", 
        "resolution": "832-1024 long side",
        "lora_strength": "0.6-0.8"
    }
}
EOF

    cat > "Flux-Kontext-Multi-Image-Stitching.json" << 'EOF'
{
    "workflow_name": "Flux Kontext Multi-Image Stitching", 
    "description": "Stitch multiple images for complex compositions",
    "note": "Import from ComfyUI community or NextDiffusion examples",
    "recommended_settings": {
        "steps": "32-40",
        "guidance": "3.5-4.5",
        "resolution": "1024x1024",
        "memory_optimization": "Use sequential processing"
    }
}
EOF
    
    note "Multi-image workflow templates created"
}

curate_photoreal_loras(){
    ensure_dirs
    note "Curating photoreal LoRAs compatible with Kontext"
    cd "$LORAS"
    
    # Install kontext-make-person-real LoRA
    if [ ! -f "kontext-make-person-real.safetensors" ]; then
        python << 'EOF'
from huggingface_hub import hf_hub_download
import os

try:
    print("📥 Downloading fofr/kontext-make-person-real LoRA...")
    downloaded_path = hf_hub_download(
        repo_id="fofr/kontext-make-person-real",
        filename="lora.safetensors",
        local_dir=".",
        local_dir_use_symlinks=False
    )
    
    # Rename for clarity
    if os.path.exists("lora.safetensors"):
        os.rename("lora.safetensors", "kontext-make-person-real.safetensors")
        size_mb = os.path.getsize("kontext-make-person-real.safetensors") / (1024*1024)
        print(f"✅ Downloaded kontext-make-person-real: {size_mb:.1f} MB")
        print("💡 Trigger: 'make this person look real'")
    
except Exception as e:
    print(f"❌ Failed to download fofr/kontext-make-person-real: {e}")
EOF
    fi
    
    # Install realism detailer LoRA  
    if [ ! -f "realism-detailer-kontext.safetensors" ]; then
        python << 'EOF'
from huggingface_hub import hf_hub_download
import os

try:
    print("📥 Downloading fal/Realism-Detailer-Kontext-Dev-LoRA...")
    downloaded_path = hf_hub_download(
        repo_id="fal/Realism-Detailer-Kontext-Dev-LoRA",
        filename="lora.safetensors", 
        local_dir=".",
        local_dir_use_symlinks=False
    )
    
    # Rename for clarity
    if os.path.exists("lora.safetensors"):
        os.rename("lora.safetensors", "realism-detailer-kontext.safetensors")
        size_mb = os.path.getsize("realism-detailer-kontext.safetensors") / (1024*1024)
        print(f"✅ Downloaded realism-detailer-kontext: {size_mb:.1f} MB")
        print("💡 Trigger: 'Add details to this face, improve skin details'")
    
except Exception as e:
    print(f"❌ Failed to download fal/Realism-Detailer-Kontext-Dev-LoRA: {e}")
EOF
    fi
    
    note "Photoreal LoRA curation completed"
    note "TIP: Browse huggingface.co/collections/fal/kontext-dev-loras for more options"
}

enable_ollama(){
    note "Setting up Ollama + prompt helper"
    
    # Install Ollama if not present
    if ! command -v ollama >/dev/null; then
        note "Installing Ollama..."
        curl -fsSL https://ollama.com/install.sh | sh
    else
        note "Ollama already installed"
    fi
    
    # Start Ollama service
    if ! pgrep ollama >/dev/null; then
        note "Starting Ollama service..."
        ollama serve > /dev/null 2>&1 &
        sleep 3
    fi
    
    # Pull required models
    note "Pulling LLM models for prompt assistance..."
    ollama pull llama3.1:8b || note "Failed to pull llama3.1:8b"
    ollama pull mistral:7b || note "Failed to pull mistral:7b"
    
    # Create prompt helper script
    cat > "$ROOT/scripts/prompt_helper.sh" << 'EOF'
#!/usr/bin/env bash
set -euo pipefail

MODEL="${1:-llama3.1:8b}"
shift 2>/dev/null || true

read -r -d '' SYS << 'EOT' || true
You are a prompt engineer for ComfyUI+Flux Kontext. Expand the user's short intent into a rich, explicit prompt:
- Include composition, lighting, lens, film grain, camera height, color palette.
- Add skin texture descriptors only when photoreal is intended.
- Avoid banned words and keep under 220 tokens.
- Focus on photography and cinematography terms.
- Be specific about technical camera settings.
EOT

QUERY="$*"
if [ -z "$QUERY" ]; then
    echo "Usage: $0 [model] <prompt to expand>"
    echo "Models: llama3.1:8b, mistral:7b"
    exit 1
fi

echo "🧠 Expanding prompt with $MODEL..."
echo "Original: $QUERY"
echo ""
echo "Expanded:"
ollama run "$MODEL" "$SYS" "$QUERY"
EOF
    
    chmod +x "$ROOT/scripts/prompt_helper.sh"
    note "Ollama + prompt helper ready"
}

prune_old_gguf(){
    note "Scanning for *.gguf files (dry-run)"
    
    # Find all GGUF files
    GGUF_FILES=$(find "$ROOT" -type f -name "*.gguf" 2>/dev/null || true)
    
    if [ -z "$GGUF_FILES" ]; then
        note "No GGUF files found"
        return 0
    fi
    
    echo "Found GGUF files:"
    echo "$GGUF_FILES" | while read -r file; do
        [ -f "$file" ] && echo "  $(du -h "$file" | cut -f1) $file"
    done
    
    echo ""
    read -rp "Delete all GGUF files? [y/N]: " yn
    if [[ "${yn:-N}" =~ ^[Yy]$ ]]; then
        note "Removing GGUF files..."
        echo "$GGUF_FILES" | while read -r file; do
            [ -f "$file" ] && rm -f "$file" && note "Deleted: $file"
        done
        note "GGUF cleanup completed"
    else
        note "Skipping GGUF deletion"
    fi
}

smoke_test(){
    ensure_dirs
    note "Running comprehensive smoke test"
    
    # Check if ComfyUI server is running
    if ! pgrep -f "ComfyUI/main.py" >/dev/null; then
        note "Starting ComfyUI server..."
        cd "$COMFY"
        nohup python main.py --listen 0.0.0.0 --port 8188 > /dev/null 2>&1 &
        sleep 8
    fi
    
    # Test API connectivity
    if curl -s http://127.0.0.1:8188/system_stats | python3 -m json.tool >/dev/null 2>&1; then
        note "✅ ComfyUI API responding"
    else
        note "❌ ComfyUI API not responding"
        return 1
    fi
    
    # Verify critical models
    REQUIRED_FILES=(
        "$DIFFUSION/flux1-dev-kontext_fp8_scaled.safetensors:FP8 Kontext model"
        "$LORAS/FLUX.1-Turbo-Alpha.safetensors:Turbo LoRA"
        "$CLIP/clip_l.safetensors:CLIP-L encoder"
        "$CLIP/t5xxl_fp8_e4m3fn.safetensors:T5-XXL encoder"
        "$VAE/ae.safetensors:VAE decoder"
    )
    
    for entry in "${REQUIRED_FILES[@]}"; do
        file="${entry%%:*}"
        desc="${entry##*:}"
        if [ -f "$file" ]; then
            size=$(du -h "$file" | cut -f1)
            note "✅ $desc ($size)"
        else
            note "❌ Missing: $desc"
        fi
    done
    
    # Test Ollama if available
    if command -v ollama >/dev/null; then
        if ollama list | grep -q llama3.1; then
            note "✅ Ollama + llama3.1:8b ready"
        else
            note "⚠️  Ollama installed but llama3.1:8b not found"
        fi
    fi
    
    note "Smoke test completed - see results above"
}

run_ukrainian_test_prompt(){
    ensure_dirs
    note "Running Ukrainian girl portrait test with auto-comparison"
    
    # Define the detailed Ukrainian girl prompt
    PROMPT="A hyper-realistic portrait of a late 20s Ukrainian girl with a fair skin tone and medium-length, voluminous balayage haircut, featuring deeper chocolate and rich auburn tones blending into a dark base, styled in an intricate braided crown intertwined with delicate golden wheat stalks and small wildflowers. A few soft, lighter strands still frame her face, each catching the warm, golden studio lights like spun sunlight. Her eyes are a bright, captivating warm brown, radiating a mix of heartfelt warmth and quiet strength, her gaze both gentle and profound. She wears a form-fitting, embroidered cream linen dress, inspired by traditional Ukrainian folk artistry with a modern twist. The dress features a deep V-neckline adorned with intricate gold and red embroidery patterns, wide, flowing sleeves gathered at the wrist, and a high slit subtly revealing her leg. The outfit incorporates delicate, sheer lace accents, with subtle, pearl-like beads catching the light. She stands serenely, her posture graceful and natural, one hand gently holding a small, intricately woven basket filled with ripe berries and wildflowers. The background is a warm, sun-drenched field of tall wheat, comprised of distant rolling hills, vibrant patches of wildflowers, and an ancient oak tree with dappled light filtering through its leaves, providing a serene and enchanting backdrop. Perfect anatomy, ideal body proportions, perfectly rendered hands and arms, complete realistic body structure."
    
    BASELINE="$TESTS/baseline_ukrainian_v0_2_0.png"
    TMP_OUTPUT="$TESTS/tmp_ukrainian_render.png"
    
    # Check if ComfyUI is running
    if ! curl -s http://127.0.0.1:8188/system_stats >/dev/null 2>&1; then
        note "❌ ComfyUI not running - start it first"
        return 1
    fi
    
    # Create test workflow with Ukrainian prompt
    TEST_WORKFLOW="/tmp/ukrainian_test_workflow.json"
    if [ -f "workflows/flux_kontext_fp8_turbo.json" ]; then
        cp workflows/flux_kontext_fp8_turbo.json "$TEST_WORKFLOW"
    elif [ -f "workflows/flux_kontext_fp8.json" ]; then
        cp workflows/flux_kontext_fp8.json "$TEST_WORKFLOW"
    else
        note "❌ No suitable workflow found"
        return 1
    fi
    
    # Modify workflow parameters
    python << EOF
import json
import time

# Load workflow
with open("$TEST_WORKFLOW", 'r') as f:
    workflow = json.load(f)

# Update parameters
test_seed = int(time.time() % 1000000)
if "5" in workflow:
    workflow["5"]["inputs"]["text"] = """$PROMPT"""
if "8" in workflow:
    workflow["8"]["inputs"]["batch_size"] = 1
if "9" in workflow:
    workflow["9"]["inputs"]["seed"] = test_seed
    workflow["9"]["inputs"]["steps"] = 12
if "7" in workflow:
    workflow["7"]["inputs"]["guidance"] = 6.0

# Save modified workflow
with open("$TEST_WORKFLOW", 'w') as f:
    json.dump(workflow, f)
    
print(f"Test seed: {test_seed}")
EOF
    
    note "🎨 Queuing Ukrainian portrait test..."
    
    # Queue the test
    RESULT=\$(curl -s -X POST -H "Content-Type: application/json" $
        -d "{\"prompt\": \$(cat \"$TEST_WORKFLOW\")}" $
        http://127.0.0.1:8188/prompt)
    
    if echo "$RESULT" | grep -q "prompt_id"; then
        PROMPT_ID=\$(echo "$RESULT" | grep -o '"prompt_id":"[^"]*"' | cut -d'"' -f4)
        note "✅ Test queued - Prompt ID: $PROMPT_ID"
        
        # Wait for generation to complete (simple polling)
        note "⏳ Waiting for generation to complete..."
        for i in {1..60}; do
            sleep 2
            # Check if new files appeared in output
            LATEST_FILE=\$(find "$COMFY/output" -name "flux_kontext*.png" -newer "$TEST_WORKFLOW" 2>/dev/null | head -1)
            if [ -n "$LATEST_FILE" ]; then
                break
            fi
            printf "."
        done
        echo ""
        
        # Find the generated file
        LATEST_FILE=\$(find "$COMFY/output" -name "flux_kontext*.png" -newer "$TEST_WORKFLOW" 2>/dev/null | head -1)
        
        if [ -n "$LATEST_FILE" ] && [ -f "$LATEST_FILE" ]; then
            cp "$LATEST_FILE" "$TMP_OUTPUT"
            
            # Calculate SHA256 hash
            NEW_HASH=\$(sha256sum "$TMP_OUTPUT" | cut -d' ' -f1)
            
            # Compare with baseline if it exists
            if [ -f "$BASELINE" ]; then
                OLD_HASH=\$(sha256sum "$BASELINE" | cut -d' ' -f1)
                
                if [ "$NEW_HASH" = "$OLD_HASH" ]; then
                    note "⏭️ No change in render (hash match: ${NEW_HASH:0:8}...). Skipping commit."
                    rm "$TMP_OUTPUT"
                else
                    mv "$TMP_OUTPUT" "$BASELINE"
                    note "🔄 Render updated → $BASELINE (hash: ${NEW_HASH:0:8}...)"
                    git add "$BASELINE"
                    git commit -m "Updated Ukrainian portrait baseline (${NEW_HASH:0:8})" || echo "Commit skipped"
                    VERSION_TAG="v0.2.$(date +%s)"
                    git tag "$VERSION_TAG" 2>/dev/null && note "Created tag: $VERSION_TAG"
                fi
            else
                mv "$TMP_OUTPUT" "$BASELINE"
                SIZE_MB=\$(du -m "$BASELINE" | cut -f1)
                note "📸 New baseline created → $BASELINE (${SIZE_MB}MB, hash: ${NEW_HASH:0:8}...)"
                git add "$BASELINE"
                git commit -m "Created Ukrainian portrait baseline (${NEW_HASH:0:8})" || echo "Commit skipped"
                git tag "v0.2.0" 2>/dev/null && note "Created tag: v0.2.0"
            fi
        else
            note "❌ No output file found after generation"
            return 1
        fi
    else
        note "❌ Failed to queue test generation: $RESULT"
        return 1
    fi
    
    # Cleanup
    rm -f "$TEST_WORKFLOW"
    
    note "✅ Ukrainian portrait test completed"
}

show_status(){
    echo ""
    echo "🎯 CURRENT SYSTEM STATUS"
    echo "========================"
    
    # Git status
    if [ -d .git ]; then
        CURRENT_TAG=$(git describe --tags 2>/dev/null || echo "No tags")
        COMMIT_COUNT=$(git rev-list --count HEAD 2>/dev/null || echo "0")
        echo "📋 Version: $CURRENT_TAG ($COMMIT_COUNT commits)"
    fi
    
    # Disk usage
    echo "💾 Disk usage:"
    [ -d "$MODELS" ] && du -sh "$MODELS"/* 2>/dev/null | sort -hr | head -5
    
    # Service status
    echo "🔧 Services:"
    pgrep -f "ComfyUI/main.py" >/dev/null && echo "  ✅ ComfyUI running" || echo "  ❌ ComfyUI stopped"
    pgrep ollama >/dev/null && echo "  ✅ Ollama running" || echo "  ❌ Ollama stopped"
    
    echo ""
}

menu(){
    clear
    cat << 'TXT'
=== 🎛️  Comfy Control Panel (comfyctl) ===
 
1) Install FP8 Kontext Model (11.9GB, memory efficient)
2) Install Turbo LoRA (661MB, speed optimization) 
3) Install Multi-Image Kontext workflows
4) Install Face Detailer workflow + dependencies
5) Curate photoreal LoRAs (Kontext-compatible)
6) Enable Ollama + Prompt Helper (AI assistant)
7) Prune old GGUF files (cleanup, optional)
8) Run smoke test (API + models verification)
9) Expand prompt with AI (Ollama helper)
h) Hunt & test LoRAs (advanced comparison)
t) Test Ukrainian girl prompt (with auto-comparison)
s) Show system status
v) Create version checkpoint (git tag)
0) Exit

TXT
    show_status
    read -rp "Select action: " choice
    
    case "$choice" in
        1) install_ff8;;
        2) install_turbo_lora;;
        3) install_multi_image_workflows;;
        4) install_face_detailer;;
        5) curate_photoreal_loras;;
        6) enable_ollama;;
        7) prune_old_gguf;;
        8) smoke_test;;
        9) 
            echo ""
            read -rp "Model (llama3.1:8b/mistral:7b): " model
            model=${model:-llama3.1:8b}
            read -rp "Your prompt idea: " query
            if [ -n "$query" ]; then
                "$ROOT/scripts/prompt_helper.sh" "$model" "$query"
            fi
            ;;
        h) "$ROOT/lora_hunter.py";;
        t) run_ukrainian_test_prompt;;
        s) show_status;;
        v)
            read -rp "Version tag (e.g., v0.2.0): " tag
            if [ -n "$tag" ]; then
                git add -A
                git commit -m "Checkpoint: $tag" || echo "No changes to commit"
                git tag "$tag" 2>/dev/null && note "Created tag: $tag" || note "Tag already exists"
            fi
            ;;
        0) exit 0;;
        *) echo "Invalid choice";;
    esac
    
    echo ""
    read -rp "Press Enter to continue..." _
}

# Main execution
ensure_dirs
while true; do 
    menu
done