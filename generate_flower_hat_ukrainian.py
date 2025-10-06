#!/usr/bin/env python3

import json
import requests
import time
import random

# Ukrainian Flower Hat Portrait Generator - Based on Working System
print("\n🌻 UKRAINIAN FLOWER HAT PORTRAIT GENERATOR 🌻")
print("=" * 60)

COMFY_URL = "http://localhost:8188"
WORKFLOW_FILE = "workflows/flux_kontext_fp8_turbo.json"

def load_workflow():
    """Load the working flux kontext turbo workflow"""
    try:
        with open(WORKFLOW_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Workflow file not found: {WORKFLOW_FILE}")
        return None

def create_flower_hat_workflow():
    """Create flower hat workflow using working template"""
    
    # Beautiful Ukrainian flower hat prompt
    flower_prompt = """A stunning beautiful Ukrainian woman in her late 20s wearing a traditional flower hat crown made of vibrant wildflowers including sunflowers, poppies, daisies, and cornflowers. She is dressed in light, airy summer clothing - a flowing white linen blouse and light blue skirt perfect for warm weather. The setting is a beautiful Ukrainian countryside with golden wheat fields in the background. Her hair flows gently in the summer breeze, framing her radiant face with natural makeup that highlights her warm brown eyes and gentle smile. The lighting is soft and golden, creating a dreamy, romantic atmosphere. Perfect anatomy, ideal proportions, photorealistic, high quality, detailed, masterpiece, traditional Ukrainian beauty, summer warmth, elegant pastoral setting."""
    
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
        "4": {
            "inputs": {
                "lora_name": "FLUX.1-Turbo-Alpha.safetensors",
                "strength_model": 0.8,
                "strength_clip": 0.8,
                "model": ["1", 0],
                "clip": ["2", 0]
            },
            "class_type": "LoraLoader",
            "_meta": {"title": "Turbo LoRA - Speed Boost"}
        },
        "5": {
            "inputs": {
                "text": flower_prompt,
                "clip": ["4", 1]
            },
            "class_type": "CLIPTextEncode",
            "_meta": {"title": "Flower Hat Prompt"}
        },
        "6": {
            "inputs": {
                "text": "deformed, cartoonish, extra fingers, blurry, lowres, bad skin, oversaturated, flat lighting, amateur photography, low quality, distorted anatomy, bad proportions, ugly, masculine features",
                "clip": ["4", 1]
            },
            "class_type": "CLIPTextEncode",
            "_meta": {"title": "Negative Prompt"}
        },
        "7": {
            "inputs": {
                "conditioning": ["5", 0],
                "guidance": 3.5
            },
            "class_type": "FluxGuidance",
            "_meta": {"title": "CFG - Flux Guidance Scale"}
        },
        "8": {
            "inputs": {
                "width": 1024,
                "height": 1024,
                "batch_size": 2
            },
            "class_type": "EmptyLatentImage",
            "_meta": {"title": "Batch - Number of Images"}
        },
        "9": {
            "inputs": {
                "seed": random.randint(1, 1000000),
                "steps": 8,
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
            "_meta": {"title": "Steps - Turbo Diffusion Steps"}
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
                "filename_prefix": "ukrainian_flower_hat",
                "images": ["10", 0]
            },
            "class_type": "SaveImage",
            "_meta": {"title": "Save Image"}
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
            print(f"❌ ComfyUI error: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Submission failed: {e}")
        return None

def wait_for_completion(prompt_id):
    """Wait for generation completion"""
    start_time = time.time()
    
    while time.time() - start_time < 120:  # 2 minute timeout
        try:
            response = requests.get(f"{COMFY_URL}/history/{prompt_id}", timeout=5)
            if response.status_code == 200:
                history = response.json()
                if prompt_id in history and history[prompt_id].get('outputs'):
                    return True
            
            elapsed = time.time() - start_time
            if elapsed > 20 and int(elapsed) % 15 == 0:
                print(f"   ⚡ Generation progress: {elapsed:.0f}s elapsed...")
                
            time.sleep(2)
            
        except Exception:
            time.sleep(2)
    
    return False

def main():
    print("🎯 Generating Ukrainian woman with flower hat...")
    print("⚙️  Configuration:")
    print("   • Traditional Ukrainian flower crown")  
    print("   • Light summer clothing for warm weather")
    print("   • Beautiful countryside setting")
    print("   • Working LoRA: FLUX.1-Turbo-Alpha")
    print("   • Steps: 8 (optimized)")
    print("   • Batch size: 2 images")
    
    # Create workflow
    workflow = create_flower_hat_workflow()
    
    print(f"\n🚀 Submitting to ComfyUI...")
    prompt_id = submit_generation(workflow)
    
    if not prompt_id:
        print("❌ Failed to submit generation")
        return 1
    
    print(f"✅ Generation queued: {prompt_id}")
    print("⏳ Generating flower hat portrait...")
    
    if wait_for_completion(prompt_id):
        print("\n🎉 UKRAINIAN FLOWER HAT PORTRAIT COMPLETE!")
        print("=" * 60)
        print("📸 Beautiful Ukrainian woman with flower hat generated!")
        print("📁 Check: ComfyUI/output/ukrainian_flower_hat_*.png")
        print("🌻 Perfect for warm summer weather!")
        return 0
    else:
        print("❌ Generation timed out")
        return 1

if __name__ == "__main__":
    exit(main())