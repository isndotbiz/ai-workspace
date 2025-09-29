#!/usr/bin/env python3
"""
Luxury AI Portrait Pipeline
===========================
Automated CLI workflow: Short Concept → GGUF Prompt Engineering → Flux GGUF Generation

Usage:
    python luxury_ai_pipeline.py "Ukrainian wealth muse"
    python luxury_ai_pipeline.py --batch "financial goddess" "luxury entrepreneur" "exotic motivator"
    python luxury_ai_pipeline.py --interactive
"""

import json
import time
import requests
import argparse
import subprocess
from pathlib import Path
from typing import List, Dict

# Configuration
COMFYUI_URL = "http://localhost:8188"
OLLAMA_URL = "http://localhost:11434"
WORKFLOW_PATH = Path("workflows/flux_fast_gguf_portrait.json")
OUTPUT_DIR = Path("ComfyUI/output")

class Colors:
    BLUE = '\033[0;34m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    NC = '\033[0m'

def print_status(message, status='info'):
    """Print colored status messages"""
    colors = {
        'info': Colors.BLUE,
        'success': Colors.GREEN,
        'warning': Colors.YELLOW,
        'error': Colors.RED,
        'highlight': Colors.CYAN
    }
    color = colors.get(status, Colors.NC)
    print(f"{color}{message}{Colors.NC}")

def check_services():
    """Check if required services are running"""
    services = {
        'ComfyUI': COMFYUI_URL + '/system_stats',
        'Ollama': OLLAMA_URL + '/api/tags'
    }
    
    for service, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print_status(f"✅ {service} is running", 'success')
            else:
                print_status(f"❌ {service} returned {response.status_code}", 'error')
                return False
        except requests.RequestException:
            print_status(f"❌ {service} not accessible at {url}", 'error')
            return False
    
    return True

def generate_prompts(concepts: List[str], variations_per_concept: int = 3) -> List[Dict]:
    """Generate detailed prompts from short concepts using Ollama"""
    print_status(f"🧠 Generating {variations_per_concept} prompt variations for each concept...", 'highlight')
    
    generated_prompts = []
    
    for concept in concepts:
        print_status(f"   Processing: '{concept}'", 'info')
        
        for i in range(variations_per_concept):
            try:
                # Add variation instructions to get different results
                variation_instruction = f"Create variation #{i+1} with a different setting/pose/mood for: {concept}"
                
                payload = {
                    "model": "prompter",
                    "prompt": variation_instruction,
                    "stream": False,
                    "options": {
                        "temperature": 0.8,  # Slightly higher for variation
                        "top_p": 0.9
                    }
                }
                
                response = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    prompt_text = result['response'].strip()
                    
                    # Clean up the prompt
                    if prompt_text.startswith('"') and prompt_text.endswith('"'):
                        prompt_text = prompt_text[1:-1]
                    
                    generated_prompts.append({
                        'concept': concept,
                        'variation': i + 1,
                        'prompt': prompt_text,
                        'filename_prefix': f"{concept.replace(' ', '_')}_v{i+1}",
                        'seed': hash(concept + str(i)) % 10000
                    })
                    
                    print_status(f"   ✅ Generated variation {i+1}", 'success')
                    
                else:
                    print_status(f"   ❌ Ollama error: {response.status_code}", 'error')
                    
            except Exception as e:
                print_status(f"   ❌ Error generating prompt {i+1}: {e}", 'error')
        
        time.sleep(1)  # Brief pause between concepts
    
    print_status(f"🎯 Generated {len(generated_prompts)} total prompts", 'success')
    return generated_prompts

def load_workflow_template():
    """Load the GGUF workflow template"""
    try:
        with open(WORKFLOW_PATH, 'r') as f:
            return json.load(f)
    except Exception as e:
        print_status(f"❌ Failed to load workflow template: {e}", 'error')
        return None

def submit_generation(prompt_data: Dict, workflow_template: Dict) -> str:
    """Submit a single image generation to ComfyUI"""
    # Customize workflow
    workflow = workflow_template.copy()
    workflow['5']['inputs']['text'] = prompt_data['prompt']
    workflow['8']['inputs']['seed'] = prompt_data['seed']
    workflow['10']['inputs']['filename_prefix'] = prompt_data['filename_prefix']
    
    # Submit to ComfyUI
    payload = {
        'prompt': workflow,
        'client_id': f"pipeline_{int(time.time())}"
    }
    
    try:
        response = requests.post(f"{COMFYUI_URL}/prompt", json=payload, timeout=10)
        if response.status_code == 200:
            result = response.json()
            return result['prompt_id']
        else:
            print_status(f"❌ ComfyUI submission error: {response.status_code}", 'error')
            return None
    except Exception as e:
        print_status(f"❌ Error submitting to ComfyUI: {e}", 'error')
        return None

def wait_for_generation(prompt_id: str, name: str, timeout: int = 180) -> bool:
    """Wait for a single generation to complete"""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{COMFYUI_URL}/history/{prompt_id}", timeout=10)
            if response.status_code == 200:
                history = response.json()
                if prompt_id in history and history[prompt_id].get('outputs'):
                    elapsed = time.time() - start_time
                    
                    # Get generated file names
                    outputs = history[prompt_id]['outputs']
                    files = []
                    for node_id, output in outputs.items():
                        if 'images' in output:
                            files.extend([img['filename'] for img in output['images']])
                    
                    print_status(f"   ✅ {name} completed in {elapsed:.1f}s → {files}", 'success')
                    return True
            
            # Brief status update every 20 seconds
            elapsed = time.time() - start_time
            if elapsed > 20 and int(elapsed) % 20 == 0:
                print_status(f"   ⏳ {name} still generating... ({elapsed:.0f}s / {timeout}s)", 'info')
            
            time.sleep(3)
            
        except Exception as e:
            print_status(f"   ⚠️ Error checking {name}: {e}", 'warning')
            time.sleep(5)
    
    print_status(f"   ⏰ {name} timed out", 'error')
    return False

def run_pipeline(concepts: List[str], variations: int = 3, batch_mode: bool = False):
    """Run the complete pipeline"""
    print_status("🚀 Luxury AI Portrait Pipeline", 'highlight')
    print_status("=" * 50, 'info')
    
    # Check services
    if not check_services():
        return False
    
    # Generate prompts
    prompt_data_list = generate_prompts(concepts, variations)
    if not prompt_data_list:
        print_status("❌ No prompts generated", 'error')
        return False
    
    # Load workflow
    workflow_template = load_workflow_template()
    if not workflow_template:
        return False
    
    print_status(f"\n🎨 Starting image generation for {len(prompt_data_list)} prompts...", 'highlight')
    
    # Generate images
    total_start = time.time()
    successful = 0
    
    if batch_mode:
        # Submit all at once, then wait
        prompt_ids = []
        for prompt_data in prompt_data_list:
            prompt_id = submit_generation(prompt_data, workflow_template)
            if prompt_id:
                prompt_ids.append((prompt_id, prompt_data['filename_prefix']))
                print_status(f"✅ Submitted: {prompt_data['filename_prefix']}", 'success')
        
        # Wait for all
        print_status(f"\n⏳ Waiting for {len(prompt_ids)} generations to complete...", 'info')
        for prompt_id, name in prompt_ids:
            if wait_for_generation(prompt_id, name):
                successful += 1
    else:
        # Sequential generation
        for i, prompt_data in enumerate(prompt_data_list, 1):
            name = prompt_data['filename_prefix']
            print_status(f"\n🎨 Generating {i}/{len(prompt_data_list)}: {name}", 'highlight')
            print_status(f"   Concept: {prompt_data['concept']}", 'info')
            
            prompt_id = submit_generation(prompt_data, workflow_template)
            if prompt_id and wait_for_generation(prompt_id, name):
                successful += 1
            
            # Brief pause between generations
            if i < len(prompt_data_list):
                time.sleep(2)
    
    # Summary
    total_time = time.time() - total_start
    print_status(f"\n🏁 Pipeline Complete!", 'highlight')
    print_status(f"   Success Rate: {successful}/{len(prompt_data_list)}", 'success' if successful > 0 else 'error')
    print_status(f"   Total Time: {total_time:.1f}s", 'info')
    print_status(f"   Average per Image: {total_time/len(prompt_data_list):.1f}s", 'info')
    
    if successful > 0:
        print_status(f"\n📸 Generated images saved to: {OUTPUT_DIR}/", 'success')
        return True
    
    return False

def interactive_mode():
    """Interactive CLI mode"""
    print_status("🎯 Interactive Mode", 'highlight')
    print_status("Enter short concepts, one per line. Type 'done' to start generation.", 'info')
    print_status("Examples: 'Ukrainian wealth muse', 'exotic motivator', 'luxury entrepreneur'", 'info')
    
    concepts = []
    while True:
        try:
            concept = input(f"{Colors.CYAN}Concept {len(concepts)+1}: {Colors.NC}").strip()
            if concept.lower() == 'done':
                break
            elif concept:
                concepts.append(concept)
                print_status(f"   Added: '{concept}'", 'success')
        except KeyboardInterrupt:
            print_status("\n👋 Goodbye!", 'info')
            return
    
    if concepts:
        variations = int(input(f"{Colors.CYAN}Variations per concept (1-5): {Colors.NC}") or "2")
        variations = max(1, min(5, variations))
        
        batch = input(f"{Colors.CYAN}Batch mode? (y/n): {Colors.NC}").lower().startswith('y')
        
        run_pipeline(concepts, variations, batch)
    else:
        print_status("No concepts provided.", 'warning')

def main():
    parser = argparse.ArgumentParser(description='Luxury AI Portrait Pipeline')
    parser.add_argument('concepts', nargs='*', help='Short concept descriptions')
    parser.add_argument('--variations', '-v', type=int, default=2, help='Variations per concept (1-5)')
    parser.add_argument('--batch', '-b', action='store_true', help='Batch mode (submit all, then wait)')
    parser.add_argument('--interactive', '-i', action='store_true', help='Interactive mode')
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_mode()
    elif args.concepts:
        variations = max(1, min(5, args.variations))
        run_pipeline(args.concepts, variations, args.batch)
    else:
        print_status("❌ No concepts provided. Use --help for usage information.", 'error')
        parser.print_help()

if __name__ == "__main__":
    main()