#!/usr/bin/env python3
"""
Generate the detailed Ukrainian portrait using FP8 Kontext workflow
"""

import json
import time
import requests
import sys
from pathlib import Path

COMFYUI_URL = "http://localhost:8188"
WORKFLOW_PATH = Path("workflows/flux_kontext_fp8_turbo.json")
PROMPT_FILE = Path("ukrainian_portrait_prompt.txt")
OUTPUT_PREFIX = "ukrainian_portrait_fp8"

# Load the detailed prompt
with open(PROMPT_FILE, 'r') as f:
    DETAILED_PROMPT = f.read().strip()

print(f"\n{'='*70}")
print("🎨 UKRAINIAN PORTRAIT GENERATOR - FP8 KONTEXT TURBO")
print(f"{'='*70}\n")

# Load workflow
print("📋 Loading workflow...")
with open(WORKFLOW_PATH, 'r') as f:
    workflow = json.load(f)

# Customize workflow
print(f"✏️ Injecting detailed prompt ({len(DETAILED_PROMPT)} chars)...")
workflow['5']['inputs']['text'] = DETAILED_PROMPT

# Optimize settings for quality
workflow['8']['inputs']['batch_size'] = 1
workflow['8']['inputs']['width'] = 1024
workflow['8']['inputs']['height'] = 1408  # Portrait ratio for full body

workflow['9']['inputs'].update({
    'seed': 202509301442,  # Timestamp-based seed
    'steps': 12,           # Higher quality (vs 8 in turbo default)
    'cfg': 1.0,            # Turbo LoRA setting
    'sampler_name': 'euler',
    'scheduler': 'simple'
})

workflow['11']['inputs']['filename_prefix'] = OUTPUT_PREFIX

print(f"⚙️ Settings: 1024x1408, 12 steps, seed=202509301442")

# Submit to ComfyUI
print(f"\n🚀 Submitting to ComfyUI...")
payload = {
    'prompt': workflow,
    'client_id': f'ukrainian_portrait_{int(time.time())}'
}

try:
    response = requests.post(
        f"{COMFYUI_URL}/prompt",
        json=payload,
        timeout=10
    )
    
    if response.status_code == 200:
        result = response.json()
        prompt_id = result['prompt_id']
        print(f"✅ Generation queued: {prompt_id}")
    else:
        print(f"❌ Error: HTTP {response.status_code}")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Failed to submit: {e}")
    sys.exit(1)

# Wait for completion
print(f"\n⏳ Generating portrait (this will take ~100-120 seconds)...\n")
start_time = time.time()
last_update = 0

while time.time() - start_time < 180:  # 3 minute timeout
    try:
        response = requests.get(
            f"{COMFYUI_URL}/history/{prompt_id}",
            timeout=5
        )
        
        if response.status_code == 200:
            history = response.json()
            
            if prompt_id in history:
                status = history[prompt_id].get('status', {})
                
                # Check if completed
                if status.get('completed', False) or history[prompt_id].get('outputs'):
                    elapsed = time.time() - start_time
                    
                    # Get generated files
                    outputs = history[prompt_id].get('outputs', {})
                    files = []
                    for node_id, output in outputs.items():
                        if 'images' in output:
                            files.extend([img['filename'] for img in output['images']])
                    
                    print(f"\n{'='*70}")
                    print(f"🎉 PORTRAIT GENERATED SUCCESSFULLY!")
                    print(f"{'='*70}")
                    print(f"⏱️ Generation Time: {elapsed:.1f}s")
                    print(f"📸 Output Files:")
                    for file in files:
                        print(f"   - {file}")
                    print(f"\n📁 Location: ComfyUI/output/")
                    print(f"🌐 View in browser: http://localhost:8188")
                    print(f"{'='*70}\n")
                    sys.exit(0)
                
                # Check for errors
                messages = status.get('messages', [])
                for msg in messages:
                    if msg[0] == 'execution_error':
                        print(f"\n❌ Generation error: {msg[1]}")
                        sys.exit(1)
        
        # Progress updates every 20 seconds
        elapsed = time.time() - start_time
        if int(elapsed) % 20 == 0 and elapsed != last_update:
            progress = min(90, (elapsed / 120) * 100)
            print(f"   ⚡ Progress: {progress:.0f}% ({elapsed:.0f}s elapsed)")
            last_update = elapsed
        
        time.sleep(2)
        
    except requests.RequestException:
        time.sleep(2)

print(f"\n⏰ Timeout after 3 minutes")
sys.exit(1)