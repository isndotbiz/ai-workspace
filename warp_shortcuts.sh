#!/bin/bash
"""
🎨 WARP SHORTCUTS FOR ULTRA LUXURY PORTRAIT GENERATOR 🎨
========================================================
Ultra-fast CLI shortcuts optimized for Warp terminal

Usage:
  source warp_shortcuts.sh  # Load all shortcuts
  flux_gen "concept"         # Quick single generation
  flux_batch "c1" "c2" "c3"  # Batch generation
  flux_status                # System status check
"""

# ============================================================================
# CORE SHORTCUTS
# ============================================================================

# Quick single portrait generation
flux_gen() {
    if [ $# -eq 0 ]; then
        echo "🎨 Usage: flux_gen \"concept\""
        echo "   Example: flux_gen \"Ukrainian wealth muse\""
        return 1
    fi
    
    cd /home/jdm/ai-workspace
    source venv/bin/activate
    ./ultra_portrait_gen.py "$1"
}

# Quick batch generation
flux_batch() {
    if [ $# -eq 0 ]; then
        echo "🎨 Usage: flux_batch \"concept1\" \"concept2\" \"concept3\""
        echo "   Example: flux_batch \"financial goddess\" \"luxury entrepreneur\""
        return 1
    fi
    
    cd /home/jdm/ai-workspace
    source venv/bin/activate
    ./ultra_portrait_gen.py --batch "$@"
}

# Interactive mode shortcut
flux_interactive() {
    cd /home/jdm/ai-workspace
    source venv/bin/activate
    ./ultra_portrait_gen.py --interactive
}

# Multiple variations shortcut
flux_variations() {
    local variations=2
    if [[ $1 =~ ^[0-9]+$ ]] && [ $1 -le 3 ]; then
        variations=$1
        shift
    fi
    
    if [ $# -eq 0 ]; then
        echo "🎨 Usage: flux_variations [number] \"concept\""
        echo "   Example: flux_variations 2 \"luxury motivator\""
        return 1
    fi
    
    cd /home/jdm/ai-workspace
    source venv/bin/activate
    ./ultra_portrait_gen.py --variations $variations "$@"
}

# ============================================================================
# SYSTEM MANAGEMENT
# ============================================================================

# Quick system status
flux_status() {
    cd /home/jdm/ai-workspace
    source venv/bin/activate
    
    echo "🔍 System Status Check..."
    python workspace_cli.py server status
    echo
    
    # Check recent generations
    echo "📸 Recent Generations:"
    ls -latr ComfyUI/output/*.png 2>/dev/null | tail -5 | while read line; do
        echo "   $line"
    done
}

# Start all services
flux_start() {
    cd /home/jdm/ai-workspace
    echo "🚀 Starting all services..."
    
    # Start ComfyUI if not running
    if ! curl -s http://localhost:8188/system_stats >/dev/null; then
        echo "   Starting ComfyUI..."
        source venv/bin/activate
        nohup python ComfyUI/main.py --listen 0.0.0.0 --port 8188 > comfyui_server.log 2>&1 &
        sleep 10
    fi
    
    # Start Ollama if not running
    if ! curl -s http://localhost:11434/api/tags >/dev/null; then
        echo "   Starting Ollama..."
        nohup ollama serve > ollama.log 2>&1 &
        sleep 5
    fi
    
    echo "✅ All services started!"
    flux_status
}

# Stop all services
flux_stop() {
    cd /home/jdm/ai-workspace
    echo "🛑 Stopping all services..."
    
    pkill -f "ComfyUI/main.py" 2>/dev/null && echo "   Stopped ComfyUI"
    pkill -f "ollama serve" 2>/dev/null && echo "   Stopped Ollama"
    
    echo "✅ All services stopped!"
}

# Restart services
flux_restart() {
    flux_stop
    sleep 3
    flux_start
}

# ============================================================================
# TESTING & MAINTENANCE
# ============================================================================

# Full system test
flux_test() {
    cd /home/jdm/ai-workspace
    source venv/bin/activate
    echo "🧪 Running comprehensive system test..."
    python test_comprehensive.py
}

# Quick model check
flux_models() {
    cd /home/jdm/ai-workspace
    source venv/bin/activate
    python workspace_cli.py models info
}

# View generated images
flux_view() {
    cd /home/jdm/ai-workspace
    echo "📸 Recent images:"
    ls -latr ComfyUI/output/*.png 2>/dev/null | tail -10
    
    # Try to open in image viewer if available
    if command -v eog >/dev/null 2>&1; then
        echo "🖼️  Opening in image viewer..."
        eog ComfyUI/output/*.png 2>/dev/null &
    elif command -v feh >/dev/null 2>&1; then
        echo "🖼️  Opening in image viewer..."
        feh ComfyUI/output/*.png 2>/dev/null &
    fi
}

# Clean old images
flux_clean() {
    cd /home/jdm/ai-workspace
    local days=${1:-30}
    echo "🧹 Cleaning images older than $days days..."
    find ComfyUI/output/ -name "*.png" -mtime +$days -delete
    echo "✅ Cleanup complete!"
}

# ============================================================================
# UTILITIES
# ============================================================================

# Monitor GPU usage
flux_gpu() {
    echo "🎮 GPU Monitor (Ctrl+C to exit):"
    watch -n 1 nvidia-smi
}

# Show logs
flux_logs() {
    local service=${1:-comfyui}
    cd /home/jdm/ai-workspace
    
    case $service in
        comfyui|c)
            echo "📋 ComfyUI Logs:"
            tail -f comfyui_server.log
            ;;
        ollama|o)
            echo "📋 Ollama Logs:"
            tail -f ollama.log 2>/dev/null || echo "No Ollama log file found"
            ;;
        *)
            echo "Usage: flux_logs [comfyui|ollama]"
            ;;
    esac
}

# Git sync shortcut
flux_sync() {
    cd /home/jdm/ai-workspace
    local message=${1:-"Auto sync from Warp shortcuts"}
    ./sync_to_github.sh "$message"
}

# ============================================================================
# PRESET CONCEPTS
# ============================================================================

# Generate luxury trio
flux_trio() {
    echo "🎨 Generating luxury portrait trio..."
    flux_batch "apex executive" "enigmatic patroness" "global adventurer"
}

# Financial empowerment series
flux_finance() {
    echo "💰 Generating financial empowerment series..."
    flux_batch "Ukrainian wealth muse" "financial goddess" "luxury entrepreneur"
}

# Exotic motivator series  
flux_exotic() {
    echo "🌟 Generating exotic motivator series..."
    flux_batch "exotic motivator" "business maven" "wealth icon"
}

# ============================================================================
# HELP
# ============================================================================

flux_help() {
    cat << 'EOF'
🎨 WARP SHORTCUTS FOR ULTRA LUXURY PORTRAIT GENERATOR

GENERATION:
  flux_gen "concept"              # Single portrait
  flux_batch "c1" "c2" "c3"       # Batch generation
  flux_variations 2 "concept"     # Multiple variations
  flux_interactive                # Interactive mode

PRESETS:
  flux_trio                       # Generate apex/patroness/adventurer
  flux_finance                    # Generate wealth/goddess/entrepreneur
  flux_exotic                     # Generate exotic motivator series

SYSTEM:
  flux_start                      # Start all services
  flux_stop                       # Stop all services  
  flux_restart                    # Restart services
  flux_status                     # System status check

UTILITIES:
  flux_test                       # Full system test
  flux_models                     # Check model files
  flux_view                       # View generated images
  flux_clean [days]               # Clean old images (default: 30 days)
  flux_gpu                        # Monitor GPU usage
  flux_logs [comfyui|ollama]      # Show service logs
  flux_sync "message"             # Git sync

EXAMPLES:
  flux_gen "Ukrainian wealth muse"
  flux_batch "financial goddess" "luxury entrepreneur" 
  flux_variations 3 "exotic motivator"
  flux_clean 7   # Clean images older than 7 days
EOF
}

# ============================================================================
# INITIALIZATION
# ============================================================================

# Load shortcuts message
echo "🎨 Ultra Luxury Portrait Generator - Warp shortcuts loaded!"
echo "   Type 'flux_help' for available commands"
echo "   Quick start: flux_gen \"your concept\""

# Export functions for use in subshells
export -f flux_gen flux_batch flux_interactive flux_variations
export -f flux_status flux_start flux_stop flux_restart
export -f flux_test flux_models flux_view flux_clean
export -f flux_gpu flux_logs flux_sync
export -f flux_trio flux_finance flux_exotic flux_help