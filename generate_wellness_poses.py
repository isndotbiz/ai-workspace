#!/usr/bin/env python3
"""
Health and Wellness Pose Generator
Generate professional wellness and fitness poses with optimized prompts
"""

import requests
import json
import time
import random
import sys
import os

# ComfyUI configuration
COMFYUI_URL = "http://localhost:8188"

# Health and wellness pose themes
WELLNESS_THEMES = [
    "yoga warrior III pose, strength and balance, powerful stance",
    "meditation lotus position, inner peace, mindfulness practice", 
    "fitness kettlebell training, power and agility, athletic form",
    "outdoor hiking adventure, determination, nature connection",
    "yoga tree pose, perfect balance, grounding energy",
    "martial arts training, discipline and focus, strong stance",
    "morning stretching routine, flexibility, healthy lifestyle",
    "wellness smoothie preparation, healthy nutrition, vibrant living",
    "sunset yoga practice, serenity, mind-body connection",
    "fitness strength training, muscle definition, empowerment"
]

# Base optimized wellness prompt
BASE_WELLNESS_PROMPT = """A confident, empowered woman in her late 20s, athletic build, radiant healthy skin, 
professional wellness photography, {theme}, perfect form and technique, inspirational pose, 
natural lighting, studio quality, high resolution, detailed anatomy, graceful movement, 
strength and femininity, wellness lifestyle, motivational fitness, clean composition, 
professional athletic wear, focused expression, determined gaze, healthy glow"""

def create_wellness_workflow(prompt, batch_size=1, steps=21, cfg=3.8, seed=-1):
    """Create ComfyUI workflow for wellness pose generation using proven GGUF structure"""
    
    if seed == -1:
        seed = random.randint(100000, 999999)
    
    workflow = {
        "3": {
            "inputs": {
                "seed": seed,
                "steps": steps,
                "cfg": cfg,
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
                "ckpt_name": "flux1-dev-Q3_K_S.gguf"
            },
            "class_type": "CheckpointLoaderSimple"
        },
        "5": {
            "inputs": {
                "width": 1024,
                "height": 1024,
                "batch_size": batch_size
            },
            "class_type": "EmptyLatentImage"
        },
        "6": {
            "inputs": {
                "text": prompt,
                "clip": ["4", 1]
            },
            "class_type": "CLIPTextEncode"
        },
        "7": {
            "inputs": {
                "text": "blurry, low quality, distorted, bad anatomy, deformed, ugly, poor form, incorrect pose, amateur photography, mutation, extra limbs, missing limbs, poorly drawn hands, poorly drawn face, bad proportions",
                "clip": ["4", 1]
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
    
    return workflow

def queue_prompt(workflow):
    """Queue workflow in ComfyUI"""
    try:
        prompt_data = {
            "prompt": workflow,
            "client_id": "wellness_generator"
        }
        
        response = requests.post(f"{COMFYUI_URL}/prompt", json=prompt_data)
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"Error queuing prompt: {e}")
        return None

def wait_for_completion(prompt_id):
    """Wait for workflow completion"""
    while True:
        try:
            response = requests.get(f"{COMFYUI_URL}/history/{prompt_id}")
            response.raise_for_status()
            history = response.json()
            
            if prompt_id in history:
                return True
                
        except requests.exceptions.RequestException:
            pass
            
        time.sleep(2)

def check_comfyui_status():
    """Check if ComfyUI is running"""
    try:
        response = requests.get(f"{COMFYUI_URL}/system_stats", timeout=5)
        return response.status_code == 200
    except:
        return False

def generate_wellness_poses(num_batches=5, batch_size=1, steps=21, cfg=3.8):
    """Generate health and wellness poses"""
    
    print("🧘 Health & Wellness Pose Generator Starting...")
    
    # Check ComfyUI status
    if not check_comfyui_status():
        print("❌ ComfyUI not running. Please start it first.")
        return False
    
    print(f"✅ ComfyUI is running")
    print(f"📊 Generating {num_batches} batches of {batch_size} images each")
    print(f"⚙️  Settings: Steps={steps}, CFG={cfg}")
    print()
    
    total_generated = 0
    
    for batch_num in range(num_batches):
        # Select random wellness theme
        theme = random.choice(WELLNESS_THEMES)
        prompt = BASE_WELLNESS_PROMPT.format(theme=theme)
        
        print(f"🎯 Batch {batch_num + 1}/{num_batches}")
        print(f"🎨 Theme: {theme}")
        print(f"📝 Prompt: {prompt[:100]}...")
        
        # Create and queue workflow
        workflow = create_wellness_workflow(
            prompt=prompt,
            batch_size=batch_size, 
            steps=steps,
            cfg=cfg,
            seed=-1
        )
        
        result = queue_prompt(workflow)
        if not result:
            print("❌ Failed to queue prompt")
            continue
            
        prompt_id = result.get('prompt_id')
        if not prompt_id:
            print("❌ No prompt ID returned")
            continue
            
        print(f"⏳ Queued with ID: {prompt_id}")
        
        # Wait for completion
        if wait_for_completion(prompt_id):
            total_generated += batch_size
            print(f"✅ Batch {batch_num + 1} completed! Generated {batch_size} images")
        else:
            print(f"❌ Batch {batch_num + 1} failed")
        
        print()
        
        # Brief pause between batches
        if batch_num < num_batches - 1:
            time.sleep(3)
    
    print(f"🎉 Wellness pose generation complete!")
    print(f"📸 Total images generated: {total_generated}")
    print(f"📁 Images saved to: ComfyUI/output/")
    
    return True

if __name__ == "__main__":
    # Parse command line arguments
    num_batches = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    batch_size = int(sys.argv[2]) if len(sys.argv) > 2 else 1  
    steps = int(sys.argv[3]) if len(sys.argv) > 3 else 21
    cfg = float(sys.argv[4]) if len(sys.argv) > 4 else 3.8
    
    print("🧘 Health & Wellness Pose Generator")
    print("=" * 50)
    
    success = generate_wellness_poses(
        num_batches=num_batches,
        batch_size=batch_size, 
        steps=steps,
        cfg=cfg
    )
    
    if success:
        print("\n🎯 Quick view command:")
        print("./view_wellness_poses.sh")
    else:
        print("\n❌ Generation failed. Check ComfyUI status.")