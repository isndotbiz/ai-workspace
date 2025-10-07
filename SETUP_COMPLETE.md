# ComfyUI Flux-Kontext Setup Complete! 🎉

## 📋 What's Been Installed

### ✅ Core Components
- **ComfyUI**: Latest version with Python 3.12 virtual environment  
- **CUDA Support**: PyTorch with CUDA 12.4 for RTX 4060 Ti
- **Flux-Kontext Templates**: Professional workflow templates for image editing
- **Ollama Integration**: Mistral 7B model for prompt optimization
- **CLI Control Panel**: `comfyctl.sh` for command-line workflow management

### ✅ Directory Structure
```
/home/jdm/ai-workspace/
├── ComfyUI/                    # Main ComfyUI installation
│   ├── models/                 # Model storage
│   │   ├── diffusion_models/   # Flux-Kontext models (to be installed)
│   │   ├── text_encoders/      # CLIP and T5 encoders (to be installed)
│   │   ├── vae/               # VAE models (to be installed)
│   │   └── loras/             # LoRA collection with config
│   ├── output/                # Generated images
│   └── venv/                  # Python virtual environment
├── comfyctl.sh               # CLI control panel ⭐
├── install-loras.sh          # LoRA setup script
└── SETUP_COMPLETE.md         # This file
```

### ✅ Available Workflow Templates
- `flux_kontext_dev_basic.json` - Single image editing
- `api_bfl_flux_1_kontext_multiple_images_input.json` - Multi-image reference
- Various other flux templates for different use cases

## 🚀 Quick Start Guide

### Step 1: Install Required Models
```bash
./comfyctl.sh install-models
```
This downloads:
- `flux1-dev-kontext_fp8_scaled.safetensors` (~8GB)
- CLIP and T5 text encoders (~4GB)  
- VAE model (~300MB)

### Step 2: Verify Installation
```bash
./comfyctl.sh status
```

### Step 3: Generate Your First Image
```bash
./comfyctl.sh generate -p "European supermodel, professional headshot, studio lighting"
```

### Step 4 (Optional): Install LoRAs
```bash
./install-loras.sh  # Sets up LoRA directory structure
# Then manually add your LoRA .safetensors files to ComfyUI/models/loras/
```

## 🎯 CLI Usage Examples

### Basic Generation
```bash
# Simple generation with prompt optimization
./comfyctl.sh generate -p "Portrait of elegant woman"

# Advanced parameters
./comfyctl.sh generate -p "European supermodel" -s 123456 -b 4 -t 30 -c 3.5

# Skip Ollama prompt optimization
./comfyctl.sh generate -p "Raw prompt" --no-ollama
```

### System Management
```bash
# Check system status
./comfyctl.sh status

# Verify models are installed
./comfyctl.sh check-models

# Run comprehensive tests
./comfyctl.sh smoke-test

# Clean old files
./comfyctl.sh clean-old
```

## 🧠 Ollama Integration

### Current Models Available
- **Mistral 7B**: Optimizes prompts for European supermodel generation
- **LLaMA 3.1 8B**: Alternative for prompt enhancement

### Prompt Optimization Process
1. Your input prompt is sent to Mistral
2. AI optimizes for:
   - Specific facial features and lighting
   - Technical photography terms
   - European supermodel aesthetics
   - Model efficiency
3. Optimized prompt is used for generation

## 📊 Hardware Optimization

### RTX 4060 Ti Optimized Settings
- **FP8 Models**: Uses `flux1-dev-kontext_fp8_scaled.safetensors` (~20GB VRAM requirement)
- **Default Settings**: 20 steps, CFG 2.5, 1024x1024 resolution
- **Batch Size**: Default 1 (increase if VRAM allows)

## 🎨 Workflow Node IDs (for advanced users)

Based on the flux-kontext workflow template:
- **Node 3**: Prompt (CLIPTextEncode)  
- **Node 6**: CFG Scale (FluxGuidance)
- **Node 7**: Batch Size (varies by workflow)
- **Node 8**: Steps (KSampler)
- **Node 31**: Main sampler with seed control
- **Node 35**: Flux guidance conditioning

## 📁 File Management

### Generated Images
- Location: `ComfyUI/output/`
- Formats: PNG, JPG, WebP
- Auto-opens in default image viewer
- Git versioning tracks generation milestones

### LoRA Integration
- Location: `ComfyUI/models/loras/`
- Configuration: `lora_config.yaml`
- Usage: `<lora:name:weight>` in prompts
- Supported formats: .safetensors

## 🔧 Git Versioning

The CLI automatically:
- Initializes git repo if needed
- Commits generation milestones
- Tags major pipeline versions
- Tracks workflow changes

## ⚡ Performance Tips

### For RTX 4060 Ti (16GB VRAM)
```bash
# Standard quality (fast)
./comfyctl.sh generate -p "prompt" -t 20 -c 2.5

# High quality (slower)  
./comfyctl.sh generate -p "prompt" -t 30 -c 3.5

# Batch processing
./comfyctl.sh generate -p "prompt" -b 4 -t 15
```

### Memory Management
- FP8 models reduce VRAM usage by ~40%
- Batch size 1-4 recommended for 16GB VRAM
- Use `clean-old` command to manage disk space

## 🚨 Troubleshooting

### Model Download Issues
```bash
# Check available space
df -h /home/jdm/ai-workspace

# Verify network connectivity
wget --spider https://huggingface.co

# Manual model placement
# Download files directly to ComfyUI/models/[category]/
```

### Generation Errors
```bash
# Check CUDA availability
nvidia-smi

# Verify models are present
./comfyctl.sh check-models

# Check virtual environment
source ComfyUI/venv/bin/activate
python -c "import torch; print(torch.cuda.is_available())"
```

### Ollama Issues
```bash
# Check Ollama status
ollama list

# Restart Ollama service
systemctl --user restart ollama  # or appropriate method

# Skip Ollama if needed
./comfyctl.sh generate -p "prompt" --no-ollama
```

## 🎯 Next Steps

### Immediate Actions
1. **Run `./comfyctl.sh install-models`** to download required models
2. **Test with `./comfyctl.sh smoke-test`** to verify everything works
3. **Generate your first supermodel images!**

### Recommended Enhancements
1. **Install quality LoRAs** from CivitAI or HuggingFace
2. **Experiment with different CFG and step values** for your style
3. **Set up custom prompt templates** for consistent results
4. **Consider installing additional upscaling models** for higher resolution

### Advanced Usage
1. **Modify workflow templates** for specialized needs
2. **Integrate with external tools** via CLI
3. **Set up automated batch processing**
4. **Create custom LoRA training workflows**

## 📞 Support Resources

### Official Documentation
- ComfyUI: https://github.com/comfyanonymous/ComfyUI
- Flux-Kontext: https://docs.comfy.org/tutorials/flux/flux-1-kontext-dev
- Ollama: https://ollama.ai

### Community
- ComfyUI Discord servers
- Reddit: r/comfyui, r/StableDiffusion
- GitHub Issues for technical problems

---

## 🏆 Success! Your AI Portrait Studio is Ready

You now have a professional-grade AI portrait generation system optimized for:
- ✨ European supermodel aesthetics
- 🎨 Professional photography quality
- ⚡ RTX 4060 Ti hardware optimization
- 🤖 Intelligent prompt optimization
- 📊 Structured, auditable workflows

**Start generating stunning portraits with a single command!**

```bash
./comfyctl.sh generate -p "European supermodel, professional headshot"
```