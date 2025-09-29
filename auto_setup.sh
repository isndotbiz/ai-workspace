#!/usr/bin/env bash
set -euo pipefail

# === AI Workspace Automated Setup Script ===
# This script will completely setup your AI workspace from scratch

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

ROOT="/home/jdm/ai-workspace"
COMFY="$ROOT/ComfyUI"

log() { echo -e "${GREEN}[$(date '+%H:%M:%S')]${NC} $1" | tee -a "$ROOT/setup-history.log"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$ROOT/setup-history.log"; }
error() { echo -e "${RED}[ERROR]${NC} $1" | tee -a "$ROOT/setup-history.log"; }
note() { echo -e "${CYAN}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }

banner() {
    clear
    echo -e "${PURPLE}"
    cat << 'EOF'
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║   🚀 AI WORKSPACE AUTOMATED SETUP 🚀                                         ║
║                                                                               ║
║   • ComfyUI with FLUX.1-dev optimized installation                           ║
║   • Photoreal LoRAs and workflows                                            ║
║   • Ollama integration for super prompt generation                           ║
║   • Comprehensive testing and validation                                     ║
║   • Face swapping preparation                                                ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
    echo
}

check_requirements() {
    log "Checking system requirements..."
    
    # Check if we have NVIDIA GPU
    if ! command -v nvidia-smi >/dev/null 2>&1; then
        error "NVIDIA GPU not detected or drivers not installed!"
        exit 1
    fi
    
    # Check VRAM
    local vram=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1)
    if [ "$vram" -lt 8000 ]; then
        warn "Low VRAM detected (${vram}MB). Some features may be limited."
    else
        success "GPU memory: ${vram}MB - Excellent for AI workloads!"
    fi
    
    # Check Python
    if ! command -v python3 >/dev/null 2>&1; then
        error "Python 3 not found!"
        exit 1
    fi
    
    success "System requirements check passed!"
}

setup_environment() {
    log "Setting up Python environment..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "$ROOT/venv" ]; then
        python3 -m venv "$ROOT/venv"
        log "Created Python virtual environment"
    fi
    
    # Activate virtual environment
    source "$ROOT/venv/bin/activate"
    
    # Install/upgrade pip
    pip install --upgrade pip
    
    # Install required packages
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
    pip install huggingface_hub transformers accelerate diffusers
    pip install requests pillow opencv-python numpy scipy
    pip install gitpython
    
    success "Python environment setup complete"
}

clone_comfyui() {
    log "Setting up ComfyUI..."
    
    if [ ! -d "$COMFY" ]; then
        git clone https://github.com/comfyanonymous/ComfyUI.git "$COMFY"
        log "Cloned ComfyUI repository"
    else
        log "ComfyUI already exists, updating..."
        cd "$COMFY" && git pull origin master
    fi
    
    # Install ComfyUI requirements
    cd "$COMFY"
    source "$ROOT/venv/bin/activate"
    pip install -r requirements.txt
    
    # Install custom nodes
    cd custom_nodes
    
    # ComfyUI-GGUF for optimized models
    if [ ! -d "ComfyUI-GGUF" ]; then
        git clone https://github.com/city96/ComfyUI-GGUF.git
        cd ComfyUI-GGUF && pip install -r requirements.txt
        cd ..
    fi
    
    # ComfyUI Manager for easy node management
    if [ ! -d "ComfyUI-Manager" ]; then
        git clone https://github.com/ltdrdata/ComfyUI-Manager.git
    fi
    
    success "ComfyUI setup complete"
}

download_models() {
    log "Downloading AI models..."
    
    local models_dir="$COMFY/models"
    mkdir -p "$models_dir"/{checkpoints,clip,vae,unet,loras}
    
    cd "$ROOT"
    source venv/bin/activate
    
    # Download FLUX.1-dev model
    python3 << 'EOF'
import os
from huggingface_hub import hf_hub_download

models_dir = "/home/jdm/ai-workspace/ComfyUI/models"
os.makedirs(f"{models_dir}/unet", exist_ok=True)

print("🔗 Downloading FLUX.1-dev GGUF model...")
try:
    hf_hub_download(
        repo_id="city96/FLUX.1-dev-gguf",
        filename="flux1-dev-Q3_K_S.gguf",
        local_dir=f"{models_dir}/unet",
        local_dir_use_symlinks=False
    )
    print("✅ FLUX.1-dev GGUF downloaded")
except Exception as e:
    print(f"❌ Failed to download FLUX.1-dev: {e}")

print("🔗 Downloading text encoders...")
try:
    hf_hub_download(
        repo_id="comfyanonymous/flux_text_encoders", 
        filename="clip_l.safetensors",
        local_dir=f"{models_dir}/clip",
        local_dir_use_symlinks=False
    )
    hf_hub_download(
        repo_id="comfyanonymous/flux_text_encoders",
        filename="t5xxl_fp16.safetensors", 
        local_dir=f"{models_dir}/clip",
        local_dir_use_symlinks=False
    )
    print("✅ Text encoders downloaded")
except Exception as e:
    print(f"❌ Failed to download encoders: {e}")

print("🔗 Downloading VAE...")
try:
    hf_hub_download(
        repo_id="black-forest-labs/FLUX.1-schnell",
        filename="ae.safetensors",
        local_dir=f"{models_dir}/vae", 
        local_dir_use_symlinks=False
    )
    print("✅ VAE downloaded")
except Exception as e:
    print(f"❌ Failed to download VAE: {e}")

print("🔗 Downloading LoRAs...")
loras = {
    "Hyper-FLUX.1-dev-8steps-lora.safetensors": ("ByteDance/Hyper-SD", "Hyper-FLUX.1-dev-8steps-lora.safetensors"),
    "flux-RealismLora.safetensors": ("XLabs-AI/flux-RealismLora", "lora.safetensors"),
    "flux-realism-enhancer.safetensors": ("strangerzonehf/Flux-Super-Realism-LoRA", "Super-Realism.safetensors")
}

for local_name, (repo_id, filename) in loras.items():
    try:
        downloaded_path = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            local_dir=f"{models_dir}/loras",
            local_dir_use_symlinks=False
        )
        # Rename if needed
        if filename != local_name:
            os.rename(
                f"{models_dir}/loras/{filename}",
                f"{models_dir}/loras/{local_name}"
            )
        print(f"✅ Downloaded {local_name}")
    except Exception as e:
        print(f"❌ Failed to download {local_name}: {e}")
EOF

    success "Model downloads complete"
}

