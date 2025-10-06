# How to Use Multi-Image ComfyUI Workflows

## 🚀 Quick Start

### 1. Start ComfyUI
```bash
cd ~/ai-workspace/ComfyUI
python main.py --listen 0.0.0.0 --port 8188
```
Open browser: `http://localhost:8188`

### 2. Load Multi-Image Workflow
- **Option A**: Import the JSON templates from `~/ai-workspace/tests/`
- **Option B**: Build from your existing workflows using multi-image nodes

## 🔗 Multi-Image Chaining Workflow

**Purpose**: Use multiple reference images for consistent identity + background control

### Setup Steps:
1. **Load Base Workflow**: Start with your existing flux-kontext workflow
2. **Add Multi-Image Nodes**:
   - `Load Image` nodes (one for each reference image)
   - `Image Batch` node to combine them
   - `Kontext Apply` node to process the batch
   - Connect to your existing nodes 3,6,7,8 (Prompt, CFG, Batch, Steps)

### Node Configuration:
```
Node 3 (Prompt): "portrait of [subject], [scene description]"
Node 6 (CFG): 3.0-4.0 (lower for multi-image)
Node 7 (Batch): 1-4 images
Node 8 (Steps): 28-36 steps
```

### Example Use Cases:
- **Character Consistency**: Same person in different poses/outfits
- **Style Transfer**: Apply one image's style to another's composition
- **Background Replacement**: Keep subject, change environment

## 🧩 Multi-Image Stitching Workflow

**Purpose**: Combine multiple images into complex compositions

### Setup Steps:
1. **Preparation**: Have 2-4 source images ready
2. **Load Stitching Workflow**: Import the stitching template
3. **Configure Nodes**:
   - Multiple `Load Image` nodes
   - `Image Resize` nodes (consistent dimensions)
   - `Kontext Compose` node for blending
   - Higher CFG guidance (3.5-4.5)

### Recommended Settings:
- **Resolution**: 1024x1024 (square works best)
- **Steps**: 32-40 (more steps for complex compositions)
- **Memory**: Use sequential processing to avoid VRAM issues

## 🎛️ CLI Control with comfyctl.sh

Your control panel script integrates with multi-image workflows:

```bash
# Run the control panel
cd ~/ai-workspace && ./comfyctl.sh

# Use Ollama to expand prompts for multi-image
./comfyctl.sh  # Select option 9
# Enter: "two people in cyberpunk setting, one standing one sitting"
```

## 🧠 Ollama Prompt Optimization

For multi-image workflows, optimize prompts like this:

```bash
cd ~/ai-workspace
./scripts/prompt_helper.sh mistral:7b "combine portrait of warrior princess with fantasy castle background"
```

The AI will expand it to technical photography terms perfect for flux-kontext.

## ⚙️ Node ID Reference (Your Workflow)

Based on your flux-kontext setup:
- **Node 3**: Prompt input
- **Node 6**: CFG Guidance Scale
- **Node 7**: Batch Size (number of images)
- **Node 8**: Diffusion Steps

## 🎨 Practical Examples

### Example 1: Character in Multiple Scenes
1. Load 3 images: character portrait, indoor scene, outdoor scene
2. Prompt: "elegant woman in [scene], professional photography, studio lighting"
3. CFG: 3.5, Steps: 32, Batch: 2

### Example 2: Style Transfer
1. Load 2 images: reference style image, target composition
2. Prompt: "apply artistic style of [reference] to [composition], detailed, masterpiece"
3. CFG: 4.0, Steps: 36, Batch: 1

### Example 3: Complex Composition
1. Load 4 images: background, character, props, lighting reference
2. Use stitching workflow with sequential processing
3. Higher steps (35-40) for clean blending

## 🔧 Troubleshooting

### VRAM Issues
- Reduce batch size to 1
- Use FP8 models (already installed)
- Enable sequential processing

### Poor Blending
- Increase CFG guidance (up to 4.5)
- Add more diffusion steps
- Use consistent resolution across inputs

### Identity Loss
- Lower CFG guidance (down to 3.0)
- Use stronger LoRA weights (0.7-0.8)
- Add identity keywords to prompt

## 📁 File Locations

- **Workflows**: `~/ai-workspace/tests/Flux-Kontext-Multi-*.json`
- **Models**: `~/ai-workspace/ComfyUI/models/`
- **Output**: `~/ai-workspace/ComfyUI/output/`
- **Control Script**: `~/ai-workspace/comfyctl.sh`

## 🚀 Advanced Usage

### Automated Multi-Image Generation
```bash
# Use your existing workflow with multi-image setup
cd ~/ai-workspace
echo "t" | ./comfyctl.sh  # Run Ukrainian test with multiple variations
```

### Custom Multi-Image Pipeline
1. Create custom JSON workflow combining your nodes 3,6,7,8
2. Add multi-image processing nodes
3. Save as new workflow template
4. Integrate with comfyctl.sh for CLI control

Ready to create stunning multi-image compositions with your flux-kontext setup! 🎨