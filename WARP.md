# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Repository Overview

This is an AI development workspace optimized for RTX 4060 Ti 16GB, focusing on high-quality portrait generation using Flux.1-dev with ComfyUI and GGUF quantization. The system includes automated prompt expansion via Ollama and optimized workflows for fast, professional portrait generation.

## Quick Start Commands

```bash
# Activate the workspace environment
source activate_workspace.sh

# Start ComfyUI with GPU acceleration
cqg

# Start all services (ComfyUI + Ollama)
flux_start  # (after sourcing warp_shortcuts.sh)

# Generate a single portrait
./ultra_portrait_gen.py "Ukrainian wealth muse"

# Generate multiple variations
./ultra_portrait_gen.py --variations 2 "financial goddess"

# Interactive generation mode
./ultra_portrait_gen.py --interactive

# Check system status
python workspace_cli.py server status

# Run comprehensive tests
python test_comprehensive.py
```

## Essential Development Commands

### Environment Management
- `source activate_workspace.sh` - Activate Python virtual environment with all aliases
- `source warp_shortcuts.sh` - Load ultra-fast CLI shortcuts for portrait generation
- `ws` - Navigate to workspace root
- `wf` - Navigate to workflows directory

### Service Management
- `flux_start` - Start ComfyUI and Ollama services
- `flux_stop` - Stop all services
- `flux_restart` - Restart all services
- `flux_status` - Check system and service status

### Image Generation
- `flux_gen "concept"` - Quick single portrait generation
- `flux_batch "concept1" "concept2" "concept3"` - Batch generation
- `flux_variations 2 "concept"` - Generate multiple variations
- `flux_interactive` - Interactive generation mode

### Testing and Maintenance
- `flux_test` - Run comprehensive system tests (96.9% success rate)
- `flux_models` - Check model file status and integrity
- `flux_view` - View recently generated images
- `flux_clean [days]` - Clean old images (default: 30 days)
- `flux_gpu` - Monitor GPU usage with nvidia-smi

## Architecture Overview

### Core Pipeline
The system implements a two-stage AI pipeline:

1. **Prompt Expansion**: Ollama (Llama 3.1 8B) expands short concepts into detailed Flux-optimized prompts
2. **Image Generation**: ComfyUI with GGUF-quantized Flux.1-dev model generates high-quality portraits

### Data Flow
```
User Concept → Ollama Expansion → ComfyUI Workflow → GGUF Flux.1-dev → Portrait Image
```

### Technology Stack
- **AI Models**: Flux.1-dev GGUF (Q3_K_S quantized, 4.9GB)
- **Text Encoders**: CLIP-L (235MB) + T5-XXL GGUF (2.0GB) 
- **Prompt AI**: Llama 3.1 8B via Ollama
- **Backend**: ComfyUI with GGUF custom nodes
- **Performance**: 90-120 seconds per 1024x1024 image, ~6-8GB VRAM usage

### Directory Structure
```
/
├── ComfyUI/                    # ComfyUI installation (submodule)
│   ├── models/
│   │   ├── diffusion_models/   # GGUF Flux.1-dev model
│   │   ├── clip/              # CLIP-L and T5-XXL encoders
│   │   ├── vae/               # VAE decoder
│   │   └── loras/             # Detail enhancement LoRAs
│   ├── custom_nodes/          # GGUF and other custom nodes
│   └── output/                # Generated images
├── workflows/                 # ComfyUI workflow JSON files
├── venv/                      # Python virtual environment
├── ultra_portrait_gen.py      # Main portrait generator script
├── workspace_cli.py           # Workspace management CLI
├── warp_shortcuts.sh          # Fast CLI shortcuts
└── activate_workspace.sh      # Environment activation
```

## Key Workflow Files

### Primary Workflows
- `flux_fast_gguf_portrait.json` - Ultra-optimized GGUF portrait workflow (main)
- `flux_balanced_quality.json` - Balanced speed/quality workflow
- `flux_ultra_quality.json` - Maximum quality workflow (slower)
- `flux_turbo_4step.json` - Ultra-fast 4-step generation

### Specialized Workflows  
- `luxury_entrepreneur_portrait.json` - Business/professional presets
- `apex_executive_portrait.json` - Corporate executive styling
- `enigmatic_patroness_portrait.json` - Artistic/sophisticated styling

