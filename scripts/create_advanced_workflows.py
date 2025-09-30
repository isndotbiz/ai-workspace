#!/usr/bin/env python3
"""
Advanced Workflow Generator
Creates example workflows for:
1. Image upscaling (Ultimate SD Upscale + ESRGAN)
2. Face detail enhancement (Impact Pack FaceDetailer)
3. Multi-image Kontext composition
4. Combined pipelines (Kontext → Face Detail → Upscale)
"""

import json
from pathlib import Path

WORKFLOWS_DIR = Path(__file__).parent.parent / "workflows" / "advanced"
WORKFLOWS_DIR.mkdir(parents=True, exist_ok=True)

print("🎨 Creating Advanced Workflows for ComfyUI")
print("=" * 70)

# Workflow 1: Simple 4x Upscale with UltraSharp
workflow_upscale_simple = {
    "1": {
        "inputs": {"image": "input_image.png", "upload": "image"},
        "class_type": "LoadImage",
        "_meta": {"title": "Load Input Image"}
    },
    "2": {
        "inputs": {
            "upscale_model_name": "4x-UltraSharp.pth"
        },
        "class_type": "UpscaleModelLoader",
        "_meta": {"title": "Load Upscale Model"}
    },
    "3": {
        "inputs": {
            "upscale_model": ["2", 0],
            "image": ["1", 0]
        },
        "class_type": "ImageUpscaleWithModel",
        "_meta": {"title": "Upscale 4x"}
    },
    "4": {
        "inputs": {
            "filename_prefix": "upscaled_4x",
            "images": ["3", 0]
        },
        "class_type": "SaveImage",
        "_meta": {"title": "Save Upscaled"}
    }
}

# Workflow 2: Ultimate SD Upscale with Tiling (For large images)
workflow_upscale_ultimate = {
    "1": {
        "inputs": {"image": "input_image.png", "upload": "image"},
        "class_type": "LoadImage",
        "_meta": {"title": "Load Input Image"}
    },
    "2": {
        "inputs": {
            "unet_name": "flux1-dev-kontext_fp8_scaled.safetensors",
            "weight_dtype": "fp8_e4m3fn"
        },
        "class_type": "UNETLoader",
        "_meta": {"title": "Load UNet"}
    },
    "3": {
        "inputs": {
            "clip_name1": "clip_l.safetensors",
            "clip_name2": "t5xxl_fp8_e4m3fn.safetensors",
            "type": "flux"
        },
        "class_type": "DualCLIPLoader",
        "_meta": {"title": "Load CLIP"}
    },
    "4": {
        "inputs": {"vae_name": "ae.safetensors"},
        "class_type": "VAELoader",
        "_meta": {"title": "Load VAE"}
    },
    "5": {
        "inputs": {
            "upscale_model_name": "4x-UltraSharp.pth"
        },
        "class_type": "UpscaleModelLoader",
        "_meta": {"title": "Load Upscale Model"}
    },
    "6": {
        "inputs": {
            "text": "high quality, detailed, sharp, professional photography",
            "clip": ["3", 0]
        },
        "class_type": "CLIPTextEncode",
        "_meta": {"title": "Positive Prompt"}
    },
    "7": {
        "inputs": {
            "text": "blurry, low quality, artifacts, noise",
            "clip": ["3", 0]
        },
        "class_type": "CLIPTextEncode",
        "_meta": {"title": "Negative Prompt"}
    },
    "8": {
        "inputs": {
            "image": ["1", 0],
            "upscale_model": ["5", 0],
            "model": ["2", 0],
            "positive": ["6", 0],
            "negative": ["7", 0],
            "vae": ["4", 0],
            "upscale_by": 4.0,
            "tile_width": 1024,
            "tile_height": 1024,
            "seam_fix_mode": "Band Pass",
            "seam_fix_denoise": 0.3,
            "seam_fix_width": 64,
            "seam_fix_mask_blur": 8,
            "seam_fix_padding": 16,
            "seed": 42,
            "steps": 20,
            "cfg": 3.5,
            "sampler_name": "euler",
            "scheduler": "simple",
            "denoise": 0.35
        },
        "class_type": "UltimateSDUpscale",
        "_meta": {"title": "Ultimate SD Upscale 4x (Tiled)"}
    },
    "9": {
        "inputs": {
            "filename_prefix": "ultimate_upscaled_4x",
            "images": ["8", 0]
        },
        "class_type": "SaveImage",
        "_meta": {"title": "Save Result"}
    }
}

