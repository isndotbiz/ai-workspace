#!/usr/bin/env python3
"""
Fast Portrait Generator using Flux GGUF
=======================================
Rapid generation of luxury portraits using optimized GGUF workflow
Expected generation time: 60-90 seconds per image
"""

import json
import time
import requests
from pathlib import Path

COMFYUI_URL = "http://localhost:8188"
WORKFLOW_PATH = Path("workflows/flux_fast_gguf_portrait.json")

# Three luxury portrait prompts optimized for fast generation
PROMPTS = [
    {
        "name": "apex_executive_fast",
        "prompt": "A highly detailed, photorealistic portrait of a confident, attractive woman in her early 30s, embodying the 'apex executive' and 'visionary CEO'. She stands commandingly in a sprawling, ultra-modern penthouse office suite, overlooking a bustling metropolis at dusk. Her expression is astute, determined, and subtly powerful, conveying deep strategic thought and unwavering ambition. Lighting is dynamic and cinematic, featuring dramatic contrasts between the warm interior lights and the cool blue hues of the city skyline. Impeccably tailored, sleek monochrome power suit, minimalist but striking designer watch, sharp asymmetrical bob haircut, bold yet refined makeup. Assertive, intellectual, high-stakes elegance, inspiring leadership. Hyperrealistic, ultra-detailed skin texture, cinematic color grading, professional editorial photography aesthetic, crisp depth of field, 8k, masterpiece, award-winning portraiture.",
        "seed": 2501
    },
    {
        "name": "enigmatic_patroness_fast", 
        "prompt": "A highly detailed, photorealistic portrait of a confident, attractive woman in her late 30s, styled as an 'enigmatic art patroness' and 'cultural influencer'. She is seated gracefully within a lavish, dimly lit private art gallery, surrounded by avant-garde sculptures and a single spotlight illuminating a key piece. Her gaze is thoughtful, deep, and subtly alluring, suggesting profound insight and a sophisticated appreciation for beauty. Lighting is theatrical and chiaroscuro, with strong contrasts and dramatic shadows that highlight her features and the artwork, creating an intimate, exclusive atmosphere. Flowing, dark silk evening gown with subtle embroidery, vintage emerald jewelry, elegant upswept hair, smoky eyes with a deep red lip. Mysterious, refined, artistic opulence, quiet authority. Hyperrealistic, ultra-detailed skin texture, cinematic color grading, high-fashion art photography aesthetic, shallow depth of field, 8k, masterpiece, gallery-quality photography.",
        "seed": 3701
    },
    {
        "name": "global_adventurer_fast",
        "prompt": "A highly detailed, photorealistic portrait of a confident, attractive woman in her early 30s, embodying a 'global adventurer' and 'luxury travel icon'. She stands on the observation deck of a private yacht, anchored in a pristine, turquoise cove, with a dramatic cliff face and lush tropical foliage in the background. Her expression is adventurous, free-spirited, and radiating joy, with a hint of sun-kissed allure. Lighting is vibrant and natural, showcasing the brilliant blues of the ocean and sky, with a sun-drenched, radiant feel. Chic, resort-wear designer jumpsuit in linen or silk, oversized sunglasses, delicate gold chain and shell-motif earrings, windswept long hair, natural glowing makeup. Liberated, exotic, opulent leisure, aspirational wanderlust. Hyperrealistic, ultra-detailed skin texture, vibrant cinematic color grading, high-end travel photography aesthetic, wide-angle depth of field, 8k, masterpiece, National Geographic quality.",
        "seed": 4321
    }
]

def check_server():
    """Check if ComfyUI server is running"""
    try:
        response = requests.get(f"{COMFYUI_URL}/system_stats", timeout=5)
        return response.status_code == 200
    except:
        return False

def load_workflow():
    """Load the base workflow template"""
    with open(WORKFLOW_PATH, 'r') as f:
        return json.load(f)