### Performance Optimization

**RTX 4060 Ti 16GB Optimized Settings:**
```json
{
  "steps": 10,           // Reduced from 16 for speed
  "cfg": 2.0,           // Lower for faster convergence  
  "sampler": "euler",   // Fast, reliable sampler
  "scheduler": "simple", // Minimal overhead
  "resolution": "1024x1024", // High quality
  "batch_size": 1       // Optimal for 16GB VRAM
}
```

**Memory Management:**
- GGUF Quantization reduces model size by 60%
- Smart CPU/GPU offloading
- Efficient batch processing
- LoRA strength: 0.6-0.8 for balanced enhancement

## Service Configuration

### Default Ports
- **ComfyUI**: localhost:8188
- **Ollama**: localhost:11434

### Environment Variables
Set in activate_workspace.sh:
```bash
WORKSPACE_ROOT="/home/jdm/ai-workspace"
COMFYUI_PATH="$WORKSPACE_ROOT/ComfyUI"
WORKFLOWS_PATH="$WORKSPACE_ROOT/workflows" 
CUDA_VISIBLE_DEVICES=0
PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:1024
```

## Testing and Quality Assurance

### System Testing
- `python test_comprehensive.py` - Full system test suite (96.9% success rate)
- `python test_models.py` - Model integrity verification
- `python workspace_cli.py server status` - Health check

### Performance Benchmarks
| Setting | Generation Time | Quality | VRAM Usage |
|---------|----------------|---------|------------|
| 8 steps | 60-75s | Good | 5.5GB |
| 10 steps | 75-90s | Very Good | 6.0GB |
| 12 steps | 90-110s | Excellent | 6.5GB |

## Troubleshooting

### Common Issues

**ComfyUI server not running:**
```bash
pkill -f "ComfyUI/main.py"
./start_comfyui.sh
curl http://localhost:8188/system_stats  # Test connection
```

**Ollama not accessible:**
```bash
ollama serve &
ollama list
ollama run prompter "test"
```

**Out of VRAM errors:**
- Reduce batch size or resolution
- Use `--lowvram` flag: `python ComfyUI/main.py --lowvram`
- Monitor usage: `nvidia-smi`
- Close other GPU applications

**Generation timeout:**
- Check VRAM usage with `nvidia-smi`
- Reduce steps in workflow (8-12 optimal)
- Use batch mode for multiple images
- Restart ComfyUI if memory fragmented

### Health Checks
```bash
# Service status
curl http://localhost:8188/system_stats
curl http://localhost:11434/api/tags

# GPU availability
python -c "import torch; print(torch.cuda.is_available())"
nvidia-smi

# Model verification
python workspace_cli.py models info
ls -la ComfyUI/models/diffusion_models/flux1-dev-Q3_K_S.gguf
```

## Git Workflow

### Automatic Exclusions
- Model files (*.safetensors, *.gguf, *.ckpt) are excluded from Git
- Generated outputs are excluded
- Virtual environment and cache files excluded

### Sync to GitHub
```bash
./sync_to_github.sh "Your commit message"
# Or use shortcut after sourcing warp_shortcuts.sh
flux_sync "Your commit message"
```

## Advanced Usage

### Custom Workflow Creation
1. Copy existing workflow JSON from `workflows/`
2. Modify parameters using ComfyUI web interface
3. Export and save as new workflow
4. Test with `ultra_portrait_gen.py --workflow your_workflow.json`

### Batch Processing
```bash
# Preset concept series
flux_trio        # Generate apex/patroness/adventurer
flux_finance     # Generate wealth/goddess/entrepreneur  
flux_exotic      # Generate exotic motivator series

# Custom batch with variations
./ultra_portrait_gen.py --variations 3 --batch "concept1" "concept2" "concept3"
```

### Performance Monitoring
```bash
flux_gpu         # Real-time GPU monitoring
flux_logs comfyui # View ComfyUI logs
flux_logs ollama  # View Ollama logs
```

This workspace is production-ready and optimized for ultra-fast, high-quality portrait generation using state-of-the-art AI models on RTX 4060 Ti hardware.