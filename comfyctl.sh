#!/bin/bash

# ComfyUI CLI Control Panel - flux-kontext with Ollama Integration
# Version 1.0.0 - Structured, auditable AI portrait generation workflow
# Hardware: RTX 4060 Ti - Optimized for FP8 models

set -euo pipefail

# ============================================================================
# CONFIGURATION
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMFYUI_DIR="${SCRIPT_DIR}/ComfyUI"
WORKFLOW_DIR="${COMFYUI_DIR}/venv/lib/python3.12/site-packages/comfyui_workflow_templates/templates"
OUTPUT_DIR="${COMFYUI_DIR}/output"
VENV_PATH="${COMFYUI_DIR}/venv/bin/activate"

# Default parameters (Node IDs from flux-kontext workflow)
DEFAULT_SEED="randomize"
DEFAULT_BATCH=1          # Node ID 7
DEFAULT_STEPS=20         # Node ID 8  
DEFAULT_CFG=2.5          # Node ID 6
DEFAULT_PROMPT=""        # Node ID 3
DEFAULT_WIDTH=1024
DEFAULT_HEIGHT=1024

# Workflow templates
FLUX_KONTEXT_BASIC="flux_kontext_dev_basic.json"
FLUX_KONTEXT_MULTI="api_bfl_flux_1_kontext_multiple_images_input.json"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    exit 1
}

check_dependencies() {
    log "🔍 Checking dependencies..."
    
    if ! command -v python3 &> /dev/null; then
        error "Python3 not found. Please install Python 3.8+."
    fi
    
    if ! command -v ollama &> /dev/null; then
        warn "Ollama not found. Install with: curl -fsSL https://ollama.ai/install.sh | sh"
        warn "Prompt optimization will be disabled."
        OLLAMA_AVAILABLE=false
    else
        OLLAMA_AVAILABLE=true
        log "✅ Ollama found"
    fi
    
    if [[ ! -f "${VENV_PATH}" ]]; then
        error "ComfyUI virtual environment not found at ${VENV_PATH}"
    fi
    
    if [[ ! -f "${WORKFLOW_DIR}/${FLUX_KONTEXT_BASIC}" ]]; then
        error "Flux-kontext workflow template not found"
    fi
    
    log "✅ Dependencies check passed"
}

activate_venv() {
    log "🚀 Activating ComfyUI virtual environment..."
    source "${VENV_PATH}"
}

# ============================================================================
# OLLAMA INTEGRATION
# ============================================================================

optimize_prompt_with_ollama() {
    local input_prompt="$1"
    
    if [[ "${OLLAMA_AVAILABLE}" != "true" ]]; then
        echo "${input_prompt}"
        return
    fi
    
    log "🧠 Optimizing prompt with Ollama (Mistral)..."
    
    local system_prompt="You are an expert prompt engineer for AI image generation models, specifically optimized for Flux.1-Kontext-Dev for creating European supermodel portraits. 

Transform the user's prompt to follow best practices:
1. Be specific about facial features, lighting, and composition
2. Include technical photography terms for professional quality
3. Optimize for European supermodel aesthetic
4. Keep the prompt focused and efficient for the model
5. Maintain the original intent while enhancing detail

Return ONLY the optimized prompt, no explanations."

    local optimized_prompt
    optimized_prompt=$(ollama run mistral <<EOF
System: ${system_prompt}

User: ${input_prompt}
EOF
)
    
    if [[ -n "${optimized_prompt}" ]]; then
        log "✨ Prompt optimized successfully"
        echo "${optimized_prompt}"
    else
        warn "Ollama optimization failed, using original prompt"
        echo "${input_prompt}"
    fi
}

# ============================================================================
# MODEL MANAGEMENT
# ============================================================================

