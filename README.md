# AI Workspace - Professional ComfyUI Development Environment

A comprehensive AI development workspace optimized for **RTX 4060 Ti 16GB** on Ubuntu WSL2, featuring ComfyUI, Flux.1-dev, and professional workflow management.

## 🚀 Quick Start

```bash
# Activate the workspace environment
source activate_workspace.sh

# Start ComfyUI with GPU acceleration
cqg

# Navigate to workflows
wf

# Sync to GitHub (excludes large model files)
./sync_to_github.sh "Your commit message"
```

## 📁 Directory Structure

```
ai-workspace/
├── 📄 README.md                    # This file
├── 📄 requirements.txt             # Python dependencies
├── 📄 .gitignore                   # Git ignore (excludes model files)
├── 📄 CHANGELOG.md                 # Version history
├── 🔧 activate_workspace.sh        # Environment activation script
├── 🔧 sync_to_github.sh           # GitHub sync script (smart exclusion)
├── 📁 venv/                        # Python virtual environment
├── 📁 workflows/                   # ComfyUI workflow JSON files
├── 📁 ComfyUI/                     # ComfyUI installation
│   ├── 📁 models/
│   │   ├── 📁 checkpoints/         # Flux.1-dev, SDXL models
│   │   ├── 📁 clip/                # Text encoders (CLIP, T5)
│   │   ├── 📁 vae/                 # VAE models
│   │   ├── 📁 loras/               # LoRA adaptations
│   │   ├── 📁 upscale_models/      # Super-resolution models
│   │   ├── 📁 controlnet/          # ControlNet models
│   │   └── 📁 diffusers/           # Diffusers format models
│   ├── 📁 custom_nodes/            # ComfyUI extensions
│   ├── 📁 output/                  # Generated images
│   └── 📁 input/                   # Input images
├── 📁 scripts/                     # Helper scripts
└── 📁 docs/                        # Documentation
```

## 🎯 Features

### ✅ Optimized for RTX 4060 Ti 16GB
- **CUDA 12.1** support with PyTorch
- **Memory-optimized** settings for 16GB VRAM
- **Flux.1-dev** focused workflows
- **Smart batch sizing** and resolution recommendations

### ✅ Professional Workflow Management
- **Curated Flux.1-dev workflows** for photorealistic generation
- **LoRA management** with strength optimization
- **Version-controlled workflows** (JSON tracked in Git)
- **Preset configurations** for different use cases

### ✅ Development Environment
- **Isolated Python virtual environment**
- **Comprehensive dependency management**
- **VS Code integration** with extensions
- **Jupyter notebook support** for experimentation

### ✅ Smart Git Integration
- **Large model files excluded** from Git (never uploaded to GitHub)
- **Workflow and configuration tracking**
- **Automatic changelog management**
- **One-command GitHub sync**

## 🛠️ Installation & Setup

### Prerequisites
- Ubuntu 20.04+ or WSL2 with Ubuntu
- RTX 4060 Ti 16GB (or similar CUDA GPU)
- Python 3.8+
- Git
- At least 50GB free disk space

### Initial Setup
```bash
# Clone or create your workspace
cd ~/
mkdir ai-workspace && cd ai-workspace

# Initialize git repository
git init

# Set up virtual environment
python3 -m venv venv

# Activate workspace
source activate_workspace.sh
```

## 🎨 Flux.1-dev Models & LoRAs

### Core Models (Downloaded Automatically)
- **flux1-dev.safetensors** (~11GB) - Main Flux.1-dev checkpoint
- **clip_l.safetensors** (~246MB) - CLIP text encoder
- **t5xxl_fp8_e4m3fn.safetensors** (~4.7GB) - T5 text encoder (FP8)
- **ae.safetensors** (~335MB) - Autoencoder

### Photorealistic LoRAs
- **flux-realism.safetensors** - Enhanced realism
- **flux-skin-detail.safetensors** - Improved skin textures
- **flux-cinematic.safetensors** - Cinematic lighting
- **flux-face-detail.safetensors** - Enhanced facial features

## 🖼️ Workflow Presets

### 1. Basic Photorealistic (`flux_photorealistic_basic.json`)
- Single LoRA application
- Optimal for quick generation
- **Resolution**: 1024x1024
- **Steps**: 28-36
- **CFG**: 6.5-7.5