# Workflow 3: Face Detail Enhancement
workflow_face_detail = {
    "1": {
        "inputs": {"image": "input_portrait.png", "upload": "image"},
        "class_type": "LoadImage",
        "_meta": {"title": "Load Portrait"}
    },
    "2": {
        "inputs": {
            "unet_name": "flux1-dev-kontext_fp8_scaled.safetensors",
            "weight_dtype": "fp8_e4m3fn"
        },
        "class_type": "UNETLoader",
        "_meta": {"title": "Load UNet"}
    },
    "3": {
        "inputs": {
            "clip_name1": "clip_l.safetensors",
            "clip_name2": "t5xxl_fp8_e4m3fn.safetensors",
            "type": "flux"
        },
        "class_type": "DualCLIPLoader",
        "_meta": {"title": "Load CLIP"}
    },
    "4": {
        "inputs": {"vae_name": "ae.safetensors"},
        "class_type": "VAELoader",
        "_meta": {"title": "Load VAE"}
    },
    "5": {
        "inputs": {
            "text": "detailed face, sharp features, high quality skin texture, professional portrait",
            "clip": ["3", 0]
        },
        "class_type": "CLIPTextEncode",
        "_meta": {"title": "Face Enhancement Prompt"}
    },
    "6": {
        "inputs": {
            "text": "blurry, low quality, bad anatomy, distorted face",
            "clip": ["3", 0]
        },
        "class_type": "CLIPTextEncode",
        "_meta": {"title": "Negative Prompt"}
    },
    "7": {
        "inputs": {
            "image": ["1", 0],
            "model": ["2", 0],
            "clip": ["3", 0],
            "vae": ["4", 0],
            "positive": ["5", 0],
            "negative": ["6", 0],
            "bbox_detector": "bbox/face_yolov8m.pt",
            "bbox_threshold": 0.5,
            "bbox_dilation": 10,
            "crop_factor": 1.5,
            "guide_size": 512,
            "guide_size_for": True,
            "max_size": 1024,
            "seed": 42,
            "steps": 25,
            "cfg": 4.0,
            "sampler_name": "euler",
            "scheduler": "simple",
            "denoise": 0.4,
            "feather": 20,
            "noise_mask": True,
            "force_inpaint": True
        },
        "class_type": "FaceDetailer",
        "_meta": {"title": "Face Detailer (Impact Pack)"}
    },
    "8": {
        "inputs": {
            "filename_prefix": "face_detailed",
            "images": ["7", 0]
        },
        "class_type": "SaveImage",
        "_meta": {"title": "Save Enhanced Portrait"}
    }
}

