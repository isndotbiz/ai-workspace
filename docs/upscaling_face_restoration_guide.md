# Upscaling & Face Restoration Guide

## Overview

This guide covers the new upscaling and face restoration capabilities added to your AI workspace. These tools enable you to transform 1024x1024 portraits into stunning 4096x4096 images with enhanced facial details.

## Models Installed

### Upscaling Models (145 MB total)
Located in: `ComfyUI/models/upscale_models/`

1. **RealESRGAN_x4plus.pth** (64 MB)
   - General purpose 4x upscaling
   - Best for: Photorealistic portraits, natural images
   - Quality: Excellent for most use cases

2. **RealESRGAN_x4plus_anime_6B.pth** (18 MB)
   - Specialized for anime and illustrations
   - Best for: Stylized art, drawn characters
   - Quality: Optimized for non-photorealistic content

3. **4x-UltraSharp.pth** (64 MB)
   - High-quality general purpose upscaling
   - Best for: Maximum sharpness and detail
   - Quality: Premium option for critical work

### Face Restoration Models (692 MB total)
Located in: `ComfyUI/models/facerestore_models/`

1. **GFPGANv1.4.pth** (333 MB)
   - Advanced face restoration and enhancement
   - Strength: Excellent for fixing artifacts
   - Use case: Primary face restoration tool

2. **codeformer.pth** (360 MB)
   - State-of-the-art face reconstruction
   - Strength: Best for severely degraded faces
   - Use case: When GFPGAN isn't enough

## Available Workflows

### 1. Basic 4x Upscaling
**File**: `workflows/flux_kontext_fp8_upscale_4x.json`

**Pipeline**:
```
Flux Kontext Generation (1024x1024)
    ↓
RealESRGAN 4x Upscaling
    ↓
Save Image (4096x4096)
```

**Settings**:
- Steps: 10
- CFG: 6.0
- Batch size: 1
- Generation time: ~2 minutes

**Use case**: When you need high-resolution output without face enhancement

### 2. Ultimate Portrait Pipeline
**File**: `workflows/flux_kontext_ultimate_portrait.json`

**Pipeline**:
```
Flux Kontext + Realism LoRA (1024x1024)
    ↓
RealESRGAN 4x Upscaling (4096x4096)
    ↓
GFPGAN Face Restoration
    ↓
Save Final Image
```

**Settings**:
- Steps: 12 (quality focused)
- CFG: 3.5
- Realism LoRA: 0.7 strength
- Generation time: ~3-4 minutes
- VRAM usage: 12-14GB peak

**Use case**: Professional portraits requiring maximum quality

## Performance Characteristics

### RTX 4060 Ti 16GB Performance

| Pipeline | Resolution | Time | VRAM Peak | Quality |
|----------|------------|------|-----------|---------|
| Base Generation | 1024x1024 | 90-110s | 8-10GB | Excellent |
| + 4x Upscale | 4096x4096 | +30-40s | +2-3GB | Superb |
| + Face Restore | 4096x4096 | +10-15s | +1-2GB | Ultimate |
| **Total** | **4096x4096** | **~3-4min** | **12-14GB** | **Production** |

### Memory Optimization Tips

1. **Batch Size**: Keep at 1 for 4x upscaling
2. **Close Other Apps**: Free up VRAM before starting
3. **Monitor VRAM**: Use `nvidia-smi` to watch usage
4. **Sequential Processing**: For multiple images, process one at a time

## Usage Examples

### Quick Test
```bash
# Activate environment
source activate_workspace.sh

# Start ComfyUI
cqg

# In another terminal, queue the upscaling workflow
python ultra_portrait_gen.py \
  --workflow flux_kontext_fp8_upscale_4x.json \
  "elegant Ukrainian businesswoman"
```

### Ultimate Quality Portrait
```bash
# Queue the complete pipeline
python ultra_portrait_gen.py \
  --workflow flux_kontext_ultimate_portrait.json \
  "sophisticated European executive portrait"
```

### Batch Upscaling (from existing images)
If you have base 1024x1024 portraits already generated:

1. Open ComfyUI web interface at `http://localhost:8188`
2. Load workflow: `flux_kontext_fp8_upscale_4x.json`
3. Replace the generation nodes with "Load Image" node
4. Connect to upscaling pipeline
5. Queue multiple images

## Troubleshooting

### Out of VRAM Error

**Symptom**: ComfyUI crashes during upscaling or face restoration

**Solutions**:
1. Close other GPU applications
2. Reduce batch size to 1
3. Use `--lowvram` flag when starting ComfyUI:
   ```bash
   python ComfyUI/main.py --lowvram
   ```
4. Process images one at a time
5. Restart ComfyUI to clear memory fragmentation

### Poor Face Restoration Quality

**Symptom**: Face looks overly smooth or artificial

**Solutions**:
1. Try CodeFormer instead of GFPGAN
2. Adjust `codeformer_fidelity` parameter (0.3-0.7 range)
3. Use lower strength face restoration
4. Generate base image with higher steps (14-16) before upscaling

