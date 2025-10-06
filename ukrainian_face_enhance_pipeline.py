#!/usr/bin/env python3

import json
import requests
import time
import os
import glob
from PIL import Image

# ✨ UKRAINIAN FLOWER HAT GIRL - STAGE 3: FACE ENHANCEMENT ✨
print("\n✨ UKRAINIAN FLOWER HAT GIRL - STAGE 3: FACE ENHANCEMENT ✨")
print("=" * 70)

COMFY_URL = "http://localhost:8188"
OUTPUT_DIR = "ComfyUI/output"

def create_face_enhance_workflow(image_filename, face_model="codeformer.pth"):
    """Create face enhancement workflow using CodeFormer"""
    
    workflow = {
        "1": {
            "inputs": {
                "image": image_filename,
                "upload": "image"
            },
            "class_type": "LoadImage",
            "_meta": {"title": "Load 4x Image"}
        },
        "2": {
            "inputs": {
                "model_name": face_model
            },
            "class_type": "FaceRestoreModelLoader",
            "_meta": {"title": "Load CodeFormer"}
        },
        "3": {
            "inputs": {
                "facerestore_model": ["2", 0],
                "image": ["1", 0]
            },
            "class_type": "FaceRestore",
            "_meta": {"title": "Enhance Facial Features"}
        },
        "4": {
            "inputs": {
                "filename_prefix": "ukrainian_flower_enhanced",
                "images": ["3", 0]
            },
            "class_type": "SaveImage",
            "_meta": {"title": "Save Enhanced"}
        }
    }
    
    return workflow