check_models() {
    log "🔍 Checking required models..."
    
    local missing_models=()
    
    # Check flux-kontext model
    if [[ ! -f "${COMFYUI_DIR}/models/diffusion_models/flux1-dev-kontext_fp8_scaled.safetensors" ]]; then
        missing_models+=("flux1-dev-kontext_fp8_scaled.safetensors")
    fi
    
    # Check text encoders
    if [[ ! -f "${COMFYUI_DIR}/models/text_encoders/clip_l.safetensors" ]]; then
        missing_models+=("clip_l.safetensors")
    fi
    
    if [[ ! -f "${COMFYUI_DIR}/models/text_encoders/t5xxl_fp8_e4m3fn_scaled.safetensors" ]]; then
        missing_models+=("t5xxl_fp8_e4m3fn_scaled.safetensors")
    fi
    
    # Check VAE
    if [[ ! -f "${COMFYUI_DIR}/models/vae/ae.safetensors" ]]; then
        missing_models+=("ae.safetensors")
    fi
    
    if [[ ${#missing_models[@]} -gt 0 ]]; then
        warn "Missing models detected:"
        for model in "${missing_models[@]}"; do
            echo "  - ${model}"
        done
        echo
        echo "Run 'install-models' command to download missing models."
        return 1
    fi
    
    log "✅ All required models present"
    return 0
}

install_models() {
    log "📥 Installing flux-kontext models..."
    
    mkdir -p "${COMFYUI_DIR}/models/diffusion_models"
    mkdir -p "${COMFYUI_DIR}/models/text_encoders"
    mkdir -p "${COMFYUI_DIR}/models/vae"
    
    log "Downloading flux1-dev-kontext_fp8_scaled.safetensors..."
    wget -O "${COMFYUI_DIR}/models/diffusion_models/flux1-dev-kontext_fp8_scaled.safetensors" \
        "https://huggingface.co/Comfy-Org/flux1-kontext-dev_ComfyUI/resolve/main/split_files/diffusion_models/flux1-dev-kontext_fp8_scaled.safetensors"
    
    log "Downloading text encoders..."
    wget -O "${COMFYUI_DIR}/models/text_encoders/clip_l.safetensors" \
        "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors"
    
    wget -O "${COMFYUI_DIR}/models/text_encoders/t5xxl_fp8_e4m3fn_scaled.safetensors" \
        "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp8_e4m3fn_scaled.safetensors"
    
    log "Downloading VAE..."
    wget -O "${COMFYUI_DIR}/models/vae/ae.safetensors" \
        "https://huggingface.co/Comfy-Org/Lumina_Image_2.0_Repackaged/resolve/main/split_files/vae/ae.safetensors"
    
    log "✅ Models installed successfully"
}

# ============================================================================
# WORKFLOW MANAGEMENT
# ============================================================================

generate_workflow() {
    local prompt="$1"
    local seed="${2:-$DEFAULT_SEED}"
    local batch="${3:-$DEFAULT_BATCH}"
    local steps="${4:-$DEFAULT_STEPS}"
    local cfg="${5:-$DEFAULT_CFG}"
    local width="${6:-$DEFAULT_WIDTH}"
    local height="${7:-$DEFAULT_HEIGHT}"
    
    log "🎨 Generating workflow configuration..."
    
    # Copy base workflow
    local workflow_file="${OUTPUT_DIR}/current_workflow.json"
    cp "${WORKFLOW_DIR}/${FLUX_KONTEXT_BASIC}" "${workflow_file}"
    
    # Update workflow with parameters using jq
    if command -v jq &> /dev/null; then
        # Update prompt (Node 6 - CLIPTextEncode)
        jq --arg prompt "$prompt" '.nodes[] | select(.id == 6) | .widgets_values[0] = $prompt' "${workflow_file}" > "${workflow_file}.tmp"
        mv "${workflow_file}.tmp" "${workflow_file}"
        
        # Update CFG (Node 35 - FluxGuidance) 
        jq --arg cfg "$cfg" '.nodes[] | select(.id == 35) | .widgets_values[0] = ($cfg | tonumber)' "${workflow_file}" > "${workflow_file}.tmp"
        mv "${workflow_file}.tmp" "${workflow_file}"
        
        # Update seed and steps (Node 31 - KSampler)
        if [[ "$seed" != "randomize" ]]; then
            jq --arg seed "$seed" --arg steps "$steps" '.nodes[] | select(.id == 31) | .widgets_values[0] = ($seed | tonumber) | .widgets_values[2] = ($steps | tonumber) | .widgets_values[1] = "fixed"' "${workflow_file}" > "${workflow_file}.tmp"
            mv "${workflow_file}.tmp" "${workflow_file}"
        else
            jq --arg steps "$steps" '.nodes[] | select(.id == 31) | .widgets_values[2] = ($steps | tonumber) | .widgets_values[1] = "randomize"' "${workflow_file}" > "${workflow_file}.tmp"
            mv "${workflow_file}.tmp" "${workflow_file}"
        fi
        
        log "✅ Workflow configured successfully"
    else
        warn "jq not found. Using template workflow without parameter updates."
    fi
    
    echo "${workflow_file}"
}

# ============================================================================
# GENERATION PIPELINE
# ============================================================================

run_generation() {
    local workflow_file="$1"
    
    log "🚀 Starting ComfyUI generation..."
    
    cd "${COMFYUI_DIR}"
    
    # Activate virtual environment and run ComfyUI
    source "${VENV_PATH}"
    
    python main.py --workflow "${workflow_file}" --output-directory "${OUTPUT_DIR}"
    
    log "✅ Generation completed"
    
    # Show latest output
    local latest_output
    latest_output=$(find "${OUTPUT_DIR}" -name "*.png" -o -name "*.jpg" -o -name "*.webp" | sort -t '_' -k2 -nr | head -n1)
    
    if [[ -n "${latest_output}" ]]; then
        log "📸 Latest output: ${latest_output}"
        
        # Optional: Open with default image viewer
        if command -v xdg-open &> /dev/null; then
            xdg-open "${latest_output}" 2>/dev/null &
        fi
    fi
}

# ============================================================================
# GIT VERSIONING
# ============================================================================

git_commit_milestone() {
    local message="$1"
    
    if [[ ! -d "${SCRIPT_DIR}/.git" ]]; then
        log "🔧 Initializing git repository..."
        git init "${SCRIPT_DIR}"
        git add .
        git commit -m "Initial ComfyUI flux-kontext setup"
    fi
    
    log "📝 Committing milestone: ${message}"
    git add .
    git commit -m "${message}" || warn "Git commit failed or no changes"
}

git_tag_version() {
    local version="$1"
    
    log "🏷️ Tagging version: ${version}"
    git tag -a "v${version}" -m "Pipeline milestone v${version}" || warn "Git tagging failed"
}

# ============================================================================
# MAIN COMMANDS
# ============================================================================

show_help() {
    cat << EOF
ComfyUI CLI Control Panel - Flux-Kontext Workflow
==================================================

COMMANDS:
  generate      Generate images with flux-kontext
  install-models Install required FP8 Kontext models  
  check-models  Verify all models are installed
  smoke-test    Run comprehensive generation tests
  clean-old     Safely prune old GGUF files
  status        Show system and model status
  help          Show this help message

GENERATE OPTIONS:
  -p, --prompt      Image generation prompt (required)
  -s, --seed        Seed for reproducibility (default: randomize)
  -b, --batch       Number of images to generate (default: 1)  
  -t, --steps       Diffusion steps (default: 20)
  -c, --cfg         CFG guidance scale (default: 2.5)
  -w, --width       Image width (default: 1024)
  -h, --height      Image height (default: 1024)
  --no-ollama       Skip prompt optimization with Ollama

EXAMPLES:
  $0 generate -p "European supermodel, professional headshot"
  $0 generate -p "Portrait photography" -s 123456 -b 4 -t 30
  $0 install-models
  $0 smoke-test

Node ID Reference (flux-kontext workflow):
  Node 3: Prompt (CLIPTextEncode)
  Node 6: CFG (FluxGuidance) 
  Node 7: Batch (varies by workflow)
  Node 8: Steps (KSampler)

EOF
}

cmd_generate() {
    local prompt=""
    local seed="$DEFAULT_SEED"
    local batch="$DEFAULT_BATCH"
    local steps="$DEFAULT_STEPS"
    local cfg="$DEFAULT_CFG"
    local width="$DEFAULT_WIDTH"
    local height="$DEFAULT_HEIGHT"
    local use_ollama=true
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -p|--prompt)
                prompt="$2"
                shift 2
                ;;
            -s|--seed)
                seed="$2"
                shift 2
                ;;
            -b|--batch)
                batch="$2"
                shift 2
                ;;
            -t|--steps)
                steps="$2"
                shift 2
                ;;
            -c|--cfg)
                cfg="$2"
                shift 2
                ;;
            -w|--width)
                width="$2"
                shift 2
                ;;
            -h|--height)
                height="$2"
                shift 2
                ;;
            --no-ollama)
                use_ollama=false
                shift
                ;;
            *)
                error "Unknown option: $1"
                ;;
        esac
    done
    
    if [[ -z "${prompt}" ]]; then
        error "Prompt is required. Use -p or --prompt"
    fi
    
    # Check dependencies and models
    check_dependencies
    if ! check_models; then
        error "Required models are missing. Run 'install-models' first."
    fi
    
    # Optimize prompt if Ollama is available
    local optimized_prompt="$prompt"
    if [[ "$use_ollama" == true ]]; then
        optimized_prompt=$(optimize_prompt_with_ollama "$prompt")
    fi
    
    log "📋 Generation Parameters:"
    echo "  Prompt: ${optimized_prompt}"
    echo "  Seed: ${seed}"
    echo "  Batch: ${batch}"
    echo "  Steps: ${steps}"
    echo "  CFG: ${cfg}"
    echo "  Resolution: ${width}x${height}"
    echo
    
    # Create output directory
    mkdir -p "${OUTPUT_DIR}"
    
    # Generate workflow
    local workflow_file
    workflow_file=$(generate_workflow "$optimized_prompt" "$seed" "$batch" "$steps" "$cfg" "$width" "$height")
    
    # Run generation
    run_generation "$workflow_file"
    
    # Commit milestone
    git_commit_milestone "Generated: $(echo "$optimized_prompt" | cut -c1-50)..."
}

