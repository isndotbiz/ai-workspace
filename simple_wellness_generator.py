#!/usr/bin/env python3
"""
Simple Wellness Pose Generator
Using working flux kontext workflow structure
"""

import requests
import json
import time
import random

# ComfyUI configuration
COMFYUI_URL = "http://localhost:8188"

def generate_wellness_pose():
    """Generate a single wellness pose using the working flux workflow"""
    
    # Get random wellness theme
    themes = [
        "yoga warrior III pose, strength and balance",
        "meditation lotus position, inner peace",
        "fitness kettlebell training, power and agility",
        "outdoor hiking, determination and nature connection",
        "yoga tree pose, perfect balance",
        "martial arts training, discipline and focus",
        "morning stretching routine, flexibility",
        "wellness smoothie preparation, healthy nutrition",
        "sunset yoga practice, serenity",
        "fitness strength training, empowerment"
    ]
    
    theme = random.choice(themes)
    
    # Optimized wellness prompt 
    prompt = f"""A confident, empowered woman in her late 20s, athletic build, radiant healthy skin, 
professional wellness photography, {theme}, perfect form and technique, inspirational pose, 
natural lighting, studio quality, high resolution, detailed anatomy, graceful movement, 
strength and femininity, wellness lifestyle, motivational fitness, clean composition, 
professional athletic wear, focused expression, determined gaze, healthy glow, hyperrealistic, 
ultra-detailed skin texture, cinematic color grading, 8k, masterpiece"""
    
    # Simple working workflow based on your flux kontext setup  
    workflow = {
        "3": {
            "inputs": {
                "seed": random.randint(100000, 999999),
                "steps": 21,
                "cfg": 3.8,
                "sampler_name": "euler",
                "scheduler": "simple",
                "denoise": 1,
                "model": ["11", 0],
                "positive": ["6", 0], 
                "negative": ["7", 0],
                "latent_image": ["5", 0]
            },
            "class_type": "KSampler"
        },
        "4": {
            "inputs": {
                "ckpt_name": "flux1-dev-kontext_fp8_scaled.safetensors"
            },
            "class_type": "CheckpointLoaderSimple"
        },
        "5": {
            "inputs": {
                "width": 1024,
                "height": 1024,
                "batch_size": 1
            },
            "class_type": "EmptyLatentImage"
        },
        "6": {
            "inputs": {
                "text": prompt,
                "clip": ["11", 1]
            },
            "class_type": "CLIPTextEncode" 
        },
        "7": {
            "inputs": {
                "text": "blurry, low quality, distorted, bad anatomy, deformed, ugly, poor form, incorrect pose, amateur photography",
                "clip": ["11", 1]
            },
            "class_type": "CLIPTextEncode"
        },
        "8": {
            "inputs": {
                "samples": ["3", 0],
                "vae": ["4", 2]
            },
            "class_type": "VAEDecode"
        },
        "9": {
            "inputs": {
                "filename_prefix": "wellness_pose",
                "images": ["8", 0]
            },
            "class_type": "SaveImage"
        },
        "10": {
            "inputs": {
                "lora_name": "flux-RealismLora.safetensors",
                "strength_model": 0.8,
                "strength_clip": 0.8,
                "model": ["4", 0],
                "clip": ["4", 1]
            },
            "class_type": "LoraLoader"
        },
        "11": {
            "inputs": {
                "lora_name": "Hyper-FLUX.1-dev-8steps-lora.safetensors", 
                "strength_model": 0.6,
                "strength_clip": 0.6,
                "model": ["10", 0],
                "clip": ["10", 1]
            },
            "class_type": "LoraLoader"
        }
    }
    
    print(f"🧘 Generating wellness pose: {theme}")
    print(f"📝 Prompt: {prompt[:80]}...")
    
    # Submit to ComfyUI
    try:
        payload = {
            "prompt": workflow,
            "client_id": "wellness_gen"
        }
        
        response = requests.post(f"{COMFYUI_URL}/prompt", json=payload)
        response.raise_for_status()
        result = response.json()
        prompt_id = result['prompt_id']
        
        print(f"✅ Queued with ID: {prompt_id}")
        
        # Wait for completion
        while True:
            try:
                history_response = requests.get(f"{COMFYUI_URL}/history/{prompt_id}")
                history_response.raise_for_status()
                history = history_response.json()
                
                if prompt_id in history:
                    print("✅ Wellness pose generation complete!")
                    print(f"📸 Check ComfyUI/output/ for wellness_pose_*.png")
                    return True
                    
            except:
                pass
                
            time.sleep(3)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧘 Simple Wellness Pose Generator")
    print("=" * 40)
    
    # Check ComfyUI status
    try:
        response = requests.get(f"{COMFYUI_URL}/system_stats", timeout=5)
        if response.status_code == 200:
            print("✅ ComfyUI is running")
            generate_wellness_pose()
        else:
            print("❌ ComfyUI not responding")
    except:
        print("❌ ComfyUI not running")