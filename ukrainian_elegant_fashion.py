#!/usr/bin/env python3

import json
import requests
import time
import random
import os
import glob

# 🌸 UKRAINIAN FLOWER HAT GIRL - ELEGANT FASHION COLLECTION 🌸
print("\n🌸 UKRAINIAN FLOWER HAT GIRL - ELEGANT FASHION COLLECTION 🌸")
print("=" * 70)

COMFY_URL = "http://localhost:8188"
OUTPUT_DIR = "ComfyUI/output"

# Fashion-focused prompts using Ollama optimization approach
FASHION_PROMPTS = [
    # Elegant Beach Fashion
    """A stunning Ukrainian woman in her late twenties with a traditional flower crown of sunflowers and cornflowers, wearing an elegant flowing beach cover-up kaftan in soft white silk over a sophisticated one-piece swimsuit, completely modest and fashionable. She stands on golden sand with ocean waves in the background, her long hair flowing in the sea breeze. Professional fashion photography lighting, high-end resort wear style, elegant and refined, masterpiece quality.""",
    
    # Traditional Ukrainian Embroidered Dress
    """An exceptionally beautiful Ukrainian woman wearing a traditional embroidered vyshyvanka dress in pristine white linen with intricate blue and yellow floral patterns, adorned with a magnificent flower crown of native wildflowers. She stands in a golden wheat field during golden hour, the traditional dress flowing elegantly around her. Authentic Ukrainian cultural fashion, professional photography, detailed embroidery work, cultural pride and beauty.""",
    
    # Summer Elegance
    """A radiant Ukrainian woman in her twenties with a vibrant flower hat crown, wearing an elegant off-shoulder summer dress in flowing light blue fabric with delicate lace details at the neckline and sleeves. She poses in a lavender field with soft romantic lighting, the dress moving gracefully in a gentle breeze. High-end fashion photography, sophisticated summer elegance, dreamy and romantic atmosphere.""",
    
    # Professional Fashion Model
    """A breathtaking Ukrainian model with a crown of mixed wildflowers, wearing a sophisticated high-fashion ensemble: a structured white blazer over a silk camisole with wide-leg linen trousers in cream. She poses confidently against a backdrop of rolling Ukrainian countryside, exuding professional elegance and poise. Editorial fashion photography, sharp professional styling, confident modeling pose, luxury fashion aesthetic.""",
    
    # Evening Elegance
    """An enchanting Ukrainian woman adorned with an elaborate flower crown of roses and baby's breath, wearing an elegant evening dress in flowing chiffon with subtle shimmer, in soft champagne color with delicate beading at the bodice. She stands in a garden setting at twilight with warm golden lighting. Formal evening wear, sophisticated elegance, red-carpet worthy styling, luxurious and refined."""
]

NEGATIVE_PROMPT = """deformed, cartoonish, extra fingers, blurry, lowres, bad skin, oversaturated, flat lighting, amateur photography, low quality, distorted anatomy, bad proportions, ugly, masculine features, weird hands, extra limbs, watermark, signature, text, logo, bad face, asymmetrical eyes, cropped, bad composition, revealing, inappropriate, sexualized"""

def create_fashion_workflow(prompt_text, seed=None, batch_size=4, width=1536, height=1536):
    """Create elegant fashion generation workflow"""
    
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
        # Fashion LoRA
        "4": {
            "inputs": {
                "lora_name": "flux_fashion.safetensors",
                "strength_model": 0.7,
                "strength_clip": 0.7,
                "model": ["1", 0],
                "clip": ["2", 0]
            },
            "class_type": "LoraLoader",
            "_meta": {"title": "Fashion LoRA"}
        },
        # Add Details LoRA
        "5": {
            "inputs": {
                "lora_name": "flux-add-details.safetensors",
                "strength_model": 0.5,
                "strength_clip": 0.5,
                "model": ["4", 0],
                "clip": ["4", 1]
            },
            "class_type": "LoraLoader",
            "_meta": {"title": "Add Details LoRA"}
        },
        # Super Realism LoRA
        "6": {
            "inputs": {
                "lora_name": "flux_super_realism.safetensors",
                "strength_model": 0.4,
                "strength_clip": 0.4,
                "model": ["5", 0],
                "clip": ["5", 1]
            },
            "class_type": "LoraLoader",
            "_meta": {"title": "Super Realism LoRA"}
        },
        "7": {
            "inputs": {
                "text": prompt_text,
                "clip": ["6", 1]
            },
            "class_type": "CLIPTextEncode",
            "_meta": {"title": "Fashion Prompt"}
        },
        "8": {
            "inputs": {
                "text": NEGATIVE_PROMPT,
                "clip": ["6", 1]
            },
            "class_type": "CLIPTextEncode",
            "_meta": {"title": "Negative Prompt"}
        },
        "9": {
            "inputs": {
                "conditioning": ["7", 0],
                "guidance": 3.5
            },
            "class_type": "FluxGuidance",
            "_meta": {"title": "CFG - Flux Guidance"}
        },
        "10": {
            "inputs": {
                "width": width,
                "height": height,
                "batch_size": batch_size
            },
            "class_type": "EmptyLatentImage",
            "_meta": {"title": "Fashion Latent"}
        },
        "11": {
            "inputs": {
                "seed": seed,
                "steps": 14,
                "cfg": 1.0,
                "sampler_name": "euler",
                "scheduler": "simple",
                "denoise": 1.0,
                "model": ["6", 0],
                "positive": ["9", 0],
                "negative": ["8", 0],
                "latent_image": ["10", 0]
            },
            "class_type": "KSampler",
            "_meta": {"title": "Fashion Sampling"}
        },
        "12": {
            "inputs": {
                "samples": ["11", 0],
                "vae": ["3", 0]
            },
            "class_type": "VAEDecode",
            "_meta": {"title": "VAE Decode"}
        },
        "13": {
            "inputs": {
                "filename_prefix": "ukrainian_flower_fashion",
                "images": ["12", 0]
            },
            "class_type": "SaveImage",
            "_meta": {"title": "Save Fashion Images"}
        }
    }
    
    return workflow