def submit_workflow(workflow_data, prompt_name):
    """Submit workflow to ComfyUI and return prompt ID"""
    payload = {
        'prompt': workflow_data,
        'client_id': f'fast_gen_{int(time.time())}'
    }
    
    try:
        response = requests.post(f"{COMFYUI_URL}/prompt", json=payload, timeout=10)
        if response.status_code == 200:
            result = response.json()
            prompt_id = result['prompt_id']
            print(f"✅ Submitted {prompt_name}: {prompt_id}")
            return prompt_id
        else:
            print(f"❌ Failed to submit {prompt_name}: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error submitting {prompt_name}: {e}")
        return None

def wait_for_completion(prompt_id, prompt_name, timeout=120):
    """Wait for workflow completion with progress updates"""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{COMFYUI_URL}/history/{prompt_id}", timeout=10)
            if response.status_code == 200:
                history = response.json()
                if prompt_id in history and history[prompt_id].get('outputs'):
                    elapsed = time.time() - start_time
                    print(f"✅ {prompt_name} completed in {elapsed:.1f}s")
                    
                    # Show generated files
                    outputs = history[prompt_id]['outputs']
                    for node_id, output in outputs.items():
                        if 'images' in output:
                            for img in output['images']:
                                print(f"   📸 Generated: {img['filename']}")
                    return True
            
            # Show progress every 15 seconds
            elapsed = time.time() - start_time
            if elapsed > 0 and int(elapsed) % 15 == 0:
                print(f"   ⏳ {prompt_name} still generating... ({elapsed:.0f}s)")
            
            time.sleep(2)
            
        except Exception as e:
            print(f"   ⚠️ Error checking progress: {e}")
            time.sleep(5)
    
    print(f"⏰ {prompt_name} timed out after {timeout}s")
    return False

def generate_all_portraits():
    """Generate all three portrait variations"""
    print("🎨 Fast Flux GGUF Portrait Generator")
    print("=" * 50)
    
    # Check server
    if not check_server():
        print("❌ ComfyUI server not running. Start it first!")
        return False
    
    print("✅ ComfyUI server ready")
    
    # Load workflow template
    try:
        workflow_template = load_workflow()
        print("✅ Workflow template loaded")
    except Exception as e:
        print(f"❌ Failed to load workflow: {e}")
        return False
    
    successful_generations = 0
    total_start_time = time.time()
    
    # Generate each portrait
    for i, prompt_data in enumerate(PROMPTS, 1):
        print(f"\n🎨 Generating {i}/3: {prompt_data['name']}")
        
        # Customize workflow for this prompt
        workflow = workflow_template.copy()
        workflow['5']['inputs']['text'] = prompt_data['prompt']
        workflow['8']['inputs']['seed'] = prompt_data['seed']
        workflow['10']['inputs']['filename_prefix'] = prompt_data['name']
        
        # Submit and wait
        prompt_id = submit_workflow(workflow, prompt_data['name'])
        if prompt_id:
            if wait_for_completion(prompt_id, prompt_data['name']):
                successful_generations += 1
                print(f"✅ {prompt_data['name']} SUCCESS")
            else:
                print(f"❌ {prompt_data['name']} FAILED")
        
        # Small pause between generations
        if i < len(PROMPTS):
            print("   ⏸️ Brief pause before next generation...")
            time.sleep(3)
    
    # Summary
    total_time = time.time() - total_start_time
    print(f"\n🏁 Generation Complete!")
    print(f"   Success Rate: {successful_generations}/{len(PROMPTS)}")
    print(f"   Total Time: {total_time:.1f}s")
    print(f"   Average per Image: {total_time/len(PROMPTS):.1f}s")
    
    if successful_generations > 0:
        print(f"\n📸 Check ComfyUI/output/ for generated images")
        return True
    else:
        print(f"\n❌ No successful generations")
        return False

if __name__ == "__main__":
    generate_all_portraits()