cmd_install_models() {
    log "🔧 Installing flux-kontext models..."
    check_dependencies
    install_models
    git_commit_milestone "Installed flux-kontext FP8 models"
    log "✅ Model installation completed"
}

cmd_check_models() {
    check_dependencies
    if check_models; then
        log "✅ All models are properly installed"
    else
        error "Some models are missing"
    fi
}

cmd_smoke_test() {
    log "🧪 Running comprehensive smoke tests..."
    
    check_dependencies
    if ! check_models; then
        error "Models missing. Run 'install-models' first."
    fi
    
    # Test prompts for European supermodel generation
    local test_prompts=(
        "Professional headshot of a European supermodel, studio lighting"
        "Portrait photography, elegant pose, soft natural lighting"
        "High fashion model, editorial style, minimalist background"
    )
    
    log "Running ${#test_prompts[@]} test generations..."
    
    for i in "${!test_prompts[@]}"; do
        log "Test $((i+1))/${#test_prompts[@]}: ${test_prompts[$i]}"
        
        local workflow_file
        workflow_file=$(generate_workflow "${test_prompts[$i]}" "$((123456 + i))" 1 10 2.5 512 512)
        
        run_generation "$workflow_file"
        sleep 2  # Brief pause between generations
    done
    
    git_commit_milestone "Completed smoke tests - all systems operational"
    git_tag_version "smoke-test-$(date +%Y%m%d_%H%M%S)"
    
    log "✅ Smoke tests completed successfully"
}

