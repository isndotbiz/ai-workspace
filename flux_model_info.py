#!/usr/bin/env python3
"""
FLUX Model Information and Comparison Script
Shows available models and their specifications
"""

import os
import json
from pathlib import Path

def get_file_size_gb(filepath):
    """Get file size in GB"""
    if os.path.exists(filepath):
        size_bytes = os.path.getsize(filepath)
        return size_bytes / (1024**3)
    return 0

def main():
    workspace_root = "/home/jdm/ai-workspace"
    diffusion_models_dir = f"{workspace_root}/ComfyUI/models/diffusion_models"
    checkpoints_dir = f"{workspace_root}/ComfyUI/models/checkpoints"
    workflows_dir = f"{workspace_root}/workflows"
    
    print("🔍 FLUX MODEL ANALYSIS")
    print("=" * 50)
    print()
    
    # Check available models
    models = {
        "GGUF Quantized": {
            "file": "flux1-dev-Q3_K_S.gguf",
            "path": f"{diffusion_models_dir}/flux1-dev-Q3_K_S.gguf",
            "workflow": f"{workflows_dir}/flux_kontext.json",
            "loader": "UnetLoaderGGUF",
            "description": "Quantized to Q3_K_S for maximum memory efficiency",
            "benefits": ["Lowest VRAM usage", "Fastest loading", "GGUF custom nodes"],
            "use_case": "Best for RTX 4060 Ti with limited VRAM"
        },
        "FP8 Scaled": {
            "file": "flux1-dev-kontext_fp8_scaled.safetensors", 
            "path": f"{diffusion_models_dir}/flux1-dev-kontext_fp8_scaled.safetensors",
            "workflow": f"{workflows_dir}/flux_kontext_fp8.json",
            "loader": "UNETLoader",
            "description": "ComfyUI-optimized FP8 quantization from Comfy-Org",
            "benefits": ["Good memory efficiency", "Standard ComfyUI nodes", "Quality preserved"],
            "use_case": "Best balance of quality and performance"
        },
        "Full Precision": {
            "file": "flux1-dev.safetensors",
            "path": f"{checkpoints_dir}/flux1-dev.safetensors", 
            "workflow": "Standard Flux workflow",
            "loader": "CheckpointLoaderSimple",
            "description": "Original full precision model",
            "benefits": ["Maximum quality", "No quantization artifacts", "Full model weights"],
            "use_case": "When quality is more important than memory usage"
        },
        "Kontext Full": {
            "file": "flux1-kontext-dev.safetensors",
            "path": f"{checkpoints_dir}/flux1-kontext-dev.safetensors",
            "workflow": "Kontext-specific workflow needed", 
            "loader": "CheckpointLoaderSimple",
            "description": "Full precision Kontext model for image-to-image",
            "benefits": ["Context-aware generation", "Image-to-image capability", "Full precision"],
            "use_case": "Advanced image editing and context-aware generation"
        }
    }
    
    print("📊 AVAILABLE MODELS:")
    print("-" * 50)
    
    for name, info in models.items():
        size_gb = get_file_size_gb(info["path"])
        exists = "✅" if size_gb > 0 else "❌"
        workflow_exists = "✅" if os.path.exists(info["workflow"]) else "❌" if info["workflow"].endswith(".json") else "⚪"
        
        print(f"{exists} {name}")
        print(f"   File: {info['file']}")
        print(f"   Size: {size_gb:.1f} GB" if size_gb > 0 else "   Size: Not downloaded")
        print(f"   Loader: {info['loader']}")
        print(f"   Workflow: {workflow_exists} {os.path.basename(info['workflow']) if info['workflow'].endswith('.json') else info['workflow']}")
        print(f"   Description: {info['description']}")
        print(f"   Use case: {info['use_case']}")
        print()
    
    print("🎯 CURRENT WORKFLOW STATUS:")
    print("-" * 50)
    
    # Check which workflows are ready
    workflows = [
        ("flux_kontext.json", "GGUF Quantized"),
        ("flux_kontext_fp8.json", "FP8 Scaled")
    ]
    
    for workflow_file, model_type in workflows:
        workflow_path = f"{workflows_dir}/{workflow_file}"
        if os.path.exists(workflow_path):
            print(f"✅ {workflow_file} - Ready for {model_type} model")
            
            # Check if corresponding model exists
            if model_type == "GGUF Quantized":
                model_exists = os.path.exists(f"{diffusion_models_dir}/flux1-dev-Q3_K_S.gguf")
            else:  # FP8 Scaled
                model_exists = os.path.exists(f"{diffusion_models_dir}/flux1-dev-kontext_fp8_scaled.safetensors")
                
            model_status = "✅ Model available" if model_exists else "❌ Model missing"
            print(f"   {model_status}")
        else:
            print(f"❌ {workflow_file} - Missing")
        print()
    
    print("🚀 USAGE RECOMMENDATIONS:")
    print("-" * 50)
    print("• Default: Use FP8 scaled model (best balance)")
    print("• Memory constrained: Use GGUF quantized model")
    print("• Maximum quality: Use full precision models")
    print("• Image editing: Use Kontext models")
    print()
    
    print("💡 WARP COMMANDS:")
    print("-" * 50)
    print("# Use FP8 scaled model (default)")
    print('warp run flux-kontext "your prompt"')
    print()
    print("# Use GGUF model")  
    print('WARP_FLUX_MODEL=gguf warp run flux-kontext "your prompt"')
    print()
    print("# Quick test")
    print('warp run flux-kontext "elegant businesswoman in modern office"')

if __name__ == "__main__":
    main()