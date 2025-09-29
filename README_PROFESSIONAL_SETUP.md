# 🎛️ Professional FLUX Kontext Pipeline

**Version-controlled, auditable AI image generation system with comprehensive testing**

## 🎯 System Overview

This is a production-ready FLUX.1-Kontext pipeline featuring:
- **Clean versioning** with Git tags for rollback capability
- **CLI control panel** for all operations (comfyctl.sh) 
- **Ollama integration** for AI-powered prompt expansion
- **Multi-image Kontext support** with face detailing
- **Photoreal LoRA curation** (Kontext-compatible)
- **Repeatable testing** at every checkpoint
- **Warp integration** for one-click operations

## 🚀 Quick Start

### 1. Launch Control Panel
```bash
cd ~/ai-workspace
./comfyctl.sh
```

### 2. Or Use Warp Integration
Access via Warp command palette or sidebar:
- `🎛️ ComfyUI Control Panel` - Full interactive menu
- `📦 Install FP8 Kontext Model` - Download main model
- `🚀 Install Turbo LoRA` - Speed optimization
- `🧪 Run Smoke Test` - Verify everything works

### 3. Complete Installation Sequence
```bash
# Run these in order via control panel:
# 1) Install FP8 Kontext Model (11.9GB)
# 2) Install Turbo LoRA (661MB) 
# 5) Curate photoreal LoRAs
# 6) Enable Ollama + Prompt Helper
# 8) Run smoke test
```

## 📁 Project Structure

```
~/ai-workspace/
├── comfyctl.sh                 # Main control panel
├── create_test_baseline.py     # Comprehensive testing
├── scripts/
│   ├── _log.sh                # Logging utilities
│   └── prompt_helper.sh       # AI prompt expansion
├── ComfyUI/
│   ├── models/
│   │   ├── diffusion_models/  # FP8 Kontext model
│   │   ├── loras/            # Turbo + photoreal LoRAs
│   │   ├── clip/             # Text encoders
│   │   └── vae/              # VAE decoder
│   └── output/               # Generated images
├── workflows/                 # ComfyUI workflow JSONs
├── tests/                     # Test reports + workflows
├── .warp/workflows/           # Warp integration
└── setup-history.log          # Auditable log
```

## 🎨 Available Models & LoRAs

### Core Models
- **FP8 Kontext** (11.9GB) - Memory-efficient main model
- **Turbo LoRA** (661MB) - 60-70% speed improvement
- **CLIP-L + T5-XXL** - Text encoders (FP8 optimized)
- **VAE** - Image decoder

