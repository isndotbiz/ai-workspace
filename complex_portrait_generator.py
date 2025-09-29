#!/usr/bin/env python3
"""
Complex Portrait Generator - Final Optimized Version
Handles complex prompts with speed optimization under 2 minutes
"""

import json
import requests
import time
from pathlib import Path
from advanced_prompt_parser import AdvancedPromptParser

class ComplexPortraitGenerator:
    def __init__(self):
        self.comfyui_url = "http://localhost:8188"
        self.parser = AdvancedPromptParser()
        self.workspace_root = Path("/home/jdm/ai-workspace")
    
    def generate_complex_portrait(self, complex_prompt: str, target_time: int = 120) -> bool:
        """Generate a portrait from a complex prompt under target time"""
        
        print(f"🎨 Complex Portrait Generator")
        print(f"📝 Prompt: {complex_prompt[:100]}...")
        print(f"⏰ Target: {target_time}s")
        print("-" * 50)
        
        # Parse the complex prompt
        parsed = self.parser.parse_complex_prompt(complex_prompt)
        
        # Create optimized workflow for speed
        workflow = self.create_speed_optimized_workflow(parsed, target_time)
        
        if not workflow:
            print("❌ Failed to create workflow")
            return False
        
        # Submit to ComfyUI
        start_time = time.time()
        prompt_id = self.submit_generation(workflow)
        
        if not prompt_id:
            print("❌ Failed to submit generation")
            return False
        
        # Wait for completion with timeout
        success = self.wait_for_completion(prompt_id, target_time + 30)
        
        generation_time = time.time() - start_time
        print(f"⏱️  Total time: {generation_time:.1f}s")
        
        if success and generation_time <= target_time + 10:  # 10s tolerance
            print(f"🎉 SUCCESS: Generated under {target_time}s target!")
        elif success:
            print(f"✅ Generated successfully (slightly over target)")
        else:
            print(f"❌ Generation failed or timed out")
        
        return success
    
    def create_speed_optimized_workflow(self, parsed_prompt, target_time: int) -> dict:
        """Create workflow optimized for target time"""
        
        # Speed settings based on target time
        if target_time <= 90:
            steps = 8
            cfg = 2.5
            resolution = 768
        elif target_time <= 120:
            steps = 12
            cfg = 3.0
            resolution = 1024
        else:
            steps = 16
            cfg = 3.5
            resolution = 1024
        
        # Simplified workflow template
        workflow = {
            "1": {"inputs": {"unet_name": "flux1-dev-Q3_K_S.gguf"}, "class_type": "UnetLoaderGGUF"},
            "2": {"inputs": {"clip_name1": "clip_l.safetensors", "clip_name2": "t5-v1_1-xxl-encoder-Q3_K_S.gguf", "type": "flux"}, "class_type": "DualCLIPLoaderGGUF"},
            "3": {"inputs": {"vae_name": "ae.safetensors"}, "class_type": "VAELoader"},
            "4": {"inputs": {"lora_name": "flux-realism-xlabs.safetensors", "strength_model": 0.6, "strength_clip": 0.6, "model": ["1", 0], "clip": ["2", 0]}, "class_type": "LoraLoader"},
            "5": {"inputs": {"text": f"{parsed_prompt.main_subject}, {parsed_prompt.environment}, {parsed_prompt.lighting_style}, {parsed_prompt.technical_quality}", "clip": ["4", 1]}, "class_type": "CLIPTextEncode"},
            "6": {"inputs": {"text": "blurry, low quality, bad anatomy, distorted, cartoon, anime, illustration", "clip": ["4", 1]}, "class_type": "CLIPTextEncode"},
            "7": {"inputs": {"width": resolution, "height": resolution, "batch_size": 1}, "class_type": "EmptyLatentImage"},
            "8": {"inputs": {"seed": int(time.time()), "steps": steps, "cfg": cfg, "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0, "model": ["4", 0], "positive": ["5", 0], "negative": ["6", 0], "latent_image": ["7", 0]}, "class_type": "KSampler"},
            "9": {"inputs": {"samples": ["8", 0], "vae": ["3", 0]}, "class_type": "VAEDecode"},
            "10": {"inputs": {"filename_prefix": "complex_portrait", "images": ["9", 0]}, "class_type": "SaveImage"}
        }
        
        print(f"⚙️  Settings: {steps} steps, CFG {cfg}, {resolution}x{resolution}")
        return workflow
    
    def submit_generation(self, workflow: dict) -> str:
        """Submit generation to ComfyUI"""
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
    
    def wait_for_completion(self, prompt_id: str, timeout: int) -> bool:
        """Wait for generation completion"""
        start_time = time.time()
        
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
                            recent_images = list(output_dir.glob("complex_portrait_*.png"))
                            
                            if recent_images:
                                latest = max(recent_images, key=lambda p: p.stat().st_mtime)
                                size_mb = latest.stat().st_size / (1024 * 1024)
                                print(f"📸 Generated: {latest.name} ({size_mb:.1f}MB)")
                                return True
                
                # Progress update every 20 seconds
                elapsed = time.time() - start_time
                if int(elapsed) % 20 == 0:
                    print(f"⏳ Generating... {elapsed:.0f}s")
                
                time.sleep(2)
                
            except Exception as e:
                print(f"⚠️ Check failed: {e}")
                time.sleep(5)
        
        print(f"⏰ Timed out after {timeout}s")
        return False

def main():
    """Main entry point"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python complex_portrait_generator.py \"complex prompt\" [target_time]")
        sys.exit(1)
    
    complex_prompt = sys.argv[1]
    target_time = int(sys.argv[2]) if len(sys.argv) > 2 else 120
    
    generator = ComplexPortraitGenerator()
    success = generator.generate_complex_portrait(complex_prompt, target_time)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()