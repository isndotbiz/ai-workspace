#!/usr/bin/env python3
"""
Flux Kontext Generator - Advanced CLI with Full Parameter Control
Supports: images count, steps, CFG, guidance, resolution, and complex prompts
"""

import json
import requests
import time
import random
import argparse
from pathlib import Path
from typing import Dict, Optional

class FluxKontextGenerator:
    def __init__(self):
        self.comfyui_url = "http://localhost:8188"
        self.ollama_url = "http://localhost:11434"
        self.workspace_root = Path("/home/jdm/ai-workspace")
        self.workflow_path = self.workspace_root / "workflows" / "flux_kontext.json"
    
    def expand_prompt_with_ollama(self, user_prompt: str, style: str = "luxury") -> str:
        """Expand prompt using Ollama/Mistral for better results"""
        
        style_prompts = {
            "luxury": "Transform into a luxury portrait with elegant, sophisticated styling and premium atmosphere",
            "professional": "Transform into a professional business portrait with corporate styling and modern atmosphere", 
            "artistic": "Transform into an artistic portrait with creative styling and unique atmosphere",
            "cinematic": "Transform into a cinematic portrait with dramatic lighting and film-like atmosphere"
        }
        
        system_prompt = f"""You are a professional portrait photographer and prompt expert for Flux.1-dev. {style_prompts.get(style, style_prompts['luxury'])}.

Rules:
- Focus ONLY on photorealistic human subjects
- Include specific details about the person (age, appearance, expression)
- Add professional photography details (lighting, composition, camera settings)
- Keep under 200 words total
- No artistic, painted, or illustrated styles
- Ensure the subject is clearly human

Return only the enhanced photographic prompt, nothing else."""

        try:
            payload = {
                "model": "mistral",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "num_ctx": 2048
                }
            }
            
            response = requests.post(f"{self.ollama_url}/api/chat", json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            enhanced = result['message']['content'].strip()
            
            # Clean up quotes if present
            if enhanced.startswith('"') and enhanced.endswith('"'):
                enhanced = enhanced[1:-1]
            
            return enhanced
            
        except Exception as e:
            print(f"⚠️ Prompt expansion failed: {e}")
            return user_prompt
    
    def create_workflow(self, prompt: str, num_images: int, steps: int, cfg: float, 
                       guidance: float, width: int, height: int, seed: Optional[int] = None) -> Dict:
        """Create customized workflow with all parameters"""
        
        try:
            with open(self.workflow_path, 'r') as f:
                workflow = json.load(f)
        except FileNotFoundError:
            print(f"❌ Workflow template not found: {self.workflow_path}")
            return {}
        
        # Set prompt
        workflow["5"]["inputs"]["text"] = prompt
        
        # Set generation parameters
        workflow["8"]["inputs"]["batch_size"] = num_images
        workflow["8"]["inputs"]["width"] = width
        workflow["8"]["inputs"]["height"] = height
        
        workflow["9"]["inputs"]["steps"] = steps
        workflow["9"]["inputs"]["cfg"] = cfg
        workflow["9"]["inputs"]["seed"] = seed if seed else random.randint(1000000, 9999999)
        
        # Set Flux guidance
        workflow["7"]["inputs"]["guidance"] = guidance
        
        return workflow
    
    def generate_images(self, prompt: str, num_images: int = 2, steps: int = 25, 
                       cfg: float = 1.0, guidance: float = 7.5, width: int = 1024, 
                       height: int = 1024, style: str = "luxury", seed: Optional[int] = None,
                       expand_prompt: bool = True) -> bool:
        """Generate images with full parameter control"""
        
        print(f"🎨 Flux Kontext Generator")
        print(f"📝 Prompt: {prompt}")
        print(f"🖼️  Images: {num_images}")
        print(f"⚡ Steps: {steps}")
        print(f"🎛️  CFG: {cfg}")
        print(f"🎯 Guidance: {guidance}")
        print(f"📐 Size: {width}x{height}")
        print(f"🎭 Style: {style}")
        print("-" * 50)
        
        # Expand prompt if requested
        if expand_prompt:
            print("🧠 Expanding prompt with Mistral...")
            enhanced_prompt = self.expand_prompt_with_ollama(prompt, style)
            print(f"✨ Enhanced: {enhanced_prompt[:100]}...")
        else:
            enhanced_prompt = prompt
        
        # Create workflow
        workflow = self.create_workflow(
            enhanced_prompt, num_images, steps, cfg, guidance, width, height, seed
        )
        
        if not workflow:
            return False
        
        # Submit generation
        start_time = time.time()
        prompt_id = self.submit_generation(workflow)
        
        if not prompt_id:
            return False
        
        # Wait for completion
        success = self.wait_for_completion(prompt_id, num_images, steps)
        
        generation_time = time.time() - start_time
        print(f"⏱️ Total time: {generation_time:.1f}s")
        print(f"⚡ Per image: {generation_time/num_images:.1f}s")
        
        return success
    
    def submit_generation(self, workflow: Dict) -> Optional[str]:
        """Submit workflow to ComfyUI"""
        try:
            payload = {"prompt": workflow}
            response = requests.post(f"{self.comfyui_url}/prompt", json=payload, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            prompt_id = result.get('prompt_id')
            
            if prompt_id:
                print(f"✅ Submitted: {prompt_id}")
                return prompt_id
            else:
                print("❌ No prompt_id in response")
                return None
                
        except Exception as e:
            print(f"❌ Submission failed: {e}")
            return None
    
    def wait_for_completion(self, prompt_id: str, num_images: int, steps: int) -> bool:
        """Wait for generation with smart timeout"""
        
        # Calculate timeout based on parameters
        estimated_time = (steps * num_images * 4) + 60  # 4s per step per image + 60s buffer
        timeout = max(estimated_time, 180)  # Minimum 3 minutes
        
        start_time = time.time()
        last_progress_time = start_time
        
        while time.time() - start_time < timeout:
            try:
                # Check history
                response = requests.get(f"{self.comfyui_url}/history", timeout=5)
                if response.status_code == 200:
                    history = response.json()
                    
                    if prompt_id in history:
                        prompt_data = history[prompt_id]
                        if 'outputs' in prompt_data:
                            elapsed = time.time() - start_time
                            print(f"🎉 Completed in {elapsed:.1f}s")
                            
                            # Check for output files
                            output_dir = self.workspace_root / "ComfyUI" / "output"
                            recent_images = list(output_dir.glob("flux_kontext_*.png"))
                            
                            if recent_images:
                                # Get most recent images
                                recent_images.sort(key=lambda p: p.stat().st_mtime, reverse=True)
                                
                                print(f"📸 Generated {len(recent_images[:num_images])} images:")
                                for i, img in enumerate(recent_images[:num_images]):
                                    size_mb = img.stat().st_size / (1024 * 1024)
                                    print(f"   {i+1}. {img.name} ({size_mb:.1f}MB)")
                                
                                return True
                
                # Progress update every 20 seconds
                elapsed = time.time() - start_time
                if elapsed - (last_progress_time - start_time) >= 20:
                    progress = min(95, (elapsed / estimated_time) * 100)
                    print(f"⏳ Generating... {progress:.0f}% ({elapsed:.0f}s)")
                    last_progress_time = time.time()
                
                time.sleep(3)
                
            except Exception as e:
                print(f"⚠️ Check failed: {e}")
                time.sleep(5)
        
        print(f"⏰ Timed out after {timeout}s")
        return False

def main():
    """Command-line interface with full parameter support"""
    parser = argparse.ArgumentParser(
        description="Flux Kontext Generator - Advanced CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python flux_kontext_generator.py "luxury tech CEO" 
  python flux_kontext_generator.py "business woman" --images 4 --steps 30 --cfg 1.2
  python flux_kontext_generator.py "professional portrait" --guidance 8.0 --style cinematic
  python flux_kontext_generator.py "entrepreneur" --width 768 --height 1024 --seed 12345
        """
    )
    
    parser.add_argument('prompt', help='Portrait concept or description')
    parser.add_argument('--images', '-n', type=int, default=2, help='Number of images to generate (default: 2)')
    parser.add_argument('--steps', '-s', type=int, default=25, help='Generation steps (default: 25)')
    parser.add_argument('--cfg', '-c', type=float, default=1.0, help='CFG scale (default: 1.0)')
    parser.add_argument('--guidance', '-g', type=float, default=7.5, help='Flux guidance (default: 7.5)')
    parser.add_argument('--width', '-w', type=int, default=1024, help='Image width (default: 1024)')
    parser.add_argument('--height', '-h', type=int, default=1024, help='Image height (default: 1024)')
    parser.add_argument('--style', choices=['luxury', 'professional', 'artistic', 'cinematic'], 
                       default='luxury', help='Style for prompt expansion (default: luxury)')
    parser.add_argument('--seed', type=int, help='Random seed (optional)')
    parser.add_argument('--no-expand', action='store_true', help='Skip prompt expansion')
    
    args = parser.parse_args()
    
    generator = FluxKontextGenerator()
    
    # Validate parameters
    if args.images < 1 or args.images > 8:
        print("❌ Number of images must be between 1 and 8")
        return 1
    
    if args.steps < 5 or args.steps > 50:
        print("❌ Steps must be between 5 and 50")
        return 1
    
    if args.cfg < 0.5 or args.cfg > 10.0:
        print("❌ CFG must be between 0.5 and 10.0")
        return 1
    
    # Generate images
    success = generator.generate_images(
        prompt=args.prompt,
        num_images=args.images,
        steps=args.steps,
        cfg=args.cfg,
        guidance=args.guidance,
        width=args.width,
        height=args.height,
        style=args.style,
        seed=args.seed,
        expand_prompt=not args.no_expand
    )
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())