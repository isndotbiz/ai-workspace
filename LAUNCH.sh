#!/usr/bin/env bash
set -euo pipefail

# === AI WORKSPACE LAUNCH SCRIPT ===
# Your one-command solution to start the complete AI workspace

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

clear
echo -e "${PURPLE}"
cat << 'EOF'
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║   🎨 AI WORKSPACE LAUNCHER v2.0.0 🎨                                         ║
║                                                                               ║
║   Your complete AI portrait generation system is ready!                      ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

cd /home/jdm/ai-workspace

echo -e "${CYAN}🚀 What would you like to do?${NC}"
echo
echo -e "${GREEN}[1]${NC} Run automated setup (installs everything from scratch)"
echo -e "${GREEN}[2]${NC} Generate super prompts (8 persona variations with AI enhancement)"
echo -e "${GREEN}[3]${NC} Run comprehensive tests (validate entire system)" 
echo -e "${GREEN}[4]${NC} Launch existing comfyctl control panel"
echo -e "${GREEN}[5]${NC} View face swapping implementation roadmap"
echo -e "${GREEN}[6]${NC} Quick system status check"
echo
echo -e "${BLUE}[0]${NC} Exit"
echo

read -rp "Select option: " choice

case "$choice" in
    1)
        echo -e "${YELLOW}🔧 Running automated setup...${NC}"
        echo "This will install ComfyUI, models, LoRAs, Ollama, and all dependencies."
        read -rp "Continue? [Y/n]: " confirm
        if [[ "${confirm:-Y}" =~ ^[Yy]$ ]]; then
            ./auto_setup.sh
        fi
        ;;
    2)
        echo -e "${YELLOW}🎨 Generating super prompts...${NC}"
        if [ -f "venv/bin/activate" ]; then
            source venv/bin/activate
        fi
        ./super_prompts.py
        ;;
    3)
        echo -e "${YELLOW}🧪 Running comprehensive tests...${NC}"
        if [ -f "venv/bin/activate" ]; then
            source venv/bin/activate
        fi
        ./comprehensive_test_suite.py
        ;;
    4)
        echo -e "${YELLOW}🎛️  Launching comfyctl control panel...${NC}"
        ./comfyctl.sh
        ;;
    5)
        echo -e "${YELLOW}🔮 Face swapping roadmap:${NC}"
        if command -v less >/dev/null 2>&1; then
            less FACE_SWAP_IMPLEMENTATION.md
        else
            cat FACE_SWAP_IMPLEMENTATION.md
        fi
        ;;
    6)
        echo -e "${YELLOW}📊 Quick system status:${NC}"
        echo
        
        # GPU Status
        if command -v nvidia-smi >/dev/null 2>&1; then
            echo -e "${GREEN}GPU:${NC}"
            nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv,noheader,nounits | head -1
            echo
        fi
        
        # Services
        echo -e "${GREEN}Services:${NC}"
        if pgrep -f "ComfyUI" >/dev/null; then
            echo "  ✅ ComfyUI running"
        else
            echo "  ❌ ComfyUI stopped"
        fi
        
        if pgrep -x "ollama" >/dev/null; then
            echo "  ✅ Ollama running"
        else
            echo "  ❌ Ollama stopped"
        fi
        echo
        
        # Disk usage
        echo -e "${GREEN}Storage:${NC}"
        du -sh ComfyUI/models/* 2>/dev/null | sort -hr | head -5 || echo "  Models directory not found"
        echo
        
        # Git info
        if [ -d .git ]; then
            echo -e "${GREEN}Version:${NC}"
            echo "  $(git describe --tags 2>/dev/null || echo 'No tags')"
            echo "  $(git log -1 --oneline)"
        fi
        ;;
    0)
        echo -e "${CYAN}Thanks for using AI Workspace! 🎨${NC}"
        exit 0
        ;;
    *)
        echo -e "${YELLOW}Invalid option. Please try again.${NC}"
        exit 1
        ;;
esac

echo
echo -e "${CYAN}🎯 Next steps:${NC}"
echo "• Access ComfyUI at: http://localhost:8188"
echo "• Use super prompts for stunning portraits"  
echo "• Test new LoRAs with the comprehensive suite"
echo "• Explore face swapping roadmap for future features"
echo
echo -e "${PURPLE}✨ Your AI workspace is ready for professional portrait generation! ✨${NC}"