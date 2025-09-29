#!/bin/bash
# Start ComfyUI Server
# ====================

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting ComfyUI Server...${NC}"

# Navigate to workspace
cd /home/jdm/ai-workspace

# Activate environment
echo -e "${YELLOW}📦 Activating environment...${NC}"
source venv/bin/activate

# Set environment variables for optimal RTX 4060 Ti performance
export CUDA_VISIBLE_DEVICES=0
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:1024

# Check if ComfyUI is already running
if lsof -i:8188 > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  ComfyUI appears to be already running on port 8188${NC}"
    echo -e "${BLUE}🌐 Access it at: http://localhost:8188${NC}"
    exit 0
fi

# Start ComfyUI
echo -e "${GREEN}✨ Starting ComfyUI server on http://localhost:8188${NC}"
echo -e "${BLUE}💡 Press Ctrl+C to stop the server${NC}"
echo -e "${BLUE}🎨 Load your workflow from the workflows/ directory${NC}"
echo ""

python ComfyUI/main.py --listen 0.0.0.0 --port 8188