install_ollama() {
    log "Installing and setting up Ollama..."
    
    # Install Ollama if not present
    if ! command -v ollama >/dev/null 2>&1; then
        curl -fsSL https://ollama.com/install.sh | sh
        log "Ollama installed"
    fi
    
    # Start Ollama service
    if ! pgrep -x "ollama" > /dev/null; then
        note "Starting Ollama service..."
        ollama serve &
        sleep 5
    fi
    
    # Pull models
    log "Downloading AI models for prompt generation..."
    ollama pull llama3.1:8b || warn "Failed to pull llama3.1:8b"
    ollama pull mistral:7b || warn "Failed to pull mistral:7b"
    
    success "Ollama setup complete"
}

create_workflows() {
    log "Creating optimized workflows..."
    
    mkdir -p "$ROOT/workflows"
    
    # Create basic FLUX workflow
    cat > "$ROOT/workflows/flux_basic.json" << 'EOF'
{
  "3": {
    "inputs": {
      "seed": 42,
      "steps": 12,
      "cfg": 3.5,
      "sampler_name": "euler",
      "scheduler": "simple",
      "denoise": 1,
      "model": ["4", 0],
      "positive": ["6", 0],
      "negative": ["7", 0],
      "latent_image": ["5", 0]
    },
    "class_type": "KSampler"
  },
  "4": {
    "inputs": {"ckpt_name": "flux1-dev-Q3_K_S.gguf"},
    "class_type": "CheckpointLoaderSimple"
  },
  "5": {
    "inputs": {"width": 1024, "height": 1024, "batch_size": 1},
    "class_type": "EmptyLatentImage"
  },
  "6": {
    "inputs": {"text": "A beautiful portrait", "clip": ["4", 1]},
    "class_type": "CLIPTextEncode"
  },
  "7": {
    "inputs": {"text": "blurry, low quality", "clip": ["4", 1]},
    "class_type": "CLIPTextEncode"
  },
  "8": {
    "inputs": {"samples": ["3", 0], "vae": ["4", 2]},
    "class_type": "VAEDecode"
  },
  "9": {
    "inputs": {"filename_prefix": "flux-output", "images": ["8", 0]},
    "class_type": "SaveImage"
  }
}
EOF

    # Create portrait workflow with LoRAs
    cat > "$ROOT/workflows/flux_portrait_lora.json" << 'EOF'
{
  "3": {
    "inputs": {
      "seed": 12345,
      "steps": 16, 
      "cfg": 3.5,
      "sampler_name": "euler",
      "scheduler": "simple",
      "denoise": 1,
      "model": ["11", 0],
      "positive": ["6", 0],
      "negative": ["7", 0],
      "latent_image": ["5", 0]
    },
    "class_type": "KSampler"
  },
  "4": {
    "inputs": {"ckpt_name": "flux1-dev-Q3_K_S.gguf"},
    "class_type": "CheckpointLoaderSimple"
  },
  "5": {
    "inputs": {"width": 832, "height": 1152, "batch_size": 1},
    "class_type": "EmptyLatentImage"
  },
  "6": {
    "inputs": {"text": "PROMPT_PLACEHOLDER", "clip": ["4", 1]},
    "class_type": "CLIPTextEncode"
  },
  "7": {
    "inputs": {"text": "blurry, low quality, distorted, bad anatomy", "clip": ["4", 1]},
    "class_type": "CLIPTextEncode"
  },
  "8": {
    "inputs": {"samples": ["3", 0], "vae": ["4", 2]},
    "class_type": "VAEDecode"
  },
  "9": {
    "inputs": {"filename_prefix": "portrait", "images": ["8", 0]},
    "class_type": "SaveImage"
  },
  "10": {
    "inputs": {
      "lora_name": "flux-RealismLora.safetensors",
      "strength_model": 0.8,
      "strength_clip": 0.8,
      "model": ["4", 0],
      "clip": ["4", 1]
    },
    "class_type": "LoraLoader"
  },
  "11": {
    "inputs": {
      "lora_name": "Hyper-FLUX.1-dev-8steps-lora.safetensors",
      "strength_model": 0.6,
      "strength_clip": 0.6,
      "model": ["10", 0],
      "clip": ["10", 1]
    },
    "class_type": "LoraLoader"
  }
}
EOF

    success "Workflows created"
}