### Upscaling Takes Too Long

**Symptom**: 4x upscaling takes over 2 minutes

**Solutions**:
1. Check VRAM usage - might be swapping to system RAM
2. Verify GPU utilization with `nvidia-smi`
3. Ensure CUDA is properly configured
4. Try a different upscale model (anime variant is faster)

### Artifacts in Upscaled Image

**Symptom**: Strange patterns or noise in output

**Solutions**:
1. Use higher steps in base generation (12-16)
2. Try 4x-UltraSharp model instead of RealESRGAN
3. Increase CFG slightly for more coherent base image
4. Apply face restoration to fix facial artifacts

## Node Reference

### UpscaleModelLoader Node
```json
{
  "inputs": {
    "upscale_model_name": "RealESRGAN_x4plus.pth"
  }
}
```
Options:
- `RealESRGAN_x4plus.pth`
- `RealESRGAN_x4plus_anime_6B.pth`
- `4x-UltraSharp.pth`

### ImageUpscaleWithModel Node
```json
{
  "inputs": {
    "upscale_model": ["loader_node_id", 0],
    "image": ["source_image_node_id", 0]
  }
}
```

### FaceRestoreModelLoader Node
```json
{
  "inputs": {
    "facerestore_model_name": "GFPGANv1.4.pth"
  }
}
```
Options:
- `GFPGANv1.4.pth` (recommended)
- `codeformer.pth` (more aggressive)

### FaceRestoreWithModel Node
```json
{
  "inputs": {
    "facerestore_model": ["loader_node_id", 0],
    "image": ["source_image_node_id", 0],
    "facedetection": "retinaface_resnet50",
    "codeformer_fidelity": 0.5
  }
}
```

Parameters:
- `facedetection`: Detection algorithm (retinaface_resnet50 recommended)
- `codeformer_fidelity`: 0.0-1.0 (higher = more faithful to original)

## Best Practices

### For Production Portraits

1. **Use the Ultimate Pipeline**: `flux_kontext_ultimate_portrait.json`
2. **Higher Steps**: 12-16 for base generation
3. **Realism LoRA**: 0.6-0.8 strength
4. **Face Restoration**: GFPGAN at default settings
5. **Test First**: Always generate one before batch processing

### For Experimentation

1. **Start with 4x Upscale Only**: Test upscaling without face restoration
2. **Compare Models**: Try different upscale models side-by-side
3. **Iterate**: Generate base, upscale, evaluate, regenerate if needed
4. **Document Settings**: Keep notes on what works best

### For Batch Processing

1. **Generate Base Images First**: 1024x1024 at optimal settings
2. **Review Before Upscaling**: Check quality of base images
3. **Process in Small Batches**: 3-5 images at a time
4. **Monitor VRAM**: Watch for memory issues
5. **Save Checkpoints**: Keep both base and upscaled versions

## File Size Expectations

### Output Sizes
- Base 1024x1024 PNG: ~2-3 MB
- Upscaled 4096x4096 PNG: ~15-25 MB
- With face restoration: +2-5 MB

### Storage Planning
- 100 base portraits: ~250 MB
- 100 upscaled portraits: ~2 GB
- **Recommendation**: Keep 50-100GB free for active projects

## Testing Your Setup

Run the validation script:
```bash
python test_upscale_face_models.py
```

Expected output: **6/6 tests passing (100%)**

Tests verify:
- ✓ Upscaling model files present and correct size
- ✓ Face restoration model files present
- ✓ Custom nodes installed (Impact Pack, Ultimate SD Upscale)
- ✓ Workflow files created
- ✓ Model integrity (file readable and valid)
- ✓ Sufficient disk space

## Next Steps

1. **Test the Workflows**: Generate a few portraits to verify everything works
2. **Experiment with Parameters**: Try different upscale models and settings
3. **Create Custom Workflows**: Adapt the examples to your specific needs
4. **Monitor Performance**: Track generation times and VRAM usage
5. **Document Results**: Note which combinations work best for your use cases

## Advanced: Custom Workflow Creation

To create your own upscaling + face restoration workflow:

1. Start with `flux_kontext_fp8_turbo.json` as base
2. Add `UpscaleModelLoader` node (Node 11)
3. Add `ImageUpscaleWithModel` node (Node 12)
4. Connect VAE Decode output to upscaling input
5. Optionally add `FaceRestoreModelLoader` (Node 14)
6. Optionally add `FaceRestoreWithModel` (Node 15)
7. Add `SaveImage` nodes at intermediate stages
8. Test and iterate

## Support and Resources

- **Test Script**: `test_upscale_face_models.py`
- **Workflows Directory**: `workflows/`
- **Documentation**: This file + `WARP.md`
- **Model Paths**: Check `ComfyUI/models/upscale_models/` and `facerestore_models/`

Your workspace is now fully equipped for professional-grade portrait upscaling and face enhancement! 🚀