### 2. Cinematic Chain (`flux_photorealistic_chain.json`)
- Multiple LoRA application
- Realism → Skin Detail → Cinematic
- **Best for**: Professional portraits
- **LoRA Strengths**: 0.6-0.7 range

### 3. Portrait Enhanced (`flux_photorealistic_portrait.json`)
- Face-detail focused
- All photorealistic LoRAs applied
- **Best for**: Close-up portraits
- **Higher face detail strength**: 0.7

## ⚙️ RTX 4060 Ti Optimization

### Memory Management
```python
# In ComfyUI settings
PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:1024
CUDA_VISIBLE_DEVICES=0
```

### Recommended Settings
| Resolution | Batch Size | VRAM Usage |
|------------|------------|------------|
| 1024x1024  | 1          | ~12GB      |
| 896x896    | 1          | ~9GB       |
| 768x1024   | 1          | ~10GB      |
| 1024x1024  | 2          | ~15GB      |

### Performance Tips
- Use **FP8 models** when available (T5 text encoder)
- Enable **model offloading** for complex workflows
- Use **--lowvram** flag if experiencing OOM errors
- Stick to **Flux-native LoRAs** (avoid cross-architecture mixing)

## 🔄 Git Workflow

### Automatic Exclusions (.gitignore)
✅ **Tracked in Git:**
- Workflow JSON files
- Configuration files
- Scripts and documentation
- Requirements and setup files

❌ **Excluded from Git:**
- Model files (*.safetensors, *.ckpt, etc.)
- Generated outputs
- Virtual environment
- Cache files

### Sync to GitHub
```bash
# Commit and push (models automatically excluded)
./sync_to_github.sh "Add new portrait workflow"

# Or with interactive commit message
./sync_to_github.sh
```

## 📊 Model Management

### Download Models
Models are downloaded using authenticated Hugging Face access:
```bash
# Set your HF token
export HF_TOKEN=hf_your_token_here

# Use the built-in download helper
hf_wget "https://huggingface.co/model/path" "local/path"
```

### Model Verification
```bash
# Check model sizes and integrity
ls -lh ComfyUI/models/checkpoints/
du -h ComfyUI/models/*/
```

### Model Organization
- **Keep Flux models separate** from SDXL/SD15
- **Use descriptive filenames** for LoRAs
- **Document model sources** in CHANGELOG.md

## 🚀 Usage Examples

### Start ComfyUI
```bash
# With GPU (recommended)
cqg

# CPU only (fallback)
cq

# With specific arguments
python ComfyUI/main.py --listen 0.0.0.0 --port 8188
```

### Load Workflow
1. Open ComfyUI web interface (http://localhost:8188)
2. Load workflow from `workflows/` directory
3. Adjust prompt and LoRA strengths
4. Generate images

### Development Workflow
```bash
# Activate environment
source activate_workspace.sh

# Make changes to workflows
wf
nano flux_photorealistic_custom.json

# Test changes
cqg

# Commit and sync
./sync_to_github.sh "Add custom workflow"
```

## 🛡️ Safety & Best Practices

### Security
- **Never commit model files** to public repositories
- **Use environment variables** for API keys
- **Keep HF tokens secure** in `~/.config/huggingface/token`

### Performance
- **Monitor VRAM usage** with `nvidia-smi`
- **Use appropriate batch sizes** for your GPU
- **Close unused applications** during generation

### Workflow Management
- **Test workflows** before committing
- **Document LoRA combinations** that work well
- **Keep backups** of working configurations

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and updates.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Test your changes with different workflows
4. Document any new LoRA combinations or settings
5. Submit a pull request

## 📄 License

This workspace configuration is MIT licensed. Individual models may have their own licenses.

## 🆘 Troubleshooting

### Common Issues

#### Out of Memory Errors
```bash
# Reduce batch size or resolution
# Use --lowvram flag
python ComfyUI/main.py --lowvram

# Check memory usage
nvidia-smi
```

#### Model Loading Errors
```bash
# Verify model integrity
ls -la ComfyUI/models/checkpoints/flux1-dev.safetensors

# Check file permissions
chmod 644 ComfyUI/models/**/*.safetensors
```

#### Environment Issues
```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source activate_workspace.sh
```

## 📞 Support

- **GitHub Issues**: For workspace-related problems
- **ComfyUI Community**: For ComfyUI-specific questions  
- **Flux.1-dev Documentation**: For model-specific guidance

---

**⚡ Ready to generate amazing AI art with professional workflows!**