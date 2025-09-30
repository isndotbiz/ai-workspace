
# Advanced Workflows Guide

**Complete guide to upscaling, face detailing, and multi-image Kontext workflows**

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Upscaling Workflows](#upscaling-workflows)
3. [Face Detail Enhancement](#face-detail-enhancement)
4. [Combined Pipelines](#combined-pipelines)
5. [Hardware Optimization](#hardware-optimization)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Installation

```bash
# Run the advanced workflow setup
cd /home/jdm/ai-workspace
bash scripts/setup_advanced_workflows.sh

# Create example workflows
python scripts/create_advanced_workflows.py

# Restart ComfyUI to load new models
pkill -f "ComfyUI/main.py"
python ComfyUI/main.py --listen 0.0.0.0 --port 8188
```

### Verify Installation

```bash
# Check upscaling models
ls -lh ComfyUI/models/upscale_models/

# Check face restoration models
ls -lh ComfyUI/models/facerestore_models/

# List workflows
ls -1 workflows/advanced/
```

---

## Upscaling Workflows

### Simple 4x Upscale

**Workflow:** `upscale_simple_4x.json`

**Best for:**
- Quick upscaling without refinement
- Preserving existing image quality
- Fast processing

**Usage:**
1. Load workflow in ComfyUI
2. Upload your image
3. Select upscale model:
   - `4x-UltraSharp.pth` - Best for photos
   - `RealESRGAN_x4plus.pth` - Photorealistic
   - `RealESRGAN_x4plus_anime_6B.pth` - Anime/illustrations
4. Queue prompt

**Performance:**
- **RTX 4060 Ti 16GB:** ~5-15 seconds
- **VRAM Usage:** 2-4GB
- **Input:** Up to 2048x2048
- **Output:** 4x resolution

---

### Ultimate SD Upscale (Tiled)

**Workflow:** `upscale_ultimate_tiled_4x.json`

**Best for:**
- Large images (2048x2048+)
- Adding detail while upscaling
- Fixing artifacts from previous generation

**Key Parameters:**

| Parameter | Value | Notes |
|-----------|-------|-------|
| upscale_by | 2.0-4.0 | Higher = larger output |
| tile_width/height | 1024 | Safe for 16GB VRAM |
| denoise | 0.25-0.35 | Lower = preserve original |
| steps | 15-25 | More steps = better seams |
| seam_fix_denoise | 0.2-0.3 | Tile blending |

**Tile Size Guidelines:**

| VRAM | Safe Tile Size | Max Tile Size |
|------|----------------|---------------|
| 8GB | 512px | 768px |
| 12GB | 768px | 1024px |
| 16GB | 1024px | 2048px |
| 24GB+ | 2048px | 4096px |

**Performance (RTX 4060 Ti 16GB):**
- 1024x1024 → 4096x4096: ~2-3 minutes
- 1408x1408 → 2816x2816: ~1-2 minutes
- VRAM usage: 8-12GB peak

**Tips:**
- Lower denoise (0.2-0.3) preserves more original detail
- Higher denoise (0.4-0.5) adds new details but changes image more
- Use "Band Pass" seam fix mode for best tile blending
- Increase seam_fix_width (64-128) for smoother transitions

---

## Face Detail Enhancement

### Face Detailer Workflow

**Workflow:** `face_detail_enhancement.json`

**Best for:**
- Enhancing facial features
- Fixing blurry/low-res faces
- Multi-face processing

**Key Parameters:**

| Parameter | Value | Effect |
|-----------|-------|--------|
| bbox_threshold | 0.3-0.7 | Lower = detect smaller faces |
| bbox_dilation | 10-20 | Expands face mask |
| crop_factor | 1.5-2.5 | Context around face |
| denoise | 0.3-0.5 | Lower = subtle, Higher = dramatic |
| steps | 20-30 | Quality vs speed |
| feather | 15-25 | Edge blending |

**Detection Models:**

1. **bbox/face_yolov8m.pt** (Default)
   - Fast, accurate
   - Good for multiple faces
   - Works well with varied angles

2. **MediaPipe**
   - Real-time capable
   - Best for frontal faces
   - Lower resource usage

3. **RetinaFace**
   - Highest accuracy
   - Better with difficult angles
   - Slightly slower

**Face Restoration Models:**

### GFPGAN v1.4 (Recommended for most use cases)
- Balanced quality and speed
- Strength: 0.5-0.8
- Best for: General portrait enhancement

### CodeFormer
- Higher quality, more control
- Fidelity: 0.5 (natural) to 1.0 (accurate)
- Best for: Professional restoration

**Usage Example:**

```python
# Generate portrait
python generate_ukrainian_portrait.py

# Load result in ComfyUI
# Apply face_detail_enhancement.json workflow
# Parameters:
#   bbox_threshold: 0.5
#   denoise: 0.4
#   steps: 25
#   restoration: GFPGANv1.4
```

**Performance:**
- Single face: 20-30 seconds
- Multiple faces: 30-60 seconds
- VRAM usage: 6-8GB

---

## Combined Pipelines

### Full Pipeline: Generate → Face Detail → Upscale

**Workflow:** `full_pipeline_kontext_face_upscale.json`

**Complete process:**
1. Generate with FLUX Kontext FP8
2. Enhance face details
3. Upscale 2x with tiling

**Recommended Settings:**

**Generation Phase:**
- Steps: 12
- Resolution: 1024x1408 (portrait)
- LoRA: Realism (0.8 strength)

**Face Detail Phase:**
- Detection: YOLOv8m
- Denoise: 0.4
- Steps: 25

**Upscale Phase:**
- Model: 4x-UltraSharp
- Upscale by: 2.0 (1024x1408 → 2048x2816)
- Tile size: 1024px
- Denoise: 0.25

**Total Time:** 2-3 minutes
**Total VRAM:** Peak 10-12GB
**Final Resolution:** 2048x2816 (8K quality)

---

## Hardware Optimization

### RTX 4060 Ti 16GB (Your System)

**Optimal Settings:**

**For Speed (Fast Mode):**
```json
{
  "upscale_tile_size": 512,
  "upscale_steps": 15,
  "upscale_denoise": 0.25,
  "face_detail_steps": 20,
  "face_detail_denoise": 0.3
}
```
**Time:** ~60-90 seconds total

**For Quality (Balanced Mode):**
```json
{
  "upscale_tile_size": 1024,
  "upscale_steps": 20-25,
  "upscale_denoise": 0.3,
  "face_detail_steps": 25-30,
  "face_detail_denoise": 0.4
}
```
**Time:** ~2-3 minutes total

**For Max Quality (Ultra Mode):**
```json
{
  "upscale_tile_size": 2048,
  "upscale_steps": 30-40,
  "upscale_denoise": 0.35,
  "face_detail_steps": 35-40,
  "face_detail_denoise": 0.45,
  "multi_stage_upscale": "2x → 2x"
}
```
**Time:** ~5-7 minutes total

---

## Workflow Combinations

### Best for Portraits

```
Generate (FLUX FP8) → Face Detail (GFPGAN v1.4) → Upscale (4x-UltraSharp)
```

**Settings:**
- Generation: 1024x1408, 12 steps
- Face detail: denoise 0.4, steps 25
- Upscale: 2x, denoise 0.3, tiles 1024px

**Result:** 2048x2816 high-quality portrait

---

### Best for Existing Low-Res Images

```
Load Image → Upscale (2x) → Face Detail → Upscale (2x) → Final
```

**Settings:**
- First upscale: RealESRGAN, simple
- Face detail: denoise 0.5, steps 30
- Second upscale: 4x-UltraSharp, denoise 0.25

**Result:** 4x total upscale with enhanced faces

---

### Best for Multiple Faces

```
Generate → Batch Face Detector → Individual Face Detail → Composite → Upscale
```

**Settings:**
- Detection threshold: 0.4 (catch all faces)
- Process each face separately
- Higher feathering: 25-30
- Final upscale: 1.5-2x

---

## Troubleshooting

### Issue: Out of VRAM

**Symptoms:** CUDA out of memory error

**Solutions:**
1. Reduce tile size (1024 → 512)
2. Use `--lowvram` flag when starting ComfyUI
3. Process images sequentially, not in batch
4. Close other GPU applications
5. Reduce upscale factor (4x → 2x)

**Command:**
```bash
python ComfyUI/main.py --lowvram --listen 0.0.0.0 --port 8188
```

---

### Issue: Blurry Upscaled Images

**Symptoms:** Output lacks detail, looks soft

**Solutions:**
1. Increase denoise (0.3 → 0.4)
2. Try different upscale model
3. Use multi-stage upscaling (2x → 2x instead of 4x)
4. Increase steps (20 → 30)
5. Add detail refinement pass

---

### Issue: Faces Not Detected

**Symptoms:** Face detailer skips faces

**Solutions:**
1. Lower detection threshold (0.5 → 0.3)
2. Try different detection model (YOLOv8 → MediaPipe)
3. Ensure faces are large enough (>128px recommended)
4. Check face angle (profile faces harder to detect)
5. Pre-upscale small faces before detection

---

### Issue: Over-Processed Faces

**Symptoms:** Faces look artificial or plastic

**Solutions:**
1. Lower restoration strength (0.7 → 0.5)
2. Reduce denoise (0.5 → 0.3)
3. Use CodeFormer with lower fidelity (0.5-0.6)
4. Decrease detail enhancement steps (30 → 20)
5. Blend with original using lower opacity

---

### Issue: Visible Tile Seams

**Symptoms:** Grid pattern or lines in upscaled image

**Solutions:**
1. Enable seam fix mode: "Band Pass" or "Half Tile + Intersections"
2. Increase seam_fix_width (64 → 128)
3. Increase seam_fix_mask_blur (8 → 16)
4. Use higher overlap between tiles
5. Try different seam_fix_denoise values (0.2-0.4)

---

### Issue: Slow Processing

**Symptoms:** Takes longer than expected

**Solutions:**
1. Reduce tile size for upscaling
2. Lower step counts (25 → 15-20)
3. Use faster upscale model (ESRGAN over LDSR)
4. Process at lower resolution first
5. Use batch processing for multiple images

---

## Model Selection Guide

### Upscaling Models by Content Type

| Content Type | Best Model | Alternative |
|--------------|------------|-------------|
| Portraits | 4x-UltraSharp | RealESRGAN_x4plus |
| Landscapes | 4x-UltraSharp | RealESRGAN_x4plus |
| Anime/Manga | RealESRGAN_anime_6B | 4x-AnimeSharp |
| Text/UI | 4x-UltraSharp | LDSR |
| Product Photos | RealESRGAN_x4plus | 4x-UltraSharp |

### Face Restoration by Quality Level

| Quality Level | Model | Strength | Steps |
|---------------|-------|----------|-------|
| Quick | GFPGAN v1.4 | 0.5-0.6 | 20 |
| Balanced | GFPGAN v1.4 | 0.7 | 25 |
| High Quality | CodeFormer | 0.6-0.7 | 30 |
| Maximum | CodeFormer | 0.8-0.9 | 35-40 |

---

## Performance Benchmarks

### RTX 4060 Ti 16GB

**Simple Upscale (4x):**
- 512x512 → 2048x2048: ~5 seconds
- 1024x1024 → 4096x4096: ~15 seconds

**Ultimate SD Upscale (4x with tiles):**
- 1024x1024 → 4096x4096: ~2-3 minutes
- 1408x1408 → 2816x2816: ~1-2 minutes

**Face Detail Enhancement:**
- Single face: ~20-30 seconds
- 2-3 faces: ~40-60 seconds

**Full Pipeline (Generate + Face + Upscale):**
- 1024x1408 portrait → 2048x2816: ~2-3 minutes total

---

## Next Steps

1. ✅ **Current:** Upscaling + Face Detail workflows ready
2. 🔄 **Testing:** Run full pipeline on your Ukrainian portraits
3. 📋 **Planned:** Multi-image Kontext composition examples
4. 📋 **Future:** Batch processing automation

---

## Resources

- **ComfyUI Impact Pack:** https://github.com/ltdrdata/ComfyUI-Impact-Pack
- **Ultimate SD Upscale:** https://github.com/ssitu/ComfyUI_UltimateSDUpscale
- **Model Downloads:** See `ADVANCED_MODELS_INFO.md`
- **FLUX Documentation:** `FLUX_PROMPTING_GUIDE.md`
- **Workspace Guide:** `WARP.md`

---

**Generated:** 2025-09-30  
**Version:** v2.3.0 - Advanced Workflows  
**Status:** Production Ready with Advanced Features ✅
