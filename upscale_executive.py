#!/usr/bin/env python3

import json
import requests
import time
import os

# 4x Upscaler for Enhanced Executive Portrait
print("\n🚀 ULTRA HIGH-RES UPSCALER - 4X ENHANCEMENT")
print("=" * 50)

COMFY_URL = "http://localhost:8188"
INPUT_IMAGE = "enhanced_executive_ultra_00001_.png"

def create_upscale_workflow(input_image):
    """Create 4x upscaling workflow with face enhancement"""
    
    workflow = {
        # Load the generated image
        "1": {
            "inputs": {
                "image": input_image,
                "upload": "image"
            },
            "class_type": "LoadImage"
        },
        
        # Load upscaling model
        "2": {
            "inputs": {
                "model_name": "4x-UltraSharp.pth"  # High-quality 4x upscaler
            },
            "class_type": "UpscaleModelLoader"
        },
        
        # Perform 4x upscaling
        "3": {
            "inputs": {
                "upscale_model": ["2", 0],
                "image": ["1", 0]
            },
            "class_type": "ImageUpscaleWithModel"
        },
        
        # Load VAE for encoding/decoding
        "4": {
            "inputs": {
                "vae_name": "ae.safetensors"
            },
            "class_type": "VAELoader"
        },
        
        # Encode upscaled image to latent
        "5": {
            "inputs": {
                "pixels": ["3", 0],
                "vae": ["4", 0]
            },
            "class_type": "VAEEncode"
        },
        
        # Load Flux model for refinement
        "6": {
            "inputs": {
                "unet_name": "flux1-dev-kontext_fp8_scaled.safetensors",
                "weight_dtype": "fp8_e4m3fn"
            },
            "class_type": "UNETLoader"
        },
        
        # Load CLIP
        "7": {
            "inputs": {
                "clip_name1": "clip_l.safetensors",
                "clip_name2": "t5xxl_fp8_e4m3fn.safetensors",
                "type": "flux"
            },
            "class_type": "DualCLIPLoader"
        },
        
        # Enhancement prompt
        "8": {
            "inputs": {
                "text": "ultra high resolution, enhanced details, sharp focus, professional photography, perfect skin, flawless face, high quality, masterpiece",
                "clip": ["7", 0]
            },
            "class_type": "CLIPTextEncode"
        },
        
        # Negative prompt
        "9": {
            "inputs": {
                "text": "blurry, low quality, pixelated, artifacts, distorted, soft focus",
                "clip": ["7", 0]
            },
            "class_type": "CLIPTextEncode"
        },
        
        # Flux guidance
        "10": {
            "inputs": {
                "conditioning": ["8", 0],
                "guidance": 3.0
            },
            "class_type": "FluxGuidance"
        },
        
        # Refinement sampling (low denoising to preserve original)
        "11": {
            "inputs": {
                "seed": int(time.time()) % 1000000,
                "steps": 8,
                "cfg": 1.0,
                "sampler_name": "euler",
                "scheduler": "simple",
                "denoise": 0.3,  # Light denoising to preserve original
                "model": ["6", 0],
                "positive": ["10", 0],
                "negative": ["9", 0],
                "latent_image": ["5", 0]
            },
            "class_type": "KSampler"
        },
        
        # Decode refined image
        "12": {
            "inputs": {
                "samples": ["11", 0],
                "vae": ["4", 0]
            },
            "class_type": "VAEDecode"
        },
        
        # Save ultra high-res image
        "13": {
            "inputs": {
                "filename_prefix": "ultra_executive_4x",
                "images": ["12", 0]
            },
            "class_type": "SaveImage"
        }
    }
    
    return workflow

def submit_upscale(workflow):
    """Submit upscaling to ComfyUI"""
    try:
        response = requests.post(f"{COMFY_URL}/prompt", json={"prompt": workflow}, timeout=10)
        if response.status_code == 200:
            return response.json().get('prompt_id')
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Submission failed: {e}")
        return None

def wait_for_upscale(prompt_id, timeout=600):
    """Wait for upscaling completion"""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{COMFY_URL}/history/{prompt_id}", timeout=5)
            if response.status_code == 200:
                history = response.json()
                if prompt_id in history and history[prompt_id].get('outputs'):
                    return True
            
            elapsed = time.time() - start_time
            if int(elapsed) % 30 == 0 and elapsed > 20:
                print(f"   🔄 Upscaling progress: {elapsed:.0f}s elapsed...")
            
            time.sleep(3)
            
        except Exception:
            time.sleep(3)
    
    return False

def main():
    print("🎯 Starting 4x upscaling process...")
    print("⚙️  Configuration:")
    print("   • Input: enhanced_executive_ultra_00001_.png (1216x1216)")
    print("   • Output: ~4864x4864 ultra high resolution")
    print("   • Upscaler: 4x-UltraSharp model")
    print("   • Post-processing: Flux refinement")
    
    # Check if input image exists
    input_path = f"ComfyUI/output/{INPUT_IMAGE}"
    if not os.path.exists(input_path):
        print(f"❌ Input image not found: {input_path}")
        return 1
    
    print(f"\n📁 Input image: {INPUT_IMAGE}")
    print(f"📊 File size: {os.path.getsize(input_path) / (1024*1024):.1f} MB")
    
    # Create upscaling workflow
    workflow = create_upscale_workflow(INPUT_IMAGE)
    
    print("\n🚀 Submitting 4x upscaling...")
    prompt_id = submit_upscale(workflow)
    
    if not prompt_id:
        return 1
    
    print(f"✅ Upscaling queued: {prompt_id}")
    print("⏳ Processing 4x upscale (this may take 5-10 minutes)...")
    print("   This will create an ultra high-resolution version!")
    
    if wait_for_upscale(prompt_id):
        print("\n🎉 ULTRA HIGH-RES UPSCALING COMPLETE!")
        print("=" * 50)
        
        # Check output file
        output_files = [f for f in os.listdir("ComfyUI/output") if f.startswith("ultra_executive_4x")]
        if output_files:
            latest_file = max(output_files)
            output_path = f"ComfyUI/output/{latest_file}"
            file_size = os.path.getsize(output_path) / (1024*1024)
            
            print(f"📸 Ultra high-res image generated!")
            print(f"📁 Output: {latest_file}")
            print(f"📊 File size: {file_size:.1f} MB")
            print(f"🎯 Expected resolution: ~4864x4864 pixels")
            print("\n💡 View with:")
            print(f"   feh ComfyUI/output/{latest_file}")
        
        return 0
    else:
        print("❌ Upscaling timed out")
        return 1

if __name__ == "__main__":
    exit(main())