cmd_clean_old() {
    log "🧹 Safely pruning old files..."
    
    local output_count
    output_count=$(find "${OUTPUT_DIR}" -name "*.png" -o -name "*.jpg" -o -name "*.webp" | wc -l)
    
    if [[ $output_count -gt 50 ]]; then
        warn "Found $output_count output files. Keeping latest 50..."
        find "${OUTPUT_DIR}" -name "*.png" -o -name "*.jpg" -o -name "*.webp" | sort -t '_' -k2 -nr | tail -n +51 | xargs rm -f
        log "✅ Old outputs cleaned"
    fi
    
    # Clean any GGUF files if present (as mentioned in rules)
    local gguf_files
    gguf_files=$(find "${COMFYUI_DIR}" -name "*.gguf" 2>/dev/null)
    if [[ -n "$gguf_files" ]]; then
        warn "Found GGUF files - these may be safe to remove:"
        echo "$gguf_files"
    fi
    
    git_commit_milestone "Cleaned old files and performed maintenance"
}

cmd_status() {
    log "📊 System Status Report"
    echo
    
    echo "📁 Directories:"
    echo "  ComfyUI: ${COMFYUI_DIR}"
    echo "  Workflows: ${WORKFLOW_DIR}"  
    echo "  Output: ${OUTPUT_DIR}"
    echo
    
    echo "🧠 AI Services:"
    if command -v ollama &> /dev/null; then
        echo "  Ollama: ✅ Available"
        ollama list 2>/dev/null | head -5
    else
        echo "  Ollama: ❌ Not installed"
    fi
    echo
    
    echo "🎯 Models Status:"
    if check_models &>/dev/null; then
        echo "  Core Models: ✅ All installed"
    else  
        echo "  Core Models: ❌ Missing (run install-models)"
    fi
    
    local lora_count
    lora_count=$(find "${COMFYUI_DIR}/models/loras" -name "*.safetensors" 2>/dev/null | wc -l)
    echo "  LoRAs: $lora_count files"
    
    echo
    
    echo "📈 Recent Activity:"
    if [[ -d "${OUTPUT_DIR}" ]]; then
        local recent_count
        recent_count=$(find "${OUTPUT_DIR}" -name "*.png" -o -name "*.jpg" -o -name "*.webp" -mtime -1 2>/dev/null | wc -l)
        echo "  Images generated today: $recent_count"
        
        local latest_output
        latest_output=$(find "${OUTPUT_DIR}" -name "*.png" -o -name "*.jpg" -o -name "*.webp" 2>/dev/null | sort -t '_' -k2 -nr | head -n1)
        if [[ -n "$latest_output" ]]; then
            echo "  Latest output: $(basename "$latest_output")"
        fi
    fi
    
    echo
    echo "💾 Hardware:"
    if command -v nvidia-smi &> /dev/null; then
        nvidia-smi --query-gpu=name,memory.total,memory.used --format=csv,noheader,nounits
    else
        echo "  GPU: Not detected or nvidia-smi not available"
    fi
}

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

main() {
    if [[ $# -eq 0 ]]; then
        show_help
        exit 0
    fi
    
    case "$1" in
        generate)
            shift
            cmd_generate "$@"
            ;;
        install-models)
            cmd_install_models
            ;;
        check-models)
            cmd_check_models
            ;;
        smoke-test)
            cmd_smoke_test
            ;;
        clean-old)
            cmd_clean_old
            ;;
        status)
            cmd_status
            ;;
        help)
            show_help
            ;;
        *)
            error "Unknown command: $1. Use 'help' to see available commands."
            ;;
    esac
}

# Run main function
main "$@"