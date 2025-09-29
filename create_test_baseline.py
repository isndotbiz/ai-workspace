#!/usr/bin/env python3
"""
Comprehensive Test Generator for FLUX Kontext System
Creates baseline test image and validates entire pipeline
"""

import json
import requests
import time
import os
import sys
from pathlib import Path

# Configuration
WORKSPACE_ROOT = Path("/home/jdm/ai-workspace")
COMFYUI_URL = "http://localhost:8188"
TEST_PROMPT = "ultra-photoreal editorial portrait, 85mm lens, f/2 shallow DOF, golden hour rim light, subtle film grain, natural skin texture, freckles, detailed eyelashes, clean background bokeh, realistic proportions, accurate skin tone, high dynamic range"

def log(message):
    """Log with timestamp"""
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")
    
    # Also log to file
    log_file = WORKSPACE_ROOT / "setup-history.log"
    with open(log_file, "a") as f:
        f.write(f"[{timestamp}] {message}\n")

def check_comfyui_status():
    """Check if ComfyUI server is running and responsive"""
    try:
        response = requests.get(f"{COMFYUI_URL}/system_stats", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            log(f"✅ ComfyUI API responding - Version: {stats['system'].get('comfyui_version', 'Unknown')}")
            return True
        else:
            log(f"❌ ComfyUI API returned status {response.status_code}")
            return False
    except Exception as e:
        log(f"❌ ComfyUI API not reachable: {e}")
        return False

def check_required_files():
    """Verify all required model files are present"""
    required_files = {
        "FP8 Kontext Model": WORKSPACE_ROOT / "ComfyUI/models/diffusion_models/flux1-dev-kontext_fp8_scaled.safetensors",
        "Turbo LoRA": WORKSPACE_ROOT / "ComfyUI/models/loras/FLUX.1-Turbo-Alpha.safetensors",
        "CLIP-L Encoder": WORKSPACE_ROOT / "ComfyUI/models/clip/clip_l.safetensors",
        "T5-XXL Encoder": WORKSPACE_ROOT / "ComfyUI/models/clip/t5xxl_fp8_e4m3fn.safetensors",
        "VAE Decoder": WORKSPACE_ROOT / "ComfyUI/models/vae/ae.safetensors",
        "Turbo Workflow": WORKSPACE_ROOT / "workflows/flux_kontext_fp8_turbo.json"
    }
    
    all_present = True
    total_size_gb = 0
    
    for name, path in required_files.items():
        if path.exists():
            size_gb = path.stat().st_size / (1024**3)
            total_size_gb += size_gb
            log(f"✅ {name}: {size_gb:.1f} GB")
        else:
            log(f"❌ Missing: {name} at {path}")
            all_present = False
    
    log(f"📊 Total model storage: {total_size_gb:.1f} GB")
    return all_present

def create_test_workflow():
    """Create a test workflow with optimized settings"""
    workflow_path = WORKSPACE_ROOT / "workflows/flux_kontext_fp8_turbo.json"
    
    if not workflow_path.exists():
        log("❌ Turbo workflow not found, cannot create test")
        return None
    
    # Load the base workflow
    with open(workflow_path, 'r') as f:
        workflow = json.load(f)
    
    # Modify with test parameters
    test_seed = int(time.time()) % 1000000
    
    # Update workflow parameters
    if "5" in workflow and "inputs" in workflow["5"]:
        workflow["5"]["inputs"]["text"] = TEST_PROMPT
    
    if "8" in workflow and "inputs" in workflow["8"]:
        workflow["8"]["inputs"]["batch_size"] = 1
        
    if "9" in workflow and "inputs" in workflow["9"]:
        workflow["9"]["inputs"]["seed"] = test_seed
        workflow["9"]["inputs"]["steps"] = 8
        workflow["9"]["inputs"]["cfg"] = 1.0
    
    if "7" in workflow and "inputs" in workflow["7"]:
        workflow["7"]["inputs"]["guidance"] = 5.0
    
    return workflow, test_seed

def queue_generation(workflow):
    """Queue the workflow for generation"""
    try:
        payload = {"prompt": workflow}
        response = requests.post(f"{COMFYUI_URL}/prompt", json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if "prompt_id" in result:
                prompt_id = result["prompt_id"]
                log(f"✅ Generation queued - Prompt ID: {prompt_id}")
                return prompt_id
            else:
                log(f"❌ No prompt_id in response: {result}")
                return None
        else:
            log(f"❌ Failed to queue generation: {response.status_code}")
            log(f"Response: {response.text}")
            return None
            
    except Exception as e:
        log(f"❌ Error queuing generation: {e}")
        return None

def wait_for_completion(prompt_id, timeout=300):
    """Wait for generation to complete"""
    start_time = time.time()
    log(f"⏳ Waiting for generation to complete (timeout: {timeout}s)...")
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{COMFYUI_URL}/history/{prompt_id}", timeout=5)
            if response.status_code == 200:
                history = response.json()
                if prompt_id in history:
                    prompt_info = history[prompt_id]
                    if "status" in prompt_info:
                        status = prompt_info["status"]["status_str"]
                        if status == "success":
                            log("✅ Generation completed successfully!")
                            return True, prompt_info
                        elif status == "error":
                            log(f"❌ Generation failed: {prompt_info.get('status', {}).get('messages', 'Unknown error')}")
                            return False, prompt_info
            
            # Check queue status
            queue_response = requests.get(f"{COMFYUI_URL}/queue", timeout=5)
            if queue_response.status_code == 200:
                queue_info = queue_response.json()
                running = queue_info.get("queue_running", [])
                pending = queue_info.get("queue_pending", [])
                
                if any(item.get("prompt_id") == prompt_id for item in running):
                    elapsed = int(time.time() - start_time)
                    print(f"\r🔄 Generation in progress... ({elapsed}s)", end="", flush=True)
                elif not any(item.get("prompt_id") == prompt_id for item in pending):
                    # Not in queue anymore, check history again
                    continue
            
            time.sleep(2)
            
        except Exception as e:
            log(f"⚠️ Error checking status: {e}")
            time.sleep(5)
    
    print()  # New line after progress indicator
    log(f"⏰ Generation timed out after {timeout}s")
    return False, None

def check_output_files():
    """Check if output files were generated"""
    output_dir = WORKSPACE_ROOT / "ComfyUI/output"
    if not output_dir.exists():
        log("❌ Output directory doesn't exist")
        return []
    
    # Look for recent files (within last 5 minutes)
    recent_files = []
    cutoff_time = time.time() - 300  # 5 minutes ago
    
    for file in output_dir.glob("flux_kontext_turbo_*.png"):
        if file.stat().st_mtime > cutoff_time:
            recent_files.append(file)
    
    if recent_files:
        log(f"✅ Found {len(recent_files)} recent output file(s):")
        for file in recent_files:
            size_mb = file.stat().st_size / (1024*1024)
            log(f"   📄 {file.name} ({size_mb:.1f} MB)")
    else:
        log("❌ No recent output files found")
    
    return recent_files

def run_ollama_test():
    """Test Ollama prompt expansion"""
    try:
        import subprocess
        
        # Check if Ollama is available
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            if "llama3.1" in result.stdout:
                log("✅ Ollama + llama3.1:8b available")
                
                # Test prompt expansion
                test_concept = "tech entrepreneur portrait"
                expand_result = subprocess.run([
                    "ollama", "run", "llama3.1:8b",
                    "Transform this into a detailed photorealistic portrait prompt: " + test_concept
                ], capture_output=True, text=True, timeout=30)
                
                if expand_result.returncode == 0 and len(expand_result.stdout.strip()) > 50:
                    log("✅ Prompt expansion working")
                    return True
                else:
                    log("⚠️ Prompt expansion may have issues")
            else:
                log("❌ llama3.1:8b not found in Ollama")
        else:
            log("❌ Ollama not responding")
            
    except Exception as e:
        log(f"⚠️ Ollama test failed: {e}")
    
    return False

def create_test_report(version_tag, success, generation_time=None, output_files=None):
    """Create a comprehensive test report"""
    report = {
        "version": version_tag,
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
        "test_success": success,
        "generation_time_seconds": generation_time,
        "output_files_count": len(output_files) if output_files else 0,
        "test_prompt": TEST_PROMPT,
        "components": {
            "comfyui_api": check_comfyui_status(),
            "required_files": check_required_files(),
            "ollama_available": run_ollama_test()
        }
    }
    
    # Save report
    report_file = WORKSPACE_ROOT / "tests" / f"test_report_{version_tag.replace('.', '_')}.json"
    report_file.parent.mkdir(exist_ok=True)
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    log(f"📋 Test report saved: {report_file}")
    return report

def main():
    if len(sys.argv) > 1:
        version_tag = sys.argv[1]
    else:
        # Get current git tag
        try:
            import subprocess
            result = subprocess.run(["git", "describe", "--tags"], 
                                  capture_output=True, text=True, cwd=WORKSPACE_ROOT)
            version_tag = result.stdout.strip() if result.returncode == 0 else "unknown"
        except:
            version_tag = "unknown"
    
    log("🧪 STARTING COMPREHENSIVE SYSTEM TEST")
    log("=" * 50)
    log(f"Version: {version_tag}")
    log(f"Workspace: {WORKSPACE_ROOT}")
    log("")
    
    # 1. Check prerequisites
    log("1️⃣ Checking prerequisites...")
    if not check_comfyui_status():
        log("❌ ComfyUI not running - start it first")
        return False
    
    if not check_required_files():
        log("❌ Missing required files - run setup first")
        return False
    
    # 2. Test Ollama
    log("\n2️⃣ Testing Ollama integration...")
    ollama_working = run_ollama_test()
    
    # 3. Create and queue test workflow
    log("\n3️⃣ Creating test workflow...")
    workflow_result = create_test_workflow()
    if not workflow_result:
        log("❌ Failed to create test workflow")
        return False
    
    workflow, test_seed = workflow_result
    log(f"📝 Test seed: {test_seed}")
    
    # 4. Queue generation
    log("\n4️⃣ Queuing test generation...")
    prompt_id = queue_generation(workflow)
    if not prompt_id:
        log("❌ Failed to queue generation")
        return False
    
    # 5. Wait for completion
    log("\n5️⃣ Waiting for generation...")
    start_time = time.time()
    success, result_info = wait_for_completion(prompt_id, timeout=300)
    generation_time = time.time() - start_time if success else None
    
    if success:
        log(f"⚡ Generation completed in {generation_time:.1f} seconds")
    
    # 6. Check outputs
    log("\n6️⃣ Checking output files...")
    output_files = check_output_files()
    
    # 7. Create report
    log("\n7️⃣ Creating test report...")
    overall_success = success and len(output_files) > 0
    report = create_test_report(version_tag, overall_success, generation_time, output_files)
    
    # 8. Summary
    log("\n🎯 TEST SUMMARY")
    log("=" * 20)
    log(f"Overall Result: {'✅ PASS' if overall_success else '❌ FAIL'}")
    log(f"API Status: {'✅' if report['components']['comfyui_api'] else '❌'}")
    log(f"Files Present: {'✅' if report['components']['required_files'] else '❌'}")  
    log(f"Generation: {'✅' if success else '❌'}")
    log(f"Output Files: {len(output_files)} generated")
    log(f"Ollama: {'✅' if ollama_working else '⚠️'}")
    
    if generation_time:
        log(f"Speed: {generation_time:.1f}s for 8-step turbo generation")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)