#!/usr/bin/env python3

import json
import requests
import time
import random
import os
import glob

# 🌻 UKRAINIAN FLOWER HAT GIRL - HIGH-RES GENERATION 🌻
print("\n🌻 UKRAINIAN FLOWER HAT GIRL - HIGH-RES GENERATION 🌻")
print("=" * 70)

COMFY_URL = "http://localhost:8188"
OUTPUT_DIR = "ComfyUI/output"

# Ollama-optimized prompt for maximum detail and beauty
OPTIMIZED_PROMPT = """Generate an exceptionally photorealistic and breathtaking image of a radiantly beautiful Ukrainian woman in her late twenties, adorned with a traditional flower crown made of lush wildflowers such as sunflowers, poppies, daisies, cornflowers, artfully arranged for a vibrant and captivating display. She is elegantly dressed in a flowing white linen blouse and light blue skirt that evoke the warmth of summer, creating an ethereal contrast against her golden-hued surroundings. The setting is an idyllic Ukrainian countryside, where golden wheat fields stretch out behind her, creating a picturesque backdrop that highlights the woman's natural beauty. Her long, wavy hair gently billows in the summer breeze, cascading around her as it frames her radiant face with its warm brown eyes accentuated by tasteful and subtle makeup. A gentle smile graces her lips, adding to the overall serene and inviting atmosphere of the scene. The lighting is soft yet vibrant, casting a warm golden glow that envelops both the woman and her environment, creating a romantic and dreamy ambiance. The image should exhibit impeccable anatomy, ideal proportions, high-quality details, and be rendered with such skill and finesse that it becomes a true masterpiece - an ode to traditional Ukrainian beauty and the enchanting warmth of summer."""

NEGATIVE_PROMPT = """deformed, cartoonish, extra fingers, blurry, lowres, bad skin, oversaturated, flat lighting, amateur photography, low quality, distorted anatomy, bad proportions, ugly, masculine features, weird hands, extra limbs, watermark, signature, text, logo, bad face, asymmetrical eyes, cropped, bad composition"""

def create_hires_workflow(seed=None, batch_size=4, width=2048, height=2048):
    """Create high-resolution generation workflow"""
    
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
        # First LoRA: Turbo for speed
        "4": {
            "inputs": {
                "lora_name": "FLUX.1-Turbo-Alpha.safetensors",
                "strength_model": 0.6,  # Slightly lower for high-res
                "strength_clip": 0.6,
                "model": ["1", 0],
                "clip": ["2", 0]
            },
            "class_type": "LoraLoader",
            "_meta": {"title": "Turbo LoRA"}
        },
        # Second LoRA: Add Details
        "5": {
            "inputs": {
                "lora_name": "flux-add-details.safetensors",
                "strength_model": 0.5,  # Higher for more detail at high-res
                "strength_clip": 0.5,
                "model": ["4", 0],
                "clip": ["4", 1]
            },
            "class_type": "LoraLoader",
            "_meta": {"title": "Add Details LoRA"}
        },
        # Third LoRA: Photorealism
        "6": {
            "inputs": {
                "lora_name": "flux_photorealism.safetensors",
                "strength_model": 0.4,
                "strength_clip": 0.4,
                "model": ["5", 0],
                "clip": ["5", 1]
            },
            "class_type": "LoraLoader",
            "_meta": {"title": "Photorealism LoRA"}
        },
        "7": {
            "inputs": {
                "text": OPTIMIZED_PROMPT,
                "clip": ["6", 1]
            },
            "class_type": "CLIPTextEncode",
            "_meta": {"title": "Optimized Prompt"}
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
                "guidance": 3.0  # Slightly lower for high-res
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
            "_meta": {"title": "High-Res Latent"}
        },
        "11": {
            "inputs": {
                "seed": seed,
                "steps": 16,  # More steps for high-res quality
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
            "_meta": {"title": "High-Res Sampling"}
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
                "filename_prefix": "ukrainian_flower_hires",
                "images": ["12", 0]
            },
            "class_type": "SaveImage",
            "_meta": {"title": "Save High-Res Images"}
        }
    }
    
    return workflow

def submit_and_wait(workflow, timeout=300):
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
                if elapsed > 30 and int(elapsed) % 20 == 0:
                    print(f"   🚀 High-res processing: {elapsed:.0f}s elapsed...")
                    
                time.sleep(3)
                
            except Exception:
                time.sleep(3)
        
        print("❌ Generation timed out")
        return False
        
    except Exception as e:
        print(f"❌ Submission failed: {e}")
        return False

def generate_hires_batch(rounds=5, batch_size=4, resolution=2048):
    """Generate high-resolution images directly"""
    print(f"\n🚀 HIGH-RESOLUTION GENERATION")
    print("=" * 50)
    print(f"🎯 Target: {rounds} rounds × {batch_size} images = {rounds * batch_size} total")
    print(f"📐 Resolution: {resolution}x{resolution} (4x larger than base)")
    print("⚙️  Configuration:")
    print("   • Enhanced LoRA settings for high-res")
    print("   • 16 diffusion steps for quality")
    print("   • CFG 3.0 optimized for larger images")
    print("   • Multiple quality LoRAs stacked")
    
    total_generated = 0
    
    for round_num in range(1, rounds + 1):
        print(f"\n🚀 High-Res Round {round_num}/{rounds}: Generating {batch_size} images...")
        
        workflow = create_hires_workflow(batch_size=batch_size, width=resolution, height=resolution)
        
        if submit_and_wait(workflow, timeout=400):  # Longer timeout for high-res
            total_generated += batch_size
            print(f"✅ Round {round_num} complete! Total high-res generated: {total_generated}")
            
            # Longer pause between high-res rounds
            if round_num < rounds:
                print("   ⏳ Longer pause for high-res processing...")
                time.sleep(8)
        else:
            print(f"❌ Round {round_num} failed!")
            break
    
    # Show results
    hires_files = glob.glob(f"{OUTPUT_DIR}/ukrainian_flower_hires_*.png")
    hires_files.sort(key=os.path.getmtime, reverse=True)
    
    print(f"\n🎉 HIGH-RES GENERATION COMPLETE!")
    print("=" * 50)
    print(f"📊 Total high-res images generated: {total_generated}")
    print(f"📁 Latest {min(5, len(hires_files))} files:")
    
    for i, img in enumerate(hires_files[:5], 1):
        file_size = os.path.getsize(img) / (1024*1024)  # MB
        print(f"   {i}. {os.path.basename(img)} ({file_size:.1f}MB)")
    
    return total_generated > 0

def main():
    print("🎯 Ukrainian Flower Hat Girl - High-Resolution Generation")
    
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
    
    # Generate high-resolution images
    if not generate_hires_batch(rounds=5, batch_size=4, resolution=2048):
        print("❌ High-res generation failed!")
        return 1
    
    print("\n🎉 HIGH-RESOLUTION PIPELINE COMPLETE!")
    print("=" * 70)
    print("🚀 Generated high-resolution Ukrainian flower hat girl images")
    print("📐 Resolution: 2048x2048 (4x larger than original)")
    print("✨ Enhanced with multiple quality LoRAs")
    print("👀 View: feh ComfyUI/output/ukrainian_flower_hires_*.png")
    
    return 0

if __name__ == "__main__":
    exit(main())