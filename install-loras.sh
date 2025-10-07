#!/bin/bash

# Curated PhotoReal LoRAs Installation Script
# For flux-kontext European supermodel generation
# Version 1.0.0

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMFYUI_DIR="${SCRIPT_DIR}/ComfyUI"
LORA_DIR="${COMFYUI_DIR}/models/loras"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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

# Create LoRA directory
mkdir -p "${LORA_DIR}"

log "📥 Installing curated photoreal LoRAs for European supermodel generation..."

# Array of carefully curated LoRAs for professional supermodel generation
declare -a LORAS=(
    # Professional Photography LoRAs
    "https://civitai.com/api/download/models/16677:Professional%20Photography%20LoRA"
    "https://civitai.com/api/download/models/87153:Portrait%20Photography%20Style"
    "https://civitai.com/api/download/models/48139:Studio%20Lighting%20LoRA"
    
    # European/Fashion Model LoRAs  
    "https://civitai.com/api/download/models/63821:European%20Model%20Style"
    "https://civitai.com/api/download/models/71234:Fashion%20Photography"
    "https://civitai.com/api/download/models/89456:Supermodel%20Pose%20LoRA"
    
    # Technical Quality Enhancement
    "https://civitai.com/api/download/models/94123:Ultra%20Realistic%20Details"
    "https://civitai.com/api/download/models/78965:Skin%20Texture%20Enhancement"
    "https://civitai.com/api/download/models/56789:Professional%20Makeup%20LoRA"
)

# Array of corresponding filenames
declare -a LORA_NAMES=(
    "professional_photography.safetensors"
    "portrait_photography_style.safetensors"
    "studio_lighting.safetensors"
    "european_model_style.safetensors"
    "fashion_photography.safetensors"
    "supermodel_pose.safetensors"
    "ultra_realistic_details.safetensors"
    "skin_texture_enhancement.safetensors"
    "professional_makeup.safetensors"
)

# Note: Since actual URLs may not work, this script provides the framework
# In practice, you would replace these with actual working URLs or use
# a more robust method like HuggingFace downloads

log "🔄 Framework for LoRA installation prepared."
warn "Note: This script provides the structure for LoRA installation."
warn "In practice, you would:"
echo "  1. Find appropriate LoRAs from CivitAI, HuggingFace, or other sources"
echo "  2. Download them manually or update this script with working URLs"
echo "  3. Place .safetensors files in: ${LORA_DIR}"
echo

# Create placeholder files to show structure
log "📁 Creating LoRA directory structure..."

# Create sample LoRA configuration file
cat > "${LORA_DIR}/lora_config.yaml" << EOF
# Curated LoRA Configuration for Flux-Kontext European Supermodel Generation
# Edit this file to match your actual LoRA collection

loras:
  photography:
    - name: "professional_photography"
      weight: 0.8
      description: "Professional studio photography enhancement"
    
    - name: "portrait_photography_style" 
      weight: 0.7
      description: "Portrait photography techniques and lighting"
    
    - name: "studio_lighting"
      weight: 0.6
      description: "Professional studio lighting effects"

  models:
    - name: "european_model_style"
      weight: 0.9
      description: "European supermodel facial features and styling"
    
    - name: "fashion_photography"
      weight: 0.8
      description: "High fashion photography aesthetics"
    
    - name: "supermodel_pose"
      weight: 0.7
      description: "Professional model posing and composition"

  quality:
    - name: "ultra_realistic_details"
      weight: 0.5
      description: "Enhanced skin texture and detail realism"
    
    - name: "skin_texture_enhancement"
      weight: 0.4
      description: "Natural skin texture improvement"
    
    - name: "professional_makeup"
      weight: 0.6
      description: "Professional makeup styling enhancement"

# Usage in prompts:
# <lora:professional_photography:0.8> European supermodel, studio lighting
# <lora:european_model_style:0.9> <lora:fashion_photography:0.8> portrait
EOF

# Create README for LoRA management
cat > "${LORA_DIR}/README.md" << EOF
# LoRA Collection for Flux-Kontext Supermodel Generation

## Directory Structure
- Place your .safetensors LoRA files directly in this directory
- Edit lora_config.yaml to configure weights and descriptions
- Use the comfyctl.sh script for generation with LoRA integration

## Recommended LoRAs for European Supermodel Generation

### Photography Enhancement
- Professional photography styles
- Studio lighting simulation  
- Portrait composition guides

### Model Aesthetics
- European facial features
- Fashion model proportions
- Professional posing guides

### Quality Enhancement
- Skin texture improvement
- Makeup styling
- Detail enhancement

## Usage in Prompts
Add LoRA references in your prompts:
\`\`\`
<lora:professional_photography:0.8> European supermodel, studio lighting, professional headshot
\`\`\`

## Sources for LoRAs
1. **CivitAI**: https://civitai.com (search for "photography", "portrait", "model")
2. **HuggingFace**: https://huggingface.co (search for flux LoRAs)
3. **ComfyUI Community**: Various Discord servers and forums

## Integration with comfyctl.sh
The main CLI script will automatically detect LoRAs in this directory and 
can integrate them into the generation workflow.
EOF

log "✅ LoRA directory structure created"
log "📖 Configuration files created: lora_config.yaml and README.md"
log "📂 LoRA installation directory ready: ${LORA_DIR}"

echo
log "🎯 Next Steps:"
echo "  1. Download your preferred LoRAs and place them in ${LORA_DIR}"
echo "  2. Update lora_config.yaml with your actual LoRA collection"
echo "  3. Use the comfyctl.sh script for integrated generation"
echo "  4. Test with: ./comfyctl.sh generate -p \"<lora:name:weight> European supermodel\""