### Photoreal LoRAs (Kontext-compatible)
- `kontext-make-person-real.safetensors` - "make this person look real"
- `realism-detailer-kontext.safetensors` - "Add details to this face, improve skin details"
- Browse more: [huggingface.co/collections/fal/kontext-dev-loras](https://huggingface.co/collections/fal/kontext-dev-loras)

## 🧪 Testing & Validation

### Smoke Test (Quick)
```bash
./comfyctl.sh
# Select: 8) Run smoke test
```

### Comprehensive Test (Full Pipeline)
```bash
./create_test_baseline.py v0.2.0
```

This generates a test image using:
- **Prompt**: Ultra-photoreal editorial portrait with technical specs
- **Settings**: 8 steps, CFG 5.0, Turbo LoRA @ 0.8 strength
- **Output**: Test report + generated image for validation

### Expected Performance
- **Generation Time**: 30-45 seconds (vs 90+ without turbo)
- **Memory Usage**: ~6-8GB VRAM (perfect for RTX 4060 Ti)
- **Quality**: High detail with speed optimization

## 🧠 AI Prompt Expansion

### Using Ollama (Local LLM)
```bash
# Install via control panel option 6
./scripts/prompt_helper.sh llama3.1:8b "tech entrepreneur portrait"
```

### Available Models
- **llama3.1:8b** - Detailed, context-aware (default)
- **mistral:7b** - Fast and lightweight

### Example Expansion
```
Input: "tech entrepreneur portrait"
Output: Professional portrait of a confident tech entrepreneur, 35-45 years old, 
wearing tailored navy blazer, shot with 85mm lens at f/2.8, natural studio 
lighting with subtle rim light, contemporary office background with soft bokeh, 
high resolution, photorealistic detail, confident expression...
```

## 📊 Version Control & Checkpoints

### Current Version Tags
- `v0.0.0` - Project scaffolding baseline
- `v0.1.0` - Control panel + Warp integration
- `v0.2.0` - Complete FP8 + Turbo + LoRA setup

### Create Checkpoint
```bash
# Via control panel
./comfyctl.sh
# Select: v) Create version checkpoint

# Or via Warp
# Use: 🏷️ Create Version Checkpoint
```

### View History
```bash
git log --oneline --graph
git diff v0.1.0..v0.2.0  # See changes between versions
```

## ⚡ Optimized Workflows

### 1. Turbo Speed (8 steps, ~30-45s)
- **File**: `workflows/flux_kontext_fp8_turbo.json`
- **Settings**: 8 steps, CFG 5.0, Turbo LoRA @ 0.8
- **Use case**: Fast iterations, previews

### 2. Balanced Quality (12 steps, ~60s)  
- **File**: `workflows/flux_kontext_fp8.json`
- **Settings**: 12 steps, CFG 6.0, no speed LoRA
- **Use case**: Production quality

### 3. Multi-Image Chaining
- **File**: `tests/Flux-Kontext-Multi-Image-Chaining.json`
- **Use case**: Identity + background control
- **Settings**: 28-36 steps, multiple reference images

## 🎛️ Control Panel Features

```
=== 🎛️  Comfy Control Panel (comfyctl) ===
 
1) Install FP8 Kontext Model (11.9GB, memory efficient)
2) Install Turbo LoRA (661MB, speed optimization) 
3) Install Multi-Image Kontext workflows
4) Install Face Detailer workflow + dependencies
5) Curate photoreal LoRAs (Kontext-compatible)
6) Enable Ollama + Prompt Helper (AI assistant)
7) Prune old GGUF files (cleanup, optional)
8) Run smoke test (API + models verification)
9) Expand prompt with AI (Ollama helper)
s) Show system status
v) Create version checkpoint (git tag)
0) Exit
```

## 🚨 Troubleshooting

### ComfyUI Not Starting
```bash
cd ~/ai-workspace/ComfyUI
python main.py --listen 0.0.0.0 --port 8188
# Access at: http://localhost:8188
```

### Ollama Issues
```bash
ollama serve &
ollama list
# Should show llama3.1:8b and mistral:7b
```

### Model Files Missing
```bash
./comfyctl.sh
# Select: 8) Run smoke test
# Will show which files are missing
```

### Memory Issues
- Use FP8 model (11.9GB) instead of full precision (23GB)
- Enable `--lowvram` flag in ComfyUI if needed
- Monitor with: `nvidia-smi`

## 📈 Performance Benchmarks

| Configuration | Time | Quality | VRAM | Use Case |
|--------------|------|---------|------|----------|
| **Turbo (8 steps)** | 30-45s | Good | 6GB | Fast iteration |
| **Balanced (12 steps)** | 60-75s | Very Good | 7GB | Production |
| **Quality (20 steps)** | 90-120s | Excellent | 8GB | Final output |

## 🔄 Recommended Workflow

1. **Setup** (one-time):
   ```bash
   ./comfyctl.sh
   # Run options 1, 2, 5, 6 in sequence
   ```

2. **Test baseline**:
   ```bash
   ./create_test_baseline.py
   ```

3. **Create checkpoint**:
   ```bash
   git add -A && git commit -m "Production setup complete"
   git tag v0.2.0
   ```

4. **Generate images**:
   - Launch ComfyUI: `python ComfyUI/main.py --listen 0.0.0.0 --port 8188`
   - Load workflow: `workflows/flux_kontext_fp8_turbo.json`
   - Expand prompts: `./scripts/prompt_helper.sh llama3.1:8b "your concept"`
   - Set LoRA strength: 0.8 for turbo, 0.15-0.3 for realism detailer

## 🎯 Success Criteria

✅ **API responding** - ComfyUI server accessible  
✅ **Models present** - All required files downloaded  
✅ **Generation working** - Test image created successfully  
✅ **Turbo active** - Speed improvement verified  
✅ **Ollama ready** - Prompt expansion available  
✅ **Versioned** - Git tags for rollback capability  

## 📞 Next Steps

- **Training custom LoRAs**: Use Replicate/RunPod for dataset→LoRA workflow
- **Face detailer**: Import community workflows for surgical enhancement  
- **Multi-image**: Chain reference images for complex compositions
- **Production deployment**: Scale with cloud GPU instances

---

**🚀 Your professional AI image generation pipeline is ready for production use!**