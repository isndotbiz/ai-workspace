#!/usr/bin/env python3
"""
Advanced Prompt Parser for Complex Flux Prompts
Breaks down complex prompts into structured components for better generation
"""

import json
import requests
import re
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class ParsedPrompt:
    main_subject: str
    environment: str
    lighting_style: str
    technical_quality: str
    combined_prompt: str

class AdvancedPromptParser:
    def __init__(self, ollama_host: str = "http://localhost:11434"):
        self.ollama_host = ollama_host
        self.model_name = "mistral"
    
    def parse_complex_prompt(self, complex_prompt: str) -> ParsedPrompt:
        """Parse a complex prompt into structured components"""
        
        system_prompt = """You are a photorealistic portrait prompt expert. Break down the complex prompt into 4 focused components for optimal Flux.1-dev generation.

Rules:
- Keep each component under 77 tokens
- Focus on photorealistic human subjects
- Ensure the main subject is a person
- Be specific and detailed
- No artistic or painted styles

Return JSON in this exact format:
{
  "main_subject": "specific person description with age, appearance, expression",
  "environment": "background, setting, architectural elements",
  "lighting_style": "lighting type, mood, color temperature, shadows",
  "technical_quality": "camera settings, photography style, quality terms"
}"""

        try:
            payload = {
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Parse this complex prompt: {complex_prompt}"}
                ],
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "num_ctx": 2048
                }
            }
            
            response = requests.post(f"{self.ollama_host}/api/chat", json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            content = result['message']['content'].strip()
            
            # Extract JSON from response
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = content[start_idx:end_idx]
                parsed_data = json.loads(json_str)
                
                # Create combined prompt for fallback
                combined = f"{parsed_data['main_subject']}, {parsed_data['environment']}, {parsed_data['lighting_style']}, {parsed_data['technical_quality']}"
                
                return ParsedPrompt(
                    main_subject=parsed_data['main_subject'],
                    environment=parsed_data['environment'], 
                    lighting_style=parsed_data['lighting_style'],
                    technical_quality=parsed_data['technical_quality'],
                    combined_prompt=combined
                )
            else:
                return self._fallback_parse(complex_prompt)
                
        except Exception as e:
            print(f"⚠️ Advanced parsing failed: {e}")
            return self._fallback_parse(complex_prompt)
    
    def _fallback_parse(self, complex_prompt: str) -> ParsedPrompt:
        """Simple fallback parsing using regex patterns"""
        
        # Extract main subject (look for person descriptors)
        person_keywords = r"(woman|man|person|individual|executive|CEO|entrepreneur|visionary|professional)"
        person_match = re.search(rf"(\w+\s+){0,3}{person_keywords}.*?(?=[,.]|$)", complex_prompt, re.IGNORECASE)
        main_subject = person_match.group(0) if person_match else "professional portrait of an attractive person"
        
        # Extract environment/setting
        environment_keywords = r"(environment|setting|background|room|office|studio|architectural|building|modern|minimalist)"
        env_match = re.search(rf"[^.]*{environment_keywords}[^.]*", complex_prompt, re.IGNORECASE)
        environment = env_match.group(0) if env_match else "professional studio setting"
        
        # Extract lighting
        lighting_keywords = r"(lighting|light|illuminat|shadow|glow|bright|soft|warm|cool|dramatic)"
        light_match = re.search(rf"[^.]*{lighting_keywords}[^.]*", complex_prompt, re.IGNORECASE)
        lighting_style = light_match.group(0) if light_match else "professional studio lighting"
        
        # Extract technical quality
        quality_keywords = r"(hyperrealistic|photorealistic|8k|4k|detailed|quality|photography|camera|lens|masterpiece)"
        quality_match = re.search(rf"[^.]*{quality_keywords}[^.]*", complex_prompt, re.IGNORECASE)
        technical_quality = quality_match.group(0) if quality_match else "hyperrealistic, ultra-detailed, 8k masterpiece"
        
        return ParsedPrompt(
            main_subject=main_subject[:150],
            environment=environment[:150],
            lighting_style=lighting_style[:150], 
            technical_quality=technical_quality[:150],
            combined_prompt=complex_prompt[:500]  # Truncate if too long
        )
    
    def create_structured_workflow(self, complex_prompt: str, workflow_template: str = "flux_advanced_complex_prompt.json") -> Dict:
        """Create workflow with parsed complex prompt"""
        
        # Parse the complex prompt
        parsed = self.parse_complex_prompt(complex_prompt)
        
        print(f"🧠 Parsed Complex Prompt:")
        print(f"  👤 Subject: {parsed.main_subject}")
        print(f"  🌍 Environment: {parsed.environment}")
        print(f"  💡 Lighting: {parsed.lighting_style}")
        print(f"  📸 Quality: {parsed.technical_quality}")
        
        # Load workflow template
        template_path = f"/home/jdm/ai-workspace/workflows/{workflow_template}"
        try:
            with open(template_path, 'r') as f:
                workflow = json.load(f)
        except FileNotFoundError:
            print(f"⚠️ Template not found: {template_path}")
            return {}
        
        # Apply structured prompting
        workflow["5"]["inputs"]["text"] = parsed.main_subject
        workflow["6"]["inputs"]["text"] = parsed.environment
        workflow["7"]["inputs"]["text"] = parsed.lighting_style
        workflow["8"]["inputs"]["text"] = parsed.technical_quality
        
        # Set optimal settings for complex prompts
        workflow["14"]["inputs"]["seed"] = 42  # Fixed seed for testing
        workflow["14"]["inputs"]["steps"] = 20  # More steps for complex prompts
        workflow["14"]["inputs"]["cfg"] = 3.5  # Higher CFG for better adherence
        
        return workflow

def main():
    """CLI interface for testing"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python advanced_prompt_parser.py \"your complex prompt\"")
        sys.exit(1)
    
    complex_prompt = sys.argv[1]
    parser = AdvancedPromptParser()
    
    print("🎨 Advanced Complex Prompt Parser")
    print("=" * 40)
    print(f"📝 Input: {complex_prompt}")
    print("-" * 40)
    
    # Parse and create workflow
    workflow = parser.create_structured_workflow(complex_prompt)
    
    if workflow:
        # Save the workflow
        output_path = "/home/jdm/ai-workspace/workflows/parsed_complex_workflow.json"
        with open(output_path, 'w') as f:
            json.dump(workflow, f, indent=2)
        
        print(f"💾 Structured workflow saved to: {output_path}")
        print("🚀 Ready for complex prompt generation!")

if __name__ == "__main__":
    main()