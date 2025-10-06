#!/usr/bin/env python3

import json
import requests
import time
import os
import glob
from PIL import Image

# 🚀 UKRAINIAN FLOWER HAT GIRL - STAGE 2: UPSCALING 🚀
print("\n🚀 UKRAINIAN FLOWER HAT GIRL - STAGE 2: UPSCALING 🚀")
print("=" * 70)

COMFY_URL = "http://localhost:8188"
OUTPUT_DIR = "ComfyUI/output"

def create_upscale_workflow(image_filename, upscaler_model="4x-UltraSharp.pth"):
    """Create 4x upscaling workflow for a specific image"""
    
    workflow = {
        "1": {
            "inputs": {
                "image": image_filename,
                "upload": "image"
            },
            "class_type": "LoadImage",
            "_meta": {"title": "Load Base Image"}
        },
        "2": {
            "inputs": {
                "model_name": upscaler_model
            },
            "class_type": "UpscaleModelLoader",
            "_meta": {"title": "Load 4x UltraSharp Upscaler"}
        },
        "3": {
            "inputs": {
                "upscale_model": ["2", 0],
                "image": ["1", 0]
            },
            "class_type": "ImageUpscaleWithModel",
            "_meta": {"title": "4x Upscale (1024->4096)"}
        },
        "4": {
            "inputs": {
                "filename_prefix": "ukrainian_flower_4x",
                "images": ["3", 0]
            },
            "class_type": "SaveImage",
            "_meta": {"title": "Save 4x Upscaled"}
        }
    }
    
    return workflow

def submit_and_wait(workflow, timeout=120):
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
                    print(f"   🚀 Upscaling: {elapsed:.0f}s elapsed...")
                    
                time.sleep(2)
                
            except Exception:
                time.sleep(2)
        
        return False
        
    except Exception as e:
        print(f"❌ Submission failed: {e}")
        return False

def get_base_images(prefix="ukrainian_flower_base"):
    """Get all base images to upscale"""
    pattern = f"{OUTPUT_DIR}/{prefix}_*.png"
    files = glob.glob(pattern)
    files.sort(key=os.path.getmtime, reverse=True)
    return files

def upscale_all_images():
    """Upscale all base images"""
    base_images = get_base_images()
    
    if not base_images:
        print("❌ No base images found! Run Stage 1 first.")
        return False
    
    print(f"🎯 Found {len(base_images)} base images to upscale")
    print("⚙️  Upscaling Configuration:")
    print("   • Model: 4x-UltraSharp.pth")
    print("   • Input: 1024x1024 → Output: 4096x4096")
    print("   • Quality: Ultra high-resolution")
    
    successful_upscales = 0
    
    for i, image_path in enumerate(base_images, 1):
        image_name = os.path.basename(image_path)
        print(f"\n🚀 Upscaling {i}/{len(base_images)}: {image_name}")
        
        workflow = create_upscale_workflow(image_name)
        
        if submit_and_wait(workflow):
            successful_upscales += 1
            print(f"✅ Upscaled: {image_name} → 4x resolution")
        else:
            print(f"❌ Failed: {image_name}")
        
        # Brief pause between upscales
        if i < len(base_images):
            print("   ⏳ Brief pause...")
            time.sleep(2)
    
    print(f"\n🎉 UPSCALING COMPLETE!")
    print(f"📊 Successfully upscaled: {successful_upscales}/{len(base_images)} images")
    
    # Show latest upscaled files
    upscaled_files = glob.glob(f"{OUTPUT_DIR}/ukrainian_flower_4x_*.png")
    upscaled_files.sort(key=os.path.getmtime, reverse=True)
    
    print(f"📁 Latest upscaled files:")
    for img in upscaled_files[:5]:
        file_size = os.path.getsize(img) / (1024*1024)  # MB
        print(f"   • {os.path.basename(img)} ({file_size:.1f}MB)")
    
    return successful_upscales > 0

def main():
    print("🎯 Ukrainian Flower Hat Girl - Stage 2: 4x Upscaling")
    
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
    
    # Run upscaling
    if not upscale_all_images():
        print("❌ Upscaling failed!")
        return 1
    
    print("\n🎉 STAGE 2 COMPLETE!")
    print("=" * 70)
    print("🚀 All base images upscaled to 4x resolution (4096x4096)")
    print("🔄 Next step: Run Stage 3 for face enhancement")
    print("👀 View 4x images: feh ComfyUI/output/ukrainian_flower_4x_*.png")
    
    return 0

if __name__ == "__main__":
    exit(main())