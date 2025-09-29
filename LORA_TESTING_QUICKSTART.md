# 🎯 LoRA Testing Pipeline - Quick Start Guide

**Systematic LoRA evaluation with SHA256 auto-comparison for your Ukrainian portrait prompt**

## 🚀 Quick Start (3 Commands)

```bash
# 1. Start ComfyUI server
cd ~/ai-workspace/ComfyUI && python main.py --listen 0.0.0.0 --port 8188 &

# 2. Launch control panel  
cd ~/ai-workspace && ./comfyctl.sh

# 3. Select: h) Hunt & test LoRAs (advanced comparison)
```

## 🎯 What The Pipeline Does

### Phase 1: LoRA Discovery & Download
- Downloads 5 curated photorealism LoRAs from HuggingFace
- XLabs-AI/flux-RealismLora (primary base)
- Plus 4 enhancement LoRAs for texture, fashion, ultra-realism

### Phase 2: Systematic Testing  
- Tests 5 different LoRA combinations
- Uses your detailed Ukrainian girl prompt
- Generates test images with consistent settings

### Phase 3: Auto-Comparison
- SHA256 hash comparison with previous renders
- Only commits to Git when actual changes occur
- Creates baseline history for improvement tracking

## 🇺🇦 Your Target Prompt

```
A hyper-realistic portrait of a late 20s Ukrainian girl with a fair skin tone and medium-length, 
voluminous balayage haircut, featuring deeper chocolate and rich auburn tones blending into a 
dark base, styled in an intricate braided crown intertwined with delicate golden wheat stalks 
and small wildflowers. Her eyes are a bright, captivating warm brown, radiating a mix of 
heartfelt warmth and quiet strength. She wears a form-fitting, embroidered cream linen dress, 
inspired by traditional Ukrainian folk artistry with a modern twist...
```

## 📊 Test Combinations

| Combination | LoRAs | Focus |
|-------------|-------|-------|
| **base_realism** | flux_photorealism @ 0.8 | Baseline photorealism |
| **realism_plus_fashion** | photorealism @ 0.7 + fashion @ 0.4 | Clothing detail |
| **super_detailed** | photorealism @ 0.6 + super_realism @ 0.5 + fine_detailed @ 0.3 | Maximum texture |
| **ultra_realistic** | photorealism @ 0.5 + canopus_ultra @ 0.4 + fine_detailed @ 0.3 | Aggressive realism |
| **fashion_focused** | fashion @ 0.8 + photorealism @ 0.5 | Traditional dress detail |

## 🔬 Auto-Comparison Logic

```bash
# For each test render:
NEW_HASH=$(sha256sum render.png | cut -d' ' -f1)
OLD_HASH=$(sha256sum baseline.png | cut -d' ' -f1)

if [ "$NEW_HASH" = "$OLD_HASH" ]; then
    echo "⏭️ No change (skip commit)"
else
    echo "🔄 Updated render → commit to Git"
    git commit -m "Updated baseline (${NEW_HASH:0:8})"
fi
```

## 🚀 Alternative Usage Methods

### CLI Menu
```bash
./comfyctl.sh
# h) Hunt & test LoRAs 
# t) Test Ukrainian portrait only
```

### Direct Script
```bash
./lora_hunter.py  # Full automated pipeline
```

### Warp Integration
- `🎯 LoRA Hunter & Tester` - Complete workflow
- `🇺🇦 Test Ukrainian Portrait` - Single prompt test
- `📊 Compare Baseline Renders` - View history

## 📈 Expected Results

After running the pipeline:
- **5 LoRA combinations tested** systematically
- **Baseline renders saved** in `tests/baseline_renders/`
- **Git history** showing which combinations improved quality
- **JSON test report** with detailed comparison results

## 🎯 Decision Framework

**Keep LoRAs that:**
- ✅ Improve skin texture and realism
- ✅ Enhance traditional dress details
- ✅ Better capture hair texture and lighting
- ✅ Maintain anatomical accuracy

**Archive/Remove LoRAs that:**
- ❌ Cause cartoonish artifacts
- ❌ Distort facial features  
- ❌ Create unrealistic skin
- ❌ Reduce overall quality

## 📊 Performance Expectations

- **Download phase**: ~2-3 minutes (depends on connection)
- **Each test render**: ~45-60 seconds with Turbo LoRA
- **Total pipeline time**: ~15-20 minutes for all combinations
- **Memory usage**: ~8-10GB VRAM (perfect for RTX 4060 Ti)

## 🔄 Iterative Improvement

```bash
# Run initial test
./comfyctl.sh → h

# Check results  
./comfyctl.sh → t  # Test again to see if anything changed

# View comparison
git log --oneline --grep="baseline"  # See improvement history
```

## 🎭 Advanced: Custom Combinations

Edit `lora_hunter.py` to add your own test combinations:

```python
custom_combinations = {
    "my_custom_blend": {
        "flux_photorealism": 0.9,
        "flux_fashion": 0.3,
        "flux_fine_detailed": 0.2
    }
}
```

---

**🎯 Ready to find the perfect LoRA combination for your Ukrainian portrait!**