# Workflow 4: Combined Pipeline - Generate → Face Detail → Upscale
workflow_combined_full = {
    "1": {
        "inputs": {
            "unet_name": "flux1-dev-kontext_fp8_scaled.safetensors",
            "weight_dtype": "fp8_e4m3fn"
        },
        "class_type": "UNETLoader",
        "_meta": {"title": "Load FP8 UNet"}
    },
    "2": {
        "inputs": {
            "clip_name1": "clip_l.safetensors",
            "clip_name2": "t5xxl_fp8_e4m3fn.safetensors",
            "type": "flux"
        },
        "class_type": "DualCLIPLoader",
        "_meta": {"title": "Load CLIP"}
    },
    "3": {
        "inputs": {"vae_name": "ae.safetensors"},
        "class_type": "VAELoader",
        "_meta": {"title": "Load VAE"}
    },
    "4": {
        "inputs": {
            "lora_name": "flux-RealismLora.safetensors",
            "strength_model": 0.8,
            "strength_clip": 0.8,
            "model": ["1", 0],
            "clip": ["2", 0]
        },
        "class_type": "LoraLoader",
        "_meta": {"title": "Realism LoRA"}
    },
    "5": {
        "inputs": {
            "text": "REPLACE_WITH_YOUR_PROMPT",
            "clip": ["4", 1]
        },
        "class_type": "CLIPTextEncode",
        "_meta": {"title": "Main Prompt"}
    },
    "6": {
        "inputs": {
            "text": "blurry, low quality, bad anatomy, distorted",
            "clip": ["4", 1]
        },
        "class_type": "CLIPTextEncode",
        "_meta": {"title": "Negative Prompt"}
    },
    "7": {
        "inputs": {
            "conditioning": ["5", 0],
            "guidance": 5.0
        },
        "class_type": "FluxGuidance",
        "_meta": {"title": "Flux Guidance"}
    },
    "8": {
        "inputs": {
            "width": 1024,
            "height": 1408,
            "batch_size": 1
        },
        "class_type": "EmptyLatentImage",
        "_meta": {"title": "Portrait Latent"}
    },
    "9": {
        "inputs": {
            "seed": 42,
            "steps": 12,
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
        "_meta": {"title": "Generate Image"}
    },
    "10": {
        "inputs": {
            "samples": ["9", 0],
            "vae": ["3", 0]
        },
        "class_type": "VAEDecode",
        "_meta": {"title": "Decode Latent"}
    },
    "11": {
        "inputs": {
            "image": ["10", 0],
            "model": ["1", 0],
            "clip": ["2", 0],
            "vae": ["3", 0],
            "positive": ["5", 0],
            "negative": ["6", 0],
            "bbox_detector": "bbox/face_yolov8m.pt",
            "bbox_threshold": 0.5,
            "bbox_dilation": 10,
            "crop_factor": 1.5,
            "guide_size": 512,
            "guide_size_for": True,
            "max_size": 1024,
            "seed": 42,
            "steps": 25,
            "cfg": 4.0,
            "sampler_name": "euler",
            "scheduler": "simple",
            "denoise": 0.4,
            "feather": 20,
            "noise_mask": True,
            "force_inpaint": True
        },
        "class_type": "FaceDetailer",
        "_meta": {"title": "Enhance Face Details"}
    },
    "12": {
        "inputs": {
            "upscale_model_name": "4x-UltraSharp.pth"
        },
        "class_type": "UpscaleModelLoader",
        "_meta": {"title": "Load Upscale Model"}
    },
    "13": {
        "inputs": {
            "image": ["11", 0],
            "upscale_model": ["12", 0],
            "model": ["1", 0],
            "positive": ["5", 0],
            "negative": ["6", 0],
            "vae": ["3", 0],
            "upscale_by": 2.0,
            "tile_width": 1024,
            "tile_height": 1024,
            "seam_fix_mode": "Band Pass",
            "seam_fix_denoise": 0.25,
            "seam_fix_width": 64,
            "seam_fix_mask_blur": 8,
            "seam_fix_padding": 16,
            "seed": 42,
            "steps": 15,
            "cfg": 3.5,
            "sampler_name": "euler",
            "scheduler": "simple",
            "denoise": 0.25
        },
        "class_type": "UltimateSDUpscale",
        "_meta": {"title": "Upscale 2x"}
    },
    "14": {
        "inputs": {
            "filename_prefix": "full_pipeline",
            "images": ["13", 0]
        },
        "class_type": "SaveImage",
        "_meta": {"title": "Save Final Result"}
    }
}

# Save workflows
workflows = {
    "upscale_simple_4x.json": workflow_upscale_simple,
    "upscale_ultimate_tiled_4x.json": workflow_upscale_ultimate,
    "face_detail_enhancement.json": workflow_face_detail,
    "full_pipeline_kontext_face_upscale.json": workflow_combined_full
}

for filename, workflow in workflows.items():
    filepath = WORKFLOWS_DIR / filename
    with open(filepath, 'w') as f:
        json.dump(workflow, f, indent=2)
    print(f"✅ Created: {filename}")

print("\n" + "=" * 70)
print("🎉 Advanced Workflows Created Successfully!")
print("=" * 70)
print(f"\nLocation: {WORKFLOWS_DIR}/")
print("\nWorkflows created:")
print("  1. upscale_simple_4x.json - Simple 4x upscale")
print("  2. upscale_ultimate_tiled_4x.json - Tiled upscale for large images")
print("  3. face_detail_enhancement.json - Face detailer with Impact Pack")
print("  4. full_pipeline_kontext_face_upscale.json - Complete pipeline")
print("\nUsage:")
print("  - Load workflows in ComfyUI web interface")
print("  - Replace 'REPLACE_WITH_YOUR_PROMPT' with your prompt")
print("  - Adjust tile sizes based on your VRAM (1024px recommended for 16GB)")
print("\n" + "=" * 70)