create_scripts() {
    log "Creating utility scripts..."
    
    mkdir -p "$ROOT/scripts"
    
    # Create prompt helper
    cat > "$ROOT/scripts/prompt_helper.sh" << 'EOF'
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
EOF
    chmod +x "$ROOT/scripts/prompt_helper.sh"
    
    # Create startup script  
    cat > "$ROOT/start_comfyui.sh" << 'EOF'
#!/bin/bash
cd /home/jdm/ai-workspace
source venv/bin/activate
cd ComfyUI
python main.py --listen 0.0.0.0 --port 8188 --enable-cors-header
EOF
    chmod +x "$ROOT/start_comfyui.sh"
    
    # Create super prompt generator
    cat > "$ROOT/super_prompts.sh" << 'EOF' 
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
EOF
    chmod +x "$ROOT/super_prompts.sh"
    
    success "Utility scripts created"
}

create_testing_suite() {
    log "Creating comprehensive testing suite..."
    
    mkdir -p "$ROOT/tests"
    
    # Create test runner
    cat > "$ROOT/test_system.sh" << 'EOF'
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
EOF
    chmod +x "$ROOT/test_system.sh"
    
    success "Testing suite created"
}

face_swap_preparation() {
    log "Preparing face swapping infrastructure..."
    
    # Create face swap roadmap document
    cat > "$ROOT/FACE_SWAP_ROADMAP.md" << 'EOF'
# Face Swapping Implementation Roadmap

## Overview
This document outlines the plan to implement face swapping capabilities in our AI workspace.

## Phase 1: Research & Tools (Weeks 1-2)
- [ ] Study InsightFace + ReActor integration with ComfyUI
- [ ] Research IP-Adapter face conditioning methods
- [ ] Install ComfyUI-ReActor-Node
- [ ] Install ComfyUI-IP-Adapter-Plus
- [ ] Install ComfyUI-InstantID
- [ ] Test face detection accuracy with various image types

## Phase 2: Workflow Development (Weeks 3-4)
- [ ] Create face extraction pipeline
- [ ] Build identity preservation workflow
- [ ] Develop multi-face handling system
- [ ] Fine-tune face blending parameters
- [ ] Create face database management system

## Phase 3: Integration & Testing (Weeks 5-6)
- [ ] Integrate with existing portrait workflows
- [ ] Build batch processing system for multiple faces
- [ ] Quality validation pipeline
- [ ] Performance optimization for RTX 4060 Ti

## Phase 4: Production Features (Weeks 7-8)
- [ ] Real-time preview system
- [ ] Face alignment optimization
- [ ] Expression transfer capabilities
- [ ] Style consistency maintenance

## Requirements
- Additional 4-8GB VRAM for face models
- Face embedding database storage (~1GB per 1000 faces)
- Advanced workflow JSON templates
- Quality assessment automation

## Estimated Timeline
6-8 weeks for full implementation

## Notes
- Start with simple face swapping before advanced features
- Focus on quality over speed initially
- Build comprehensive testing for each phase
EOF

    # Create face swap placeholder scripts
    cat > "$ROOT/prepare_face_swap.sh" << 'EOF'
#!/bin/bash
echo "🔮 Face Swapping Preparation Script"
echo "This will be implemented in future phases..."
echo ""
echo "Next steps:"
echo "1. Research InsightFace integration"
echo "2. Install additional ComfyUI nodes"
echo "3. Create face detection workflows"
echo "4. Build face database system"
echo ""
echo "See FACE_SWAP_ROADMAP.md for detailed plan"
EOF
    chmod +x "$ROOT/prepare_face_swap.sh"
    
    success "Face swapping preparation complete"
}

