#!/bin/bash
# AI Workspace Activation Script
# ==============================
# This script activates the workspace virtual environment and sets up the environment

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Activating AI Workspace Environment...${NC}"

# Get the directory where this script is located
WORKSPACE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$WORKSPACE_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found. Creating one...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${YELLOW}📦 Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo -e "${YELLOW}🔧 Upgrading pip...${NC}"
pip install --upgrade pip

# Install/update requirements if needed
if [ -f "requirements.txt" ]; then
    echo -e "${YELLOW}📚 Installing/updating dependencies...${NC}"
    pip install -r requirements.txt
fi

# Set up environment variables
export WORKSPACE_ROOT="$WORKSPACE_DIR"
export COMFYUI_PATH="$WORKSPACE_DIR/ComfyUI"
export WORKFLOWS_PATH="$WORKSPACE_DIR/workflows"
export CUDA_VISIBLE_DEVICES=0
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:1024

# Add ComfyUI to Python path if it exists
if [ -d "$COMFYUI_PATH" ]; then
    export PYTHONPATH="$COMFYUI_PATH:$PYTHONPATH"
fi

# Create useful aliases
alias cq="python $COMFYUI_PATH/main.py --cpu"
alias cqg="python $COMFYUI_PATH/main.py"
alias wf="cd $WORKFLOWS_PATH"
alias ws="cd $WORKSPACE_ROOT"

# Display environment info
echo -e "${GREEN}✅ AI Workspace Environment Activated!${NC}"
echo -e "${BLUE}📍 Workspace: $WORKSPACE_DIR${NC}"
echo -e "${BLUE}🐍 Python: $(python --version)${NC}"
echo -e "${BLUE}🔥 PyTorch: $(python -c 'import torch; print(torch.__version__)' 2>/dev/null || echo 'Not installed')${NC}"
echo -e "${BLUE}🎯 CUDA Available: $(python -c 'import torch; print(torch.cuda.is_available())' 2>/dev/null || echo 'Unknown')${NC}"
echo -e "${BLUE}💾 GPU Memory: $(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1 2>/dev/null || echo 'Unknown') MB${NC}"

# Check if ComfyUI is available
if [ -d "$COMFYUI_PATH" ]; then
    echo -e "${GREEN}🎨 ComfyUI found at: $COMFYUI_PATH${NC}"
    echo -e "${BLUE}💡 Quick commands:${NC}"
    echo -e "  ${YELLOW}cqg${NC}  - Start ComfyUI with GPU"
    echo -e "  ${YELLOW}cq${NC}   - Start ComfyUI with CPU only"
    echo -e "  ${YELLOW}wf${NC}   - Navigate to workflows directory"
    echo -e "  ${YELLOW}ws${NC}   - Navigate to workspace root"
else
    echo -e "${YELLOW}⚠️  ComfyUI not found. Run the setup script to install it.${NC}"
fi

echo -e "${GREEN}🎯 Ready to start your AI development session!${NC}"