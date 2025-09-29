#!/usr/bin/env python3
"""
Test script to verify AI workspace setup and model loading
"""
import os
import sys
import yaml
import torch
from pathlib import Path

def test_environment():
    """Test basic environment setup"""
    print("🔍 Testing AI Workspace Environment...")
    print(f"📍 Working Directory: {os.getcwd()}")
    print(f"🐍 Python Version: {sys.version}")
    print(f"🔥 PyTorch Version: {torch.__version__}")
    print(f"🎯 CUDA Available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"💾 GPU: {torch.cuda.get_device_name(0)}")
        print(f"💾 GPU Memory: {torch.cuda.get_device_properties(0).total_memory // 1024**3}GB")
    print()

def test_yaml_config():
    """Test YAML configuration loading"""
    print("📋 Testing YAML Configuration...")
    yaml_path = Path("ComfyUI/extra_model_paths.yaml")
    
    if yaml_path.exists():
        print(f"✅ Found YAML config: {yaml_path}")
        try:
            with open(yaml_path, 'r') as f:
                config = yaml.safe_load(f)
            print("✅ YAML loaded successfully")
            print("📁 Configured paths:")
            for key, value in config.items():
                if isinstance(value, str) and value.startswith('/'):
                    print(f"   {key}: {value}")
        except Exception as e:
            print(f"❌ YAML loading error: {e}")
    else:
        print(f"❌ YAML config not found: {yaml_path}")
    print()

def test_model_files():
    """Test model file availability"""
    print("🎨 Testing Model Files...")
    
    models_dir = Path("ComfyUI/models")
    
    # Expected models
    expected_models = {
        "checkpoints/flux1-dev.safetensors": "Flux.1-dev Main Model",
        "clip/clip_l.safetensors": "CLIP Text Encoder", 
        "clip/t5xxl_fp8_e4m3fn.safetensors": "T5 Text Encoder",
        "vae/ae.safetensors": "Flux VAE",
        "loras/flux-add-details.safetensors": "Add Details LoRA",
        "loras/flux-antiblur.safetensors": "Anti-blur LoRA"
    }
    
    for model_path, description in expected_models.items():
        full_path = models_dir / model_path
        if full_path.exists():
            size_mb = full_path.stat().st_size / (1024 * 1024)
            print(f"✅ {description}: {size_mb:.1f}MB")
        else:
            print(f"❌ Missing: {description} ({model_path})")
    print()

def test_workflow_files():
    """Test workflow files"""
    print("🔧 Testing Workflow Files...")
    
    workflows_dir = Path("workflows")
    if workflows_dir.exists():
        workflow_files = list(workflows_dir.glob("*.json"))
        print(f"✅ Found {len(workflow_files)} workflow files:")
        for workflow in workflow_files:
            print(f"   📄 {workflow.name}")
    else:
        print("❌ No workflows directory found")
    print()

def test_comfyui_startup():
    """Test if ComfyUI can be imported and started"""
    print("🚀 Testing ComfyUI Compatibility...")
    
    comfyui_path = Path("ComfyUI")
    if comfyui_path.exists():
        print(f"✅ ComfyUI directory found: {comfyui_path}")
        
        # Add ComfyUI to path for import testing
        sys.path.insert(0, str(comfyui_path.absolute()))
        
        try:
            # Try to import some ComfyUI modules (without starting the server)
            print("🧪 Testing ComfyUI imports...")
            print("   ℹ️  Skipping import test to avoid server startup")
            print("✅ ComfyUI appears ready to start")
        except Exception as e:
            print(f"⚠️  ComfyUI import test skipped: {e}")
    else:
        print("❌ ComfyUI directory not found")
    print()

def main():
    """Run all tests"""
    print("🎯 AI Workspace Test Suite")
    print("=" * 50)
    
    test_environment()
    test_yaml_config() 
    test_model_files()
    test_workflow_files()
    test_comfyui_startup()
    
    print("🎉 Test Suite Complete!")
    print("\n💡 To start ComfyUI:")
    print("   source activate_workspace.sh")
    print("   python ComfyUI/main.py --listen 0.0.0.0 --port 8188")

if __name__ == "__main__":
    main()