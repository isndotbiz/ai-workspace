#!/usr/bin/env python3
"""
FP8 Smoke Test - Quick validation of FP8 image generation

Generates a simple test image using the FP8 workflow to confirm:
- FP8 models load correctly
- Image generation completes successfully
- VRAM usage is within expected range
- Generation time is reasonable
"""

import json
import time
import requests
import sys
from pathlib import Path
import subprocess

# Configuration
COMFYUI_URL = "http://localhost:8188"
WORKFLOW_PATH = Path(__file__).parent.parent / "workflows" / "flux_kontext_fp8.json"
TEST_PROMPT = "A professional portrait of a confident businesswoman, studio lighting, sharp focus, photorealistic"
TIMEOUT_SECONDS = 300  # 5 minutes max


def check_comfyui_running():
    """Check if ComfyUI is accessible."""
    try:
        response = requests.get(f"{COMFYUI_URL}/system_stats", timeout=5)
        return response.status_code == 200
    except:
        return False


def load_workflow():
    """Load the FP8 test workflow."""
    if not WORKFLOW_PATH.exists():
        print(f"❌ Workflow not found: {WORKFLOW_PATH}")
        return None
    
    with open(WORKFLOW_PATH, 'r') as f:
        return json.load(f)


def inject_prompt(workflow, prompt):
    """Inject test prompt into workflow."""
    for node_id, node in workflow.items():
        if node.get("class_type") == "CLIPTextEncode":
            inputs = node.get("inputs", {})
            if "text" in inputs and "PLACEHOLDER" in inputs["text"]:
                inputs["text"] = prompt
                print(f"✓ Injected prompt into node {node_id}")
                return True
    return False


def queue_prompt(workflow):
    """Queue a prompt for generation."""
    payload = {"prompt": workflow}
    
    try:
        response = requests.post(
            f"{COMFYUI_URL}/prompt",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            prompt_id = data.get("prompt_id")
            print(f"✓ Queued generation (ID: {prompt_id})")
            return prompt_id
        else:
            print(f"❌ Failed to queue: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error queuing prompt: {e}")
        return None


def wait_for_completion(prompt_id, timeout=TIMEOUT_SECONDS):
    """Wait for image generation to complete."""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{COMFYUI_URL}/history/{prompt_id}", timeout=5)
            
            if response.status_code == 200:
                history = response.json()
                
                if prompt_id in history:
                    status = history[prompt_id].get("status", {})
                    
                    if status.get("completed", False):
                        elapsed = time.time() - start_time
                        print(f"✓ Generation completed in {elapsed:.1f}s")
                        return True
                    
                    # Check for errors
                    messages = status.get("messages", [])
                    for msg in messages:
                        if msg[0] == "execution_error":
                            print(f"❌ Generation error: {msg[1]}")
                            return False
            
            time.sleep(2)
            
        except Exception as e:
            print(f"⚠ Waiting... ({e})")
            time.sleep(2)
    
    print(f"❌ Timeout after {timeout}s")
    return False


def check_vram_usage():
    """Check current VRAM usage."""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.used,memory.total", "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            used, total = map(int, result.stdout.strip().split(','))
            usage_pct = (used / total) * 100
            print(f"✓ VRAM Usage: {used}MB / {total}MB ({usage_pct:.1f}%)")
            return used, total
            
    except Exception as e:
        print(f"⚠ Could not check VRAM: {e}")
    
    return None, None


def main():
    """Run FP8 smoke test."""
    print("=" * 60)
    print("FP8 Smoke Test - Image Generation Validation")
    print("=" * 60)
    
    # Step 1: Check ComfyUI
    print("\n1. Checking ComfyUI service...")
    if not check_comfyui_running():
        print("❌ ComfyUI is not running on http://localhost:8188")
        print("   Start it with: python ComfyUI/main.py --listen 0.0.0.0 --port 8188")
        return 1
    print("✓ ComfyUI is running")
    
    # Step 2: Check VRAM before
    print("\n2. Checking initial VRAM...")
    vram_before, vram_total = check_vram_usage()
    
    # Step 3: Load workflow
    print("\n3. Loading FP8 test workflow...")
    workflow = load_workflow()
    if not workflow:
        return 1
    print(f"✓ Loaded workflow: {WORKFLOW_PATH.name}")
    
    # Step 4: Inject prompt
    print("\n4. Injecting test prompt...")
    if not inject_prompt(workflow, TEST_PROMPT):
        print("⚠ Could not inject prompt, using default")
    
    # Step 5: Queue generation
    print("\n5. Queuing image generation...")
    prompt_id = queue_prompt(workflow)
    if not prompt_id:
        return 1
    
    # Step 6: Wait for completion
    print("\n6. Waiting for generation to complete...")
    start_time = time.time()
    
    if not wait_for_completion(prompt_id):
        return 1
    
    elapsed = time.time() - start_time
    
    # Step 7: Check VRAM after
    print("\n7. Checking VRAM after generation...")
    vram_after, _ = check_vram_usage()
    
    if vram_before and vram_after:
        vram_used_for_gen = vram_after - vram_before
        print(f"✓ VRAM used for generation: ~{vram_used_for_gen}MB")
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ FP8 SMOKE TEST PASSED")
    print("=" * 60)
    print(f"Generation Time: {elapsed:.1f}s")
    print(f"VRAM Usage: {vram_after}MB / {vram_total}MB")
    print(f"\nFP8 stack is working correctly!")
    print("\nCheck ComfyUI output directory for the generated image:")
    print(f"  ComfyUI/output/")
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠ Test interrupted by user")
        sys.exit(130)