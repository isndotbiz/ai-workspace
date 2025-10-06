#!/usr/bin/env python3

import json
import requests
import time
import sys
import os

# Enhanced Executive Portrait Generator with LoRA Stacking
print("\n🎨 ENHANCED EXECUTIVE PORTRAIT GENERATOR")
print("=" * 50)

# ComfyUI settings
COMFY_URL = "http://localhost:8188"
OUTPUT_DIR = "ComfyUI/output"

# Enhanced workflow template with multiple LoRAs
def create_enhanced_workflow(prompt, seed=None):
    if seed is None:
        seed = int(time.time()) % 1000000
    
    # Sophisticated business attire prompt
    enhanced_prompt = f"""
{prompt}, sophisticated late 20s businesswoman CEO, elegant fashionable business attire, 
tailored professional clothing, confident executive pose, luxury office setting, 
impeccable style, refined beauty, sharp features, intelligent eyes, 
professional success, elegant accessories, high-end fashion, 
photorealistic, ultra detailed, masterpiece, perfect anatomy, flawless skin, 
studio lighting, professional photography, executive presence, sophisticated style
"""

    workflow = {
        "1": {
            "inputs": {
                "unet_name": "flux1-dev-kontext_fp8_scaled.safetensors",
                "weight_dtype": "fp8_e4m3fn"
            },
            "class_type": "UNETLoader"
        },
        "2": {
            "inputs": {
                "clip_name1": "clip_l.safetensors",
                "clip_name2": "t5xxl_fp8_e4m3fn.safetensors",
                "type": "flux"
            },
            "class_type": "DualCLIPLoader"
        },
        "3": {
            "inputs": {
                "vae_name": "ae.safetensors"
            },
            "class_type": "VAELoader"
        },
        # First LoRA - Turbo for speed
        "4": {
            "inputs": {
                "lora_name": "FLUX.1-Turbo-Alpha.safetensors",
                "strength_model": 0.6,
                "strength_clip": 0.6,
                "model": ["1", 0],
                "clip": ["2", 0]
            },
            "class_type": "LoraLoader"
        },
        # Second LoRA - Realism enhancement
        "5": {
            "inputs": {
                "lora_name": "flux-RealismLora.safetensors",
                "strength_model": 0.8,
                "strength_clip": 0.8,
                "model": ["4", 0],
                "clip": ["4", 1]
            },
            "class_type": "LoraLoader"
        },
        # Third LoRA - Detail enhancement
        "6": {
            "inputs": {
                "lora_name": "flux-add-details.safetensors",
                "strength_model": 0.7,
                "strength_clip": 0.7,
                "model": ["5", 0],
                "clip": ["5", 1]
            },
            "class_type": "LoraLoader"
        },
        # Positive prompt
        "7": {
            "inputs": {
                "text": enhanced_prompt,
                "clip": ["6", 1]
            },
            "class_type": "CLIPTextEncode"
        },
        # Negative prompt
        "8": {
            "inputs": {
                "text": "blurry, low quality, distorted, deformed, amateur, bad anatomy, bad proportions, low resolution, pixelated, overexposed, underexposed, noisy",
                "clip": ["6", 1]
            },
            "class_type": "CLIPTextEncode"
        },
        # Flux guidance
        "9": {
            "inputs": {
                "conditioning": ["7", 0],
                "guidance": 4.5
            },
            "class_type": "FluxGuidance"
        },
        # High resolution latent
        "10": {
            "inputs": {
                "width": 1216,
                "height": 1216,
                "batch_size": 1
            },
            "class_type": "EmptyLatentImage"
        },
        # Enhanced sampling with more steps
        "11": {
            "inputs": {
                "seed": seed,
                "steps": 16,  # Increased steps for quality
                "cfg": 1.0,
                "sampler_name": "euler",
                "scheduler": "simple",
                "denoise": 1.0,
                "model": ["6", 0],
                "positive": ["9", 0],
                "negative": ["8", 0],
                "latent_image": ["10", 0]
            },
            "class_type": "KSampler"
        },
        # VAE decode
        "12": {
            "inputs": {
                "samples": ["11", 0],
                "vae": ["3", 0]
            },
            "class_type": "VAEDecode"
        },
        # Save high-quality image
        "13": {
            "inputs": {
                "filename_prefix": "enhanced_executive_ultra",
                "images": ["12", 0]
            },
            "class_type": "SaveImage"
        }
    }
    
    return workflow

def submit_generation(workflow):
    """Submit generation to ComfyUI"""
    try:
        response = requests.post(f"{COMFY_URL}/prompt", json={"prompt": workflow}, timeout=10)
        if response.status_code == 200:
            result = response.json()
            return result.get('prompt_id')
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Submission failed: {e}")
        return None

def wait_for_completion(prompt_id, timeout=300):
    """Wait for generation completion"""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{COMFY_URL}/history/{prompt_id}", timeout=5)
            if response.status_code == 200:
                history = response.json()
                if prompt_id in history and history[prompt_id].get('outputs'):
                    return True
            
            # Progress update
            elapsed = time.time() - start_time
            if int(elapsed) % 20 == 0 and elapsed > 10:
                print(f"   ⚡ Generation progress: {elapsed:.0f}s elapsed...")
            
            time.sleep(2)
            
        except Exception:
            time.sleep(2)
    
    return False

def main():
    # Sophisticated business prompt
    prompt = """
    Sophisticated late 20s female CEO in an elegant executive pose, 
    wearing fashionable tailored business attire with refined style, 
    confident professional demeanor, luxury corporate environment, 
    impeccable fashion sense showing success and authority
    """
    
    print("🎯 Generating enhanced executive portrait...")
    print("⚙️  Configuration:")
    print("   • Resolution: 1216x1216 (high quality)")
    print("   • Steps: 16 (enhanced quality)")
    print("   • LoRAs: Turbo + Realism + Detail enhancement")
    print("   • CFG Guidance: 4.5 (optimal)")
    
    # Create workflow
    workflow = create_enhanced_workflow(prompt)
    
    # Submit generation
    print("\n🚀 Submitting to ComfyUI...")
    prompt_id = submit_generation(workflow)
    
    if not prompt_id:
        print("❌ Failed to submit generation")
        return 1
    
    print(f"✅ Generation queued: {prompt_id}")
    print("⏳ Generating enhanced portrait (this may take 2-3 minutes)...")
    
    # Wait for completion
    if wait_for_completion(prompt_id):
        print("\n🎉 ENHANCED EXECUTIVE PORTRAIT COMPLETE!")
        print("=" * 50)
        print("📸 High-quality enhanced image generated!")
        print(f"📁 Check: {OUTPUT_DIR}/enhanced_executive_ultra_*.png")
        print("🎯 Features:")
        print("   • Multiple LoRA enhancements")
        print("   • 1216x1216 high resolution") 
        print("   • 16 diffusion steps for quality")
        print("   • Sophisticated business styling")
        return 0
    else:
        print("❌ Generation timed out")
        return 1

if __name__ == "__main__":
    exit(main())