def submit_and_wait(workflow, timeout=240):
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
                if elapsed > 25 and int(elapsed) % 15 == 0:
                    print(f"   👗 Fashion processing: {elapsed:.0f}s elapsed...")
                    
                time.sleep(3)
                
            except Exception:
                time.sleep(3)
        
        print("❌ Generation timed out")
        return False
        
    except Exception as e:
        print(f"❌ Submission failed: {e}")
        return False

def generate_fashion_collection():
    """Generate elegant fashion collection"""
    print(f"\n👗 ELEGANT FASHION COLLECTION GENERATION")
    print("=" * 60)
    
    fashion_themes = [
        "Elegant Beach Fashion",
        "Traditional Ukrainian Dress", 
        "Summer Elegance",
        "Professional Fashion Model",
        "Evening Elegance"
    ]
    
    total_generated = 0
    
    for i, (theme, prompt) in enumerate(zip(fashion_themes, FASHION_PROMPTS), 1):
        print(f"\n👗 Fashion Theme {i}/5: {theme}")
        print("   • Generating 4 elegant variations...")
        print("   • Resolution: 1536x1536 (high-quality)")
        print("   • Fashion LoRA + Super Realism + Add Details")
        
        workflow = create_fashion_workflow(prompt, batch_size=4, width=1536, height=1536)
        
        if submit_and_wait(workflow, timeout=300):
            total_generated += 4
            print(f"✅ {theme} complete! Total fashion images: {total_generated}")
            
            # Brief pause between themes
            if i < len(fashion_themes):
                print("   ⏳ Preparing next fashion theme...")
                time.sleep(6)
        else:
            print(f"❌ {theme} failed!")
    
    # Show results
    fashion_files = glob.glob(f"{OUTPUT_DIR}/ukrainian_flower_fashion_*.png")
    fashion_files.sort(key=os.path.getmtime, reverse=True)
    
    print(f"\n🎉 ELEGANT FASHION COLLECTION COMPLETE!")
    print("=" * 60)
    print(f"📊 Total elegant fashion images generated: {total_generated}")
    print(f"👗 Fashion themes covered:")
    for theme in fashion_themes:
        print(f"   • {theme}")
    
    print(f"\n📁 Latest {min(8, len(fashion_files))} fashion files:")
    for i, img in enumerate(fashion_files[:8], 1):
        file_size = os.path.getsize(img) / (1024*1024)  # MB
        print(f"   {i}. {os.path.basename(img)} ({file_size:.1f}MB)")
    
    return total_generated > 0

def main():
    print("🎯 Ukrainian Flower Hat Girl - Elegant Fashion Collection")
    
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
    
    # Generate elegant fashion collection
    if not generate_fashion_collection():
        print("❌ Fashion collection generation failed!")
        return 1
    
    print("\n🎉 ELEGANT FASHION PIPELINE COMPLETE!")
    print("=" * 70)
    print("👗 Generated sophisticated Ukrainian flower hat girl fashion collection")
    print("🌸 Themes: Beach elegance, traditional dress, summer style, professional, evening wear")
    print("📐 Resolution: 1536x1536 (high-quality fashion photography)")
    print("👀 View: feh ComfyUI/output/ukrainian_flower_fashion_*.png")
    
    return 0

if __name__ == "__main__":
    exit(main())