def create_combined_enhance_workflow(image_filename):
    """Create combined upscaling + face enhancement workflow"""
    
    workflow = {
        # Load original base image
        "1": {
            "inputs": {
                "image": image_filename,
                "upload": "image"
            },
            "class_type": "LoadImage",
            "_meta": {"title": "Load Base Image"}
        },
        
        # First: 4x Upscaling
        "2": {
            "inputs": {
                "model_name": "4x-UltraSharp.pth"
            },
            "class_type": "UpscaleModelLoader",
            "_meta": {"title": "Load 4x Upscaler"}
        },
        "3": {
            "inputs": {
                "upscale_model": ["2", 0],
                "image": ["1", 0]
            },
            "class_type": "ImageUpscaleWithModel",
            "_meta": {"title": "4x Upscale (1024->4096)"}
        },
        
        # Then: Face Enhancement
        "4": {
            "inputs": {
                "model_name": "codeformer.pth"
            },
            "class_type": "FaceRestoreModelLoader",
            "_meta": {"title": "Load CodeFormer"}
        },
        "5": {
            "inputs": {
                "facerestore_model": ["4", 0],
                "image": ["3", 0]
            },
            "class_type": "FaceRestore",
            "_meta": {"title": "Enhance Facial Features"}
        },
        
        # Save final result
        "6": {
            "inputs": {
                "filename_prefix": "ukrainian_flower_final",
                "images": ["5", 0]
            },
            "class_type": "SaveImage",
            "_meta": {"title": "Save Final Enhanced"}
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
                if elapsed > 15 and int(elapsed) % 10 == 0:
                    print(f"   ✨ Enhancing: {elapsed:.0f}s elapsed...")
                    
                time.sleep(2)
                
            except Exception:
                time.sleep(2)
        
        return False
        
    except Exception as e:
        print(f"❌ Submission failed: {e}")
        return False

def get_images_to_enhance(use_upscaled=True):
    """Get images to enhance - either upscaled or base images"""
    if use_upscaled:
        pattern = f"{OUTPUT_DIR}/ukrainian_flower_4x_*.png"
        prefix = "4x upscaled"
    else:
        pattern = f"{OUTPUT_DIR}/ukrainian_flower_base_*.png"
        prefix = "base"
    
    files = glob.glob(pattern)
    files.sort(key=os.path.getmtime, reverse=True)
    
    print(f"🎯 Using {prefix} images: {len(files)} found")
    return files

def enhance_faces_only():
    """Enhance faces on already upscaled images"""
    upscaled_images = get_images_to_enhance(use_upscaled=True)
    
    if not upscaled_images:
        print("❌ No upscaled images found! Run Stage 2 first.")
        return False
    
    print(f"🎯 Found {len(upscaled_images)} upscaled images to enhance")
    print("⚙️  Face Enhancement Configuration:")
    print("   • Model: CodeFormer (advanced face restoration)")
    print("   • Input: 4096x4096 upscaled images")
    print("   • Enhancement: Facial features, skin, eyes, smile")
    
    successful_enhancements = 0
    
    for i, image_path in enumerate(upscaled_images, 1):
        image_name = os.path.basename(image_path)
        print(f"\n✨ Enhancing {i}/{len(upscaled_images)}: {image_name}")
        
        workflow = create_face_enhance_workflow(image_name)
        
        if submit_and_wait(workflow):
            successful_enhancements += 1
            print(f"✅ Enhanced: {image_name} → facial features improved")
        else:
            print(f"❌ Failed: {image_name}")
        
        # Brief pause between enhancements
        if i < len(upscaled_images):
            print("   ⏳ Brief pause...")
            time.sleep(2)
    
    return successful_enhancements

def combined_upscale_and_enhance():
    """Combined upscaling + face enhancement in one workflow"""
    base_images = get_images_to_enhance(use_upscaled=False)
    
    if not base_images:
        print("❌ No base images found! Run Stage 1 first.")
        return False
    
    print(f"🎯 Found {len(base_images)} base images for combined processing")
    print("⚙️  Combined Pipeline Configuration:")
    print("   • Step 1: 4x Upscaling (1024→4096)")
    print("   • Step 2: Face Enhancement (CodeFormer)")
    print("   • Output: Final enhanced 4096x4096 images")
    
    successful_combined = 0
    
    for i, image_path in enumerate(base_images, 1):
        image_name = os.path.basename(image_path)
        print(f"\n🚀✨ Combined Processing {i}/{len(base_images)}: {image_name}")
        
        workflow = create_combined_enhance_workflow(image_name)
        
        if submit_and_wait(workflow, timeout=180):  # Longer timeout for combined processing
            successful_combined += 1
            print(f"✅ Complete: {image_name} → upscaled + enhanced")
        else:
            print(f"❌ Failed: {image_name}")
        
        # Brief pause between combined processing
        if i < len(base_images):
            print("   ⏳ Brief pause...")
            time.sleep(3)
    
    return successful_combined

def main():
    print("🎯 Ukrainian Flower Hat Girl - Stage 3: Face Enhancement")
    
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
    
    # Check what we have
    upscaled_files = glob.glob(f"{OUTPUT_DIR}/ukrainian_flower_4x_*.png")
    base_files = glob.glob(f"{OUTPUT_DIR}/ukrainian_flower_base_*.png")
    
    print(f"\n📊 Available images:")
    print(f"   • Base images (1024x1024): {len(base_files)}")
    print(f"   • Upscaled images (4096x4096): {len(upscaled_files)}")
    
    # Choose processing method
    if upscaled_files:
        print("\n🎯 Using Stage 3A: Enhancing already upscaled images")
        successful = enhance_faces_only()
        output_prefix = "ukrainian_flower_enhanced"
    else:
        print("\n🎯 Using Stage 3B: Combined upscaling + enhancement")
        successful = combined_upscale_and_enhance()
        output_prefix = "ukrainian_flower_final"
    
    if not successful:
        print("❌ Face enhancement failed!")
        return 1
    
    # Show results
    enhanced_files = glob.glob(f"{OUTPUT_DIR}/{output_prefix}_*.png")
    enhanced_files.sort(key=os.path.getmtime, reverse=True)
    
    print(f"\n🎉 STAGE 3 COMPLETE!")
    print("=" * 70)
    print("✨ Ukrainian flower hat girl faces enhanced with CodeFormer")
    print(f"📊 Final enhanced images: {len(enhanced_files)}")
    print(f"📁 Latest enhanced files:")
    
    for img in enhanced_files[:5]:
        file_size = os.path.getsize(img) / (1024*1024)  # MB
        print(f"   • {os.path.basename(img)} ({file_size:.1f}MB)")
    
    print(f"\n👀 View final images: feh ComfyUI/output/{output_prefix}_*.png")
    print("🌻 Your Ukrainian flower hat girl collection is complete!")
    
    return 0

if __name__ == "__main__":
    exit(main())