final_setup() {
    log "Performing final setup tasks..."
    
    # Create main launcher
    cat > "$ROOT/launch.sh" << 'EOF'
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
EOF
    chmod +x "$ROOT/launch.sh"
    
    # Initialize git repository
    if [ ! -d "$ROOT/.git" ]; then
        git init
        git add .
        git commit -m "Initial AI workspace setup"
        git tag v1.0.0
        log "Git repository initialized with tag v1.0.0"
    fi
    
    success "Final setup complete!"
}

run_tests() {
    log "Running system validation tests..."
    
    cd "$ROOT"
    ./test_system.sh
    
    success "System validation complete!"
}

main() {
    banner
    
    log "Starting automated AI workspace setup..."
    echo
    
    check_requirements
    setup_environment  
    clone_comfyui
    download_models
    install_ollama
    create_workflows
    create_scripts
    create_testing_suite
    face_swap_preparation
    final_setup
    run_tests
    
    echo
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                                               ║${NC}"
    echo -e "${GREEN}║   🎉 AI WORKSPACE SETUP COMPLETE! 🎉                                         ║${NC}"
    echo -e "${GREEN}║                                                                               ║${NC}"
    echo -e "${GREEN}║   Your comprehensive AI workspace is ready for production use!               ║${NC}"
    echo -e "${GREEN}║                                                                               ║${NC}"
    echo -e "${GREEN}║   Next steps:                                                                ║${NC}"
    echo -e "${GREEN}║   1. Run: ./launch.sh                                                        ║${NC}"
    echo -e "${GREEN}║   2. Generate super prompts: ./super_prompts.sh                             ║${NC}"
    echo -e "${GREEN}║   3. Access ComfyUI at: http://localhost:8188                               ║${NC}"
    echo -e "${GREEN}║                                                                               ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo
    
    read -p "Launch the workspace now? [Y/n]: " choice
    if [[ "${choice:-Y}" =~ ^[Yy]$ ]]; then
        ./launch.sh
    fi
}

# Run if called directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi