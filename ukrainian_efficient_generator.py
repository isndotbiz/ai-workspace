#!/usr/bin/env python3

import json
import requests
import time
import random
import os
import glob

# 🌻 UKRAINIAN FLOWER HAT GIRL - EFFICIENT GENERATOR 🌻
print("\n🌻 UKRAINIAN FLOWER HAT GIRL - EFFICIENT GENERATOR 🌻")
print("=" * 70)

COMFY_URL = "http://localhost:8188"
OUTPUT_DIR = "ComfyUI/output"

# Efficient prompts for different themes
EFFICIENT_PROMPTS = [
    # Original flower hat theme
    """A radiantly beautiful Ukrainian woman in her late twenties, adorned with a traditional flower crown of sunflowers, poppies, daisies, and cornflowers. She wears an elegant flowing white linen blouse and light blue skirt. Golden Ukrainian countryside with wheat fields in the background. Soft golden lighting, gentle summer breeze, natural makeup, warm brown eyes, gentle smile. High quality, photorealistic, masterpiece.""",
    
    # Elegant summer dress
    """A stunning Ukrainian woman with a vibrant flower crown, wearing an elegant off-shoulder summer dress in light blue with delicate lace details. She poses in a lavender field with soft romantic lighting. Professional fashion photography, sophisticated summer elegance, dreamy atmosphere.""",
    
    # Traditional embroidered dress  
    """A beautiful Ukrainian woman wearing a traditional white vyshyvanka dress with blue and yellow floral embroidery, adorned with a flower crown of native wildflowers. Golden wheat field setting during golden hour. Cultural authenticity, professional photography.""",
    
    # Professional elegance
    """A breathtaking Ukrainian model with a crown of mixed wildflowers, wearing a sophisticated white blazer over silk camisole with cream linen trousers. Ukrainian countryside backdrop. Editorial fashion photography, professional styling, confident pose.""",
    
    # Beach elegance
    """A stunning Ukrainian woman with sunflowers and cornflowers in her hair, wearing an elegant flowing beach cover-up in soft white silk, completely modest and fashionable. Golden sand and ocean waves background. High-end resort wear style, elegant and refined."""
]

NEGATIVE_PROMPT = """deformed, cartoonish, extra fingers, blurry, lowres, bad skin, oversaturated, flat lighting, amateur photography, low quality, distorted anatomy, bad proportions, ugly, masculine features, weird hands, extra limbs, watermark, signature, text, logo, bad face, asymmetrical eyes, cropped, bad composition"""

def create_efficient_workflow(prompt_text, seed=None, batch_size=2, width=1280, height=1280):
    """Create memory-efficient generation workflow"""
    
    if seed is None:
        seed = random.randint(1, 1000000)
    
    workflow = {
        "1": {
            "inputs": {
                "unet_name": "flux1-dev-kontext_fp8_scaled.safetensors",
                "weight_dtype": "fp8_e4m3fn"
            },
            "class_type": "UNETLoader",
            "_meta": {"title": "Load UNET - Kontext FP8"}
        },
        "2": {
            "inputs": {
                "clip_name1": "clip_l.safetensors",
                "clip_name2": "t5xxl_fp8_e4m3fn.safetensors",
                "type": "flux"
            },
            "class_type": "DualCLIPLoader",
            "_meta": {"title": "Load CLIP Models"}
        },
        "3": {
            "inputs": {
                "vae_name": "ae.safetensors"
            },
            "class_type": "VAELoader",
            "_meta": {"title": "Load VAE"}
        },
        # Single efficient LoRA
        "4": {
            "inputs": {
                "lora_name": "flux_super_realism.safetensors",
                "strength_model": 0.6,
                "strength_clip": 0.6,
                "model": ["1", 0],
                "clip": ["2", 0]
            },
            "class_type": "LoraLoader",
            "_meta": {"title": "Super Realism LoRA"}
        },
        "5": {
            "inputs": {
                "text": prompt_text,
                "clip": ["4", 1]
            },
            "class_type": "CLIPTextEncode",
            "_meta": {"title": "Efficient Prompt"}
        },
        "6": {
            "inputs": {
                "text": NEGATIVE_PROMPT,
                "clip": ["4", 1]
            },
            "class_type": "CLIPTextEncode",
            "_meta": {"title": "Negative Prompt"}
        },
        "7": {
            "inputs": {
                "conditioning": ["5", 0],
                "guidance": 3.0
            },
            "class_type": "FluxGuidance",
            "_meta": {"title": "CFG - Flux Guidance"}
        },
        "8": {
            "inputs": {
                "width": width,
                "height": height,
                "batch_size": batch_size
            },
            "class_type": "EmptyLatentImage",
            "_meta": {"title": "Efficient Latent"}
        },
        "9": {
            "inputs": {
                "seed": seed,
                "steps": 12,  # Efficient step count
                "cfg": 1.0,
                "sampler_name": "euler",
                "scheduler": "simple",
                "denoise": 1.0,
                "model": ["4", 0],
                "positive": ["7", 0],
                "negative": ["6", 0],
                "latent_image": ["8", 0]
            },
            "class_type": "KSampler",
            "_meta": {"title": "Efficient Sampling"}
        },
        "10": {
            "inputs": {
                "samples": ["9", 0],
                "vae": ["3", 0]
            },
            "class_type": "VAEDecode",
            "_meta": {"title": "VAE Decode"}
        },
        "11": {
            "inputs": {
                "filename_prefix": "ukrainian_flower_efficient",
                "images": ["10", 0]
            },
            "class_type": "SaveImage",
            "_meta": {"title": "Save Efficient Images"}
        }
    }
    
    return workflow

def submit_and_wait(workflow, timeout=180):
    """Submit workflow and wait for completion"""
    try:
        response = requests.post(f"{COMFY_URL}/prompt", json={"prompt": workflow}, timeout=10)
        if response.status_code != 200:
            print(f"❌ ComfyUI error: HTTP {response.status_code}")
            return False
        
        result = response.json()
        prompt_id = result.get('prompt_id')
        if not prompt_id:
            print("❌ No prompt ID received")
            return False
        
        print(f"✅ Generation queued: {prompt_id}")
        
        # Wait for completion
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{COMFY_URL}/history/{prompt_id}", timeout=5)
                if response.status_code == 200:
                    history = response.json()
                    if prompt_id in history and history[prompt_id].get('outputs'):
                        return True
                
                elapsed = time.time() - start_time
                if elapsed > 20 and int(elapsed) % 15 == 0:
                    print(f"   🌻 Processing: {elapsed:.0f}s elapsed...")
                    
                time.sleep(2)
                
            except Exception:
                time.sleep(2)
        
        print("❌ Generation timed out")
        return False
        
    except Exception as e:
        print(f"❌ Submission failed: {e}")
        return False

def generate_efficient_collection(target_count=10):
    """Generate collection efficiently with memory-friendly settings"""
    print(f"\n🚀 EFFICIENT COLLECTION GENERATION")
    print("=" * 60)
    print(f"🎯 Target: {target_count} additional images")
    print("📐 Resolution: 1280x1280 (GPU-friendly high-quality)")
    print("⚙️  Optimized Configuration:")
    print("   • Single Super Realism LoRA")
    print("   • Batch size: 2 (memory efficient)")  
    print("   • 12 diffusion steps")
    print("   • Various elegant themes")
    
    themes = [
        "Original Flower Hat",
        "Elegant Summer Dress",
        "Traditional Ukrainian Dress",
        "Professional Fashion",
        "Beach Elegance"
    ]
    
    total_generated = 0
    rounds_needed = (target_count + 1) // 2  # 2 images per round
    
    for round_num in range(1, rounds_needed + 1):
        if total_generated >= target_count:
            break
            
        # Rotate through themes
        theme_idx = (round_num - 1) % len(EFFICIENT_PROMPTS)
        theme_name = themes[theme_idx]
        prompt_text = EFFICIENT_PROMPTS[theme_idx]
        
        print(f"\n🌻 Round {round_num}/{rounds_needed}: {theme_name}")
        print("   • Generating 2 efficient variations...")
        print("   • Memory-optimized settings")
        
        workflow = create_efficient_workflow(prompt_text, batch_size=2, width=1280, height=1280)
        
        if submit_and_wait(workflow, timeout=180):
            total_generated += 2
            print(f"✅ {theme_name} complete! Total generated: {min(total_generated, target_count)}")
            
            # Brief pause between rounds
            if round_num < rounds_needed and total_generated < target_count:
                print("   ⏳ Brief pause...")
                time.sleep(3)
        else:
            print(f"❌ {theme_name} failed!")
    
    # Show results
    efficient_files = glob.glob(f"{OUTPUT_DIR}/ukrainian_flower_efficient_*.png")
    efficient_files.sort(key=os.path.getmtime, reverse=True)
    
    print(f"\n🎉 EFFICIENT COLLECTION COMPLETE!")
    print("=" * 60)
    print(f"📊 Total new images generated: {len(efficient_files)}")
    print(f"👗 Themes covered: {', '.join(themes)}")
    
    print(f"\n📁 Latest {min(6, len(efficient_files))} efficient files:")
    for i, img in enumerate(efficient_files[:6], 1):
        file_size = os.path.getsize(img) / (1024*1024)  # MB
        print(f"   {i}. {os.path.basename(img)} ({file_size:.1f}MB)")
    
    return len(efficient_files) > 0

def main():
    print("🎯 Ukrainian Flower Hat Girl - Efficient Generator")
    
    # Check ComfyUI status
    try:
        response = requests.get(f"{COMFY_URL}/system_stats", timeout=5)
        if response.status_code != 200:
            print("❌ ComfyUI not responding! Please start ComfyUI first.")
            return 1
    except:
        print("❌ ComfyUI not accessible! Please start ComfyUI first.")
        return 1
    
    print("✅ ComfyUI is running")
    
    # Generate efficient collection
    if not generate_efficient_collection(target_count=10):
        print("❌ Efficient collection generation failed!")
        return 1
    
    print("\n🎉 EFFICIENT GENERATION COMPLETE!")
    print("=" * 70)
    print("🌻 Generated additional Ukrainian flower hat girl variations")
    print("📐 Resolution: 1280x1280 (optimal for your GPU)")
    print("✨ Multiple elegant themes with efficient processing")
    print("👀 View: feh ComfyUI/output/ukrainian_flower_efficient_*.png")
    
    return 0

if __name__ == "__main__":
    exit(main())