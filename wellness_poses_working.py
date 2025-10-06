#!/usr/bin/env python3
"""
Wellness Poses Generator - Based on Working Ukrainian Portrait Template
"""

import requests
import json
import time
import random
import sys

# ComfyUI configuration
COMFYUI_URL = "http://localhost:8188"

def generate_wellness_pose(theme="yoga warrior pose", seed=None):
    """Generate wellness pose using proven Ukrainian portrait workflow structure"""
    
    if seed is None:
        seed = random.randint(100000, 999999)
    
    # Wellness-optimized prompt using Ukrainian portrait structure
    prompt = f"""A hyper-realistic portrait of a confident, athletic woman in her late 20s with radiant healthy skin, expressive eyes, perfect anatomy. She is demonstrating {theme}, wearing professional athletic wear, fitness clothing, yoga attire. The setting is modern wellness studio with natural lighting, clean minimalist background. Her expression conveys strength, focus, determination, inner peace. Technical specifications: Shot with 85mm f/1.4 for beautiful depth of field, professional fitness photography lighting with softbox, composed to show full athletic form and graceful pose. The image should have professional studio quality, sharp focus on the subject, beautiful skin texture details, perfect anatomy, and inspiring wellness lighting. Style: photorealistic, high-end fitness photography, editorial quality, award-winning wellness portrait photography, motivational fitness imagery."""
    
    # Use exact working workflow structure from Ukrainian portraits
    workflow = {
        "3": {
            "inputs": {
                "seed": seed,
                "steps": 21,
                "cfg": 3.8,
                "sampler_name": "euler",
                "scheduler": "simple",
                "denoise": 1,
                "model": ["4", 0],  # Direct from checkpoint, no LoRA
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0]
            },
            "class_type": "KSampler"
        },
        "4": {
            "inputs": {
                "ckpt_name": "flux1-dev.safetensors"
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
                "clip": ["4", 1]
            },
            "class_type": "CLIPTextEncode"
        },
        "7": {
            "inputs": {
                "text": "blurry, low quality, distorted, bad anatomy, extra limbs, missing limbs, poorly drawn hands, poorly drawn face, mutation, deformed, ugly, bad proportions, amateur photography, incorrect pose",
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
                "filename_prefix": f"wellness_{theme.replace(' ', '_')}_{seed}",
                "images": ["8", 0]
            },
            "class_type": "SaveImage"
        }
    }
    
    print(f"🧘 Generating: {theme}")
    print(f"🎲 Seed: {seed}")
    
    try:
        # Submit workflow
        payload = {
            "prompt": workflow,
            "client_id": "wellness_working"
        }
        
        response = requests.post(f"{COMFYUI_URL}/prompt", json=payload)
        response.raise_for_status()
        result = response.json()
        prompt_id = result['prompt_id']
        
        print(f"✅ Queued with ID: {prompt_id}")
        
        # Wait for completion with timeout
        start_time = time.time()
        while time.time() - start_time < 120:  # 2 minute timeout
            try:
                history_response = requests.get(f"{COMFYUI_URL}/history/{prompt_id}")
                history_response.raise_for_status()
                history_data = history_response.json()
                
                if prompt_id in history_data:
                    status = history_data[prompt_id].get('status', {})
                    
                    if status.get('status_str') == 'success':
                        outputs = history_data[prompt_id].get('outputs', {})
                        if outputs:
                            for node_id, output in outputs.items():
                                if 'images' in output:
                                    for img in output['images']:
                                        print(f"📸 Generated: {img['filename']}")
                            return True
                    elif status.get('status_str') == 'error':
                        messages = status.get('messages', [])
                        for msg in messages:
                            if msg[0] == 'execution_error':
                                print(f"❌ Error: {msg[1].get('exception_message', 'Unknown error')}")
                        return False
                        
            except Exception as e:
                print(f"⚠️ Checking status: {e}")
                
            time.sleep(3)
        
        print(f"⏰ Timeout after 2 minutes")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Generate multiple wellness poses"""
    print("🧘 Wellness Poses Generator (Working Version)")
    print("=" * 50)
    
    # Check ComfyUI status
    try:
        response = requests.get(f"{COMFYUI_URL}/system_stats", timeout=5)
        if response.status_code != 200:
            print("❌ ComfyUI not responding")
            return
    except:
        print("❌ ComfyUI not running")
        return
    
    print("✅ ComfyUI is running")
    
    # Wellness pose themes
    themes = [
        "yoga warrior III pose, strength and balance",
        "meditation lotus position, inner peace and mindfulness", 
        "fitness kettlebell training, power and athletic form",
        "yoga tree pose, perfect balance and focus",
        "martial arts training, discipline and strong stance",
        "morning stretching routine, flexibility and wellness",
        "sunset yoga practice, serenity and mind-body connection",
        "fitness strength training, muscle definition and empowerment"
    ]
    
    num_poses = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    successful = 0
    
    print(f"📊 Generating {num_poses} wellness poses...\n")
    
    for i in range(num_poses):
        theme = random.choice(themes)
        print(f"🎯 Pose {i+1}/{num_poses}")
        
        if generate_wellness_pose(theme):
            successful += 1
            print("✅ SUCCESS\n")
        else:
            print("❌ FAILED\n")
        
        # Brief pause between generations
        if i < num_poses - 1:
            time.sleep(5)
    
    print(f"🏁 Complete! {successful}/{num_poses} successful")
    
    if successful > 0:
        print(f"📸 Check ComfyUI/output/ for generated wellness poses")
        print(f"🎯 Run: ./view_wellness_poses.sh")

if __name__ == "__main__":
    main()