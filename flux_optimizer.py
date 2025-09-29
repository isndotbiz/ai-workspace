#!/usr/bin/env python3
"""
Flux GGUF Optimizer - Ollama-powered intelligent settings optimization
Analyzes prompts and suggests optimal generation settings for speed/quality balance
"""

import json
import requests
import time
import random
from typing import Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class GenerationSettings:
    steps: int
    cfg: float
    width: int
    height: int
    sampler: str
    scheduler: str
    lora_strength: float
    expected_time: int  # seconds

class FluxOptimizer:
    def __init__(self, ollama_host: str = "http://localhost:11434"):
        self.ollama_host = ollama_host
        self.model_name = "mistral"  # Switch to Mistral for better analysis
        
        # Speed-optimized presets
        self.presets = {
            "ultra_fast": GenerationSettings(
                steps=6, cfg=1.5, width=768, height=1024, 
                sampler="euler", scheduler="simple", lora_strength=0.4, expected_time=75
            ),
            "fast": GenerationSettings(
                steps=8, cfg=1.8, width=768, height=1024,
                sampler="euler", scheduler="simple", lora_strength=0.5, expected_time=95
            ),
            "balanced": GenerationSettings(
                steps=10, cfg=2.0, width=1024, height=1024,
                sampler="euler", scheduler="simple", lora_strength=0.6, expected_time=120
            ),
            "quality": GenerationSettings(
                steps=12, cfg=2.2, width=1024, height=1024,
                sampler="dpmpp_2m", scheduler="karras", lora_strength=0.7, expected_time=150
            )
        }
    
    def analyze_prompt(self, user_prompt: str) -> Dict:
        """Use Ollama to analyze prompt complexity and suggest optimizations"""
        
        system_prompt = """You are an AI image generation expert. Analyze the user's prompt and respond with JSON only.

Consider:
- Complexity: How detailed is the description?
- Subject: Portrait, full body, scene, etc.
- Quality needs: Does this need ultra-high detail or can it be fast?
- Style: Photorealistic, artistic, etc.

Respond with JSON in this exact format:
{
  "complexity": "low|medium|high",
  "subject_type": "portrait|full_body|scene|object",
  "detail_level": "basic|detailed|ultra_detailed",
  "recommended_preset": "ultra_fast|fast|balanced|quality",
  "reasoning": "brief explanation",
  "estimated_time": 90
}"""

        try:
            payload = {
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Analyze this prompt: {user_prompt}"}
                ],
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "num_ctx": 1024
                }
            }
            
            response = requests.post(f"{self.ollama_host}/api/chat", json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            analysis_text = result['message']['content'].strip()
            
            # Extract JSON from response
            start_idx = analysis_text.find('{')
            end_idx = analysis_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = analysis_text[start_idx:end_idx]
                analysis = json.loads(json_str)
                return analysis
            else:
                # Fallback if JSON parsing fails
                return self._fallback_analysis(user_prompt)
                
        except Exception as e:
            print(f"⚠️  Ollama analysis failed: {e}")
            return self._fallback_analysis(user_prompt)
    
    def _fallback_analysis(self, prompt: str) -> Dict:
        """Simple fallback analysis based on prompt length and keywords"""
        words = len(prompt.split())
        
        if words < 10:
            preset = "ultra_fast"
        elif words < 20:
            preset = "fast" 
        elif words < 35:
            preset = "balanced"
        else:
            preset = "quality"
            
        return {
            "complexity": "medium",
            "subject_type": "portrait",
            "detail_level": "detailed",
            "recommended_preset": preset,
            "reasoning": f"Based on prompt length ({words} words)",
            "estimated_time": self.presets[preset].expected_time
        }
    
    def optimize_settings(self, user_prompt: str, target_time: int = 120) -> Tuple[GenerationSettings, Dict]:
        """Get optimized settings for the given prompt and time target"""
        
        print(f"🔍 Analyzing prompt with Ollama...")
        analysis = self.analyze_prompt(user_prompt)
        
        # Get recommended preset
        preset_name = analysis.get("recommended_preset", "balanced")
        
        # Adjust based on target time
        if target_time < 90 and preset_name not in ["ultra_fast", "fast"]:
            preset_name = "ultra_fast"
        elif target_time < 120 and preset_name == "quality":
            preset_name = "balanced"
        
        settings = self.presets[preset_name]
        
        print(f"🎯 Recommended preset: {preset_name}")
        print(f"📊 Analysis: {analysis['reasoning']}")
        print(f"⏱️  Expected time: ~{settings.expected_time}s")
        
        return settings, analysis
    
    def enhance_prompt(self, user_prompt: str) -> str:
        """Use Ollama to enhance the prompt for better results"""
        
        system_prompt = """You are a photorealistic portrait prompt expert. Enhance the user's prompt for Flux.1-dev generation.

Rules:
- Keep the core concept intact
- Add professional photography details
- Include lighting and composition
- Keep it concise (under 200 words)
- Focus on photorealistic quality
- No artistic styles or painting references

Return only the enhanced prompt, no explanations."""

        try:
            payload = {
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "num_ctx": 1024
                }
            }
            
            response = requests.post(f"{self.ollama_host}/api/chat", json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            enhanced = result['message']['content'].strip()
            
            # Remove quotes if present
            if enhanced.startswith('"') and enhanced.endswith('"'):
                enhanced = enhanced[1:-1]
                
            return enhanced
            
        except Exception as e:
            print(f"⚠️  Prompt enhancement failed: {e}")
            return user_prompt
    
    def create_optimized_workflow(self, user_prompt: str, target_time: int = 120, 
                                 workflow_template: str = "flux_ultra_fast_gguf.json") -> Dict:
        """Create an optimized workflow JSON with intelligent settings"""
        
        # Get optimal settings
        settings, analysis = self.optimize_settings(user_prompt, target_time)
        
        # Enhance the prompt
        enhanced_prompt = self.enhance_prompt(user_prompt)
        
        # Load workflow template
        template_path = f"/home/jdm/ai-workspace/workflows/{workflow_template}"
        try:
            with open(template_path, 'r') as f:
                workflow = json.load(f)
        except FileNotFoundError:
            print(f"⚠️  Template not found: {template_path}")
            return {}
        
        # Apply optimizations
        workflow["5"]["inputs"]["text"] = enhanced_prompt  # Positive prompt
        workflow["7"]["inputs"]["width"] = settings.width
        workflow["7"]["inputs"]["height"] = settings.height
        workflow["8"]["inputs"]["steps"] = settings.steps
        workflow["8"]["inputs"]["cfg"] = settings.cfg
        workflow["8"]["inputs"]["sampler_name"] = settings.sampler
        workflow["8"]["inputs"]["scheduler"] = settings.scheduler
        workflow["8"]["inputs"]["seed"] = random.randint(1000, 999999)
        
        # Adjust LoRA strength if present
        if "4" in workflow and "strength_model" in workflow["4"]["inputs"]:
            workflow["4"]["inputs"]["strength_model"] = settings.lora_strength
            workflow["4"]["inputs"]["strength_clip"] = settings.lora_strength
        
        # Update filename with preset info
        workflow["10"]["inputs"]["filename_prefix"] = f"flux_optimized_{analysis['recommended_preset']}"
        
        print(f"✅ Workflow optimized!")
        print(f"📝 Enhanced prompt: {enhanced_prompt}")
        print(f"⚙️  Settings: {settings.steps} steps, CFG {settings.cfg}, {settings.width}x{settings.height}")
        
        return workflow

def main():
    """Command-line interface for the optimizer"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python flux_optimizer.py \"your prompt here\" [target_time_seconds]")
        sys.exit(1)
    
    user_prompt = sys.argv[1]
    target_time = int(sys.argv[2]) if len(sys.argv) > 2 else 120
    
    optimizer = FluxOptimizer()
    
    print(f"🎨 Flux GGUF Optimizer")
    print(f"📝 Input prompt: {user_prompt}")
    print(f"⏰ Target time: {target_time}s")
    print("-" * 50)
    
    # Generate optimized workflow
    workflow = optimizer.create_optimized_workflow(user_prompt, target_time)
    
    if workflow:
        # Save optimized workflow
        output_path = "/home/jdm/ai-workspace/workflows/optimized_workflow.json"
        with open(output_path, 'w') as f:
            json.dump(workflow, f, indent=2)
        
        print(f"💾 Optimized workflow saved to: {output_path}")
        print("🚀 Ready for generation!")

if __name__ == "__main__":
    main()