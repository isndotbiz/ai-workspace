#!/usr/bin/env python3
"""
FLUX Prompt Optimizer using Ollama

Takes user prompts and optimizes them for FLUX models using best practices:
- Detailed but concise descriptions
- Natural language flow
- Technical photography details
- Proper emphasis on quality and composition
- Removes redundancy and improves structure
"""

import json
import requests
import sys
from pathlib import Path

OLLAMA_URL = "http://localhost:11434"

FLUX_OPTIMIZATION_SYSTEM = """You are a FLUX model prompt optimization expert. Your job is to take user image prompts and optimize them for FLUX.1-dev/Kontext models.

FLUX Best Practices:
1. Use natural, flowing descriptions (not comma-separated tags)
2. Include specific details about subject, pose, expression, clothing, lighting
3. Add technical photography details (lens, lighting setup) at the end
4. Be concise but detailed - aim for 150-250 words
5. Avoid redundant phrases and repetition
6. Use vivid, specific adjectives
7. Structure: Subject → Details → Setting → Technical specs
8. Don't use negative prompts in the main prompt
9. Focus on what YOU WANT, not what you don't want

Example optimization:
User: "beautiful girl with long hair"
Optimized: "A graceful young woman with flowing chestnut hair cascading past her shoulders, standing in soft golden hour light. She wears an elegant cream silk dress, her gentle expression conveying quiet confidence. The setting is a minimalist studio with warm natural light streaming from a large window. Shot with 85mm f/1.4 lens, shallow depth of field, professional photography, photorealistic detail."

Transform the user's prompt following these principles. Make it vivid, specific, and perfectly structured for FLUX."""

def optimize_prompt(user_prompt: str, model: str = "mistral") -> str:
    """Optimize a prompt for FLUX using Ollama"""
    
    print(f"🧠 Optimizing prompt with {model}...\n")
    print(f"Original length: {len(user_prompt)} chars")
    
    payload = {
        "model": model,
        "prompt": f"{FLUX_OPTIMIZATION_SYSTEM}\n\nUser prompt to optimize:\n{user_prompt}\n\nOptimized FLUX prompt:",
        "stream": False,
        "options": {
            "temperature": 0.7,
            "top_p": 0.9,
            "num_predict": 500
        }
    }
    
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            optimized = result['response'].strip()
            
            # Clean up common formatting
            optimized = optimized.strip('"\'')
            if optimized.startswith("Optimized:"):
                optimized = optimized.replace("Optimized:", "").strip()
            
            print(f"\n✅ Optimized length: {len(optimized)} chars")
            print(f"\n{'='*70}")
            print("OPTIMIZED PROMPT:")
            print(f"{'='*70}")
            print(optimized)
            print(f"{'='*70}\n")
            
            return optimized
        else:
            print(f"❌ Ollama error: HTTP {response.status_code}")
            return user_prompt
            
    except requests.RequestException as e:
        print(f"❌ Optimization failed: {e}")
        return user_prompt

def main():
    """Main CLI interface"""
    if len(sys.argv) < 2:
        print("Usage: python optimize_flux_prompt.py <prompt_file_or_text>")
        print("\nExamples:")
        print("  python optimize_flux_prompt.py ukrainian_portrait_prompt.txt")
        print('  python optimize_flux_prompt.py "beautiful woman in elegant dress"')
        sys.exit(1)
    
    # Check if argument is a file or text
    arg = sys.argv[1]
    prompt_file = Path(arg)
    
    if prompt_file.exists() and prompt_file.is_file():
        print(f"📄 Loading prompt from: {prompt_file}")
        with open(prompt_file, 'r') as f:
            user_prompt = f.read().strip()
    else:
        user_prompt = arg
    
    # Optimize
    optimized = optimize_prompt(user_prompt)
    
    # Save optimized version
    if prompt_file.exists():
        output_file = prompt_file.parent / f"{prompt_file.stem}_optimized.txt"
        with open(output_file, 'w') as f:
            f.write(optimized)
        print(f"💾 Saved optimized prompt to: {output_file}")
    else:
        output_file = Path("optimized_prompt.txt")
        with open(output_file, 'w') as f:
            f.write(optimized)
        print(f"💾 Saved optimized prompt to: {output_file}")

if __name__ == "__main__":
    main()