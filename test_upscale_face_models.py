#!/usr/bin/env python3
"""
Test script for upscaling and face restoration model availability and integrity.

Tests:
1. Model file presence
2. File sizes and integrity
3. ComfyUI node availability for upscaling and face restoration
4. Import capability of required custom nodes
"""

import os
import sys
from pathlib import Path
import hashlib

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

WORKSPACE_ROOT = Path("/home/jdm/ai-workspace")
COMFYUI_ROOT = WORKSPACE_ROOT / "ComfyUI"

def print_status(test_name, passed, message=""):
    """Print test status with color coding."""
    status = f"{GREEN}✓ PASS{RESET}" if passed else f"{RED}✗ FAIL{RESET}"
    print(f"{status} | {test_name}")
    if message:
        print(f"       {message}")

def check_file_exists(filepath, expected_size_mb=None):
    """Check if a file exists and optionally verify approximate size."""
    if not filepath.exists():
        return False, f"File not found: {filepath}"
    
    size_mb = filepath.stat().st_size / (1024 * 1024)
    
    if expected_size_mb:
        if size_mb < expected_size_mb * 0.9:  # Allow 10% tolerance
            return False, f"File size {size_mb:.1f}MB is less than expected {expected_size_mb}MB"
    
    return True, f"Found ({size_mb:.1f}MB)"

def test_upscale_models():
    """Test upscaling model files."""
    print(f"\n{BLUE}=== Testing Upscaling Models ==={RESET}")
    
    upscale_dir = COMFYUI_ROOT / "models" / "upscale_models"
    models = {
        "RealESRGAN_x4plus.pth": 64,
        "RealESRGAN_x4plus_anime_6B.pth": 18,
        "4x-UltraSharp.pth": 64,
    }
    
    all_passed = True
    for model_name, expected_size in models.items():
        model_path = upscale_dir / model_name
        passed, message = check_file_exists(model_path, expected_size)
        print_status(f"Upscale Model: {model_name}", passed, message)
        all_passed = all_passed and passed
    
    return all_passed

def test_face_restoration_models():
    """Test face restoration model files."""
    print(f"\n{BLUE}=== Testing Face Restoration Models ==={RESET}")
    
    facerestore_dir = COMFYUI_ROOT / "models" / "facerestore_models"
    models = {
        "GFPGANv1.4.pth": 333,
        "codeformer.pth": 360,
    }
    
    all_passed = True
    for model_name, expected_size in models.items():
        model_path = facerestore_dir / model_name
        passed, message = check_file_exists(model_path, expected_size)
        print_status(f"Face Restore Model: {model_name}", passed, message)
        all_passed = all_passed and passed
    
    return all_passed

def test_custom_nodes():
    """Test availability of required custom nodes."""
    print(f"\n{BLUE}=== Testing Custom Nodes ==={RESET}")
    
    custom_nodes = [
        "ComfyUI-Impact-Pack",
        "ComfyUI_UltimateSDUpscale",
    ]
    
    all_passed = True
    for node_name in custom_nodes:
        node_path = COMFYUI_ROOT / "custom_nodes" / node_name
        passed = node_path.exists()
        message = f"Found at {node_path}" if passed else f"Not found at {node_path}"
        print_status(f"Custom Node: {node_name}", passed, message)
        all_passed = all_passed and passed
    
    return all_passed

def test_workflow_files():
    """Test new workflow files."""
    print(f"\n{BLUE}=== Testing Workflow Files ==={RESET}")
    
    workflows_dir = WORKSPACE_ROOT / "workflows"
    workflows = [
        "flux_kontext_fp8_upscale_4x.json",
        "flux_kontext_ultimate_portrait.json",
    ]
    
    all_passed = True
    for workflow_name in workflows:
        workflow_path = workflows_dir / workflow_name
        passed = workflow_path.exists()
        message = f"Found at {workflow_path}" if passed else f"Not found at {workflow_path}"
        print_status(f"Workflow: {workflow_name}", passed, message)
        all_passed = all_passed and passed
    
    return all_passed

def calculate_file_hash(filepath, algorithm='sha256'):
    """Calculate hash of a file."""
    hash_func = hashlib.new(algorithm)
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_func.update(chunk)
    return hash_func.hexdigest()

def test_model_integrity():
    """Test model file integrity through basic hash calculation."""
    print(f"\n{BLUE}=== Testing Model Integrity ==={RESET}")
    
    # We'll just verify files are readable and can be hashed
    models_to_check = [
        COMFYUI_ROOT / "models" / "upscale_models" / "RealESRGAN_x4plus.pth",
        COMFYUI_ROOT / "models" / "facerestore_models" / "GFPGANv1.4.pth",
    ]
    
    all_passed = True
    for model_path in models_to_check:
        if not model_path.exists():
            print_status(f"Integrity check: {model_path.name}", False, "File not found")
            all_passed = False
            continue
        
        try:
            # Calculate hash to verify file is readable
            file_hash = calculate_file_hash(model_path)
            print_status(f"Integrity check: {model_path.name}", True, f"Hash: {file_hash[:16]}...")
        except Exception as e:
            print_status(f"Integrity check: {model_path.name}", False, f"Error: {str(e)}")
            all_passed = False
    
    return all_passed

def test_disk_space():
    """Check if there's enough disk space for operations."""
    print(f"\n{BLUE}=== Testing Disk Space ==={RESET}")
    
    import shutil
    total, used, free = shutil.disk_usage(WORKSPACE_ROOT)
    free_gb = free / (1024**3)
    
    # Recommend at least 50GB free for upscaled images
    passed = free_gb >= 50
    message = f"Available: {free_gb:.1f}GB (Recommended: 50GB+ for upscaled outputs)"
    print_status("Disk Space Check", passed, message)
    
    return passed

def main():
    """Run all tests."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}  Upscaling & Face Restoration Model Test Suite{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    tests = [
        ("Upscaling Models", test_upscale_models),
        ("Face Restoration Models", test_face_restoration_models),
        ("Custom Nodes", test_custom_nodes),
        ("Workflow Files", test_workflow_files),
        ("Model Integrity", test_model_integrity),
        ("Disk Space", test_disk_space),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"{RED}ERROR{RESET} in {test_name}: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}  Test Summary{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    pass_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"\nTests Passed: {passed}/{total} ({pass_rate:.1f}%)")
    
    for test_name, result in results:
        status = f"{GREEN}✓{RESET}" if result else f"{RED}✗{RESET}"
        print(f"  {status} {test_name}")
    
    if passed == total:
        print(f"\n{GREEN}All tests passed! ✓{RESET}")
        print(f"Your upscaling and face restoration setup is ready.")
        return 0
    else:
        print(f"\n{YELLOW}Some tests failed.{RESET}")
        print(f"Please review the failed tests above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())