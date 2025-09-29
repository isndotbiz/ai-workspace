#!/usr/bin/env python3
"""
Advanced Super Prompt Generator for FLUX.1-dev
Generates cinematic, detailed prompts for stunning portrait generation
"""

import subprocess
import random
import json
from pathlib import Path
from typing import List, Dict, Any
import time

class SuperPromptGenerator:
    def __init__(self):
        self.workspace_root = Path("/home/jdm/ai-workspace")
        self.output_dir = self.workspace_root / "generated_prompts"
        self.output_dir.mkdir(exist_ok=True)
        
        # Persona archetypes for rich character generation
        self.personas = {
            "Ukrainian Wealth Muse": {
                "appearance": "late 20s Ukrainian woman with honey-blonde balayage hair, emerald eyes, porcelain skin",
                "style": "elegant silk dress with golden embroidery, diamond jewelry, luxury accessories",
                "setting": "opulent mansion interior with marble columns and crystal chandeliers",
                "mood": "confident, sophisticated, mysteriously alluring"
            },
            "Cyberpunk Street Artist": {
                "appearance": "early 20s mixed-race woman with neon-colored hair streaks, cyber-implants, intense gaze",
                "style": "holographic jacket, LED accessories, augmented reality visor",
                "setting": "neon-lit urban alley with graffiti walls and floating holograms",
                "mood": "rebellious, creative, technologically enhanced"
            },
            "Renaissance Portrait Master": {
                "appearance": "mid-20s Italian woman with flowing auburn curls, deep brown eyes, classical beauty",
                "style": "velvet gown with intricate brocade, pearl necklace, renaissance jewelry",
                "setting": "art studio with oil paintings, classical sculptures, warm candlelight",
                "mood": "artistic, contemplative, timeless elegance"
            },
            "Mystical Forest Guardian": {
                "appearance": "ageless elvish woman with silver-white hair, violet eyes, ethereal features",
                "style": "flowing robes made of living moss and flowers, natural crown of branches",
                "setting": "ancient enchanted forest with glowing mushrooms and magical light",
                "mood": "mystical, protective, connected to nature"
            },
            "Film Noir Detective": {
                "appearance": "late 20s woman with platinum blonde hair, sharp features, piercing blue eyes",
                "style": "tailored trench coat, fedora hat, vintage accessories from the 1940s",
                "setting": "rain-soaked city street at night with dramatic shadows and neon signs",
                "mood": "mysterious, intelligent, dangerously beautiful"
            },
            "Space Explorer Princess": {
                "appearance": "early 30s woman with silver hair, luminous skin, futuristic beauty enhancements",
                "style": "form-fitting space suit with holographic elements, royal insignia",
                "setting": "spaceship bridge with stellar views and advanced technology",
                "mood": "regal, adventurous, commanding presence"
            },
            "Vintage Fashion Icon": {
                "appearance": "mid-20s woman with classic 1950s styling, red lips, perfect winged eyeliner",
                "style": "haute couture dress, designer accessories, statement jewelry",
                "setting": "luxury fashion studio with vintage cameras and elegant furniture",
                "mood": "glamorous, confident, fashion-forward"
            },
            "Bohemian Artist Muse": {
                "appearance": "late 20s free-spirited woman with wild curly hair, expressive eyes, artistic features",
                "style": "flowing bohemian dress, layered jewelry, paint-stained fingers",
                "setting": "artist's loft with canvases, sculptures, and creative chaos",
                "mood": "creative, passionate, unconventional beauty"
            }
        }
        
        # Advanced camera and lighting configurations
        self.technical_specs = {
            "cameras": [
                "85mm f/1.4 lens for beautiful bokeh and sharp subject isolation",
                "135mm f/2 for compressed perspective and creamy background blur",
                "50mm f/1.2 for natural field of view with dramatic depth of field",
                "24-70mm f/2.8 for versatile framing with professional sharpness"
            ],
            "lighting": [
                "three-point lighting setup with key light, fill light, and rim light",
                "Rembrandt lighting with dramatic triangle of light on the face",
                "butterfly lighting for glamorous, fashion-forward illumination",
                "window light with large softbox creating natural, flattering shadows",
                "golden hour backlighting with warm rim light and lens flares",
                "studio strobe lighting with octabox modifier for even illumination"
            ],
            "composition": [
                "rule of thirds with subject's eyes on the upper third line",
                "centered composition with symmetrical framing for powerful presence",
                "close-up portrait focusing on eyes and facial expression",
                "three-quarter view showing elegant neck line and shoulder angle",
                "environmental portrait showing subject in their natural context"
            ]
        }
    
    def generate_ollama_prompt(self, concept: str, model: str = "llama3.1:8b") -> str:
        """Generate an enhanced prompt using Ollama"""
        system_prompt = """You are a world-class AI art prompt engineer specializing in FLUX.1-dev image generation. 
        Transform the user's concept into a detailed, cinematic prompt that will produce stunning, photorealistic portraits.
        
        Include:
        - Specific physical details and styling
        - Professional lighting and camera settings
        - Environmental context and mood
        - Technical photography specifications
        - Artistic style and composition notes
        
        Keep response under 250 words but make it vivid and highly detailed."""
        
        try:
            result = subprocess.run([
                'ollama', 'run', model,
                f'{system_prompt}\n\nUser concept: {concept}\n\nEnhanced FLUX prompt:'
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return f"Error generating prompt: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return "Timeout: Ollama took too long to respond"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def craft_persona_prompt(self, persona_name: str) -> str:
        """Craft a detailed prompt based on a persona archetype"""
        if persona_name not in self.personas:
            return f"Persona '{persona_name}' not found"
        
        persona = self.personas[persona_name]
        camera = random.choice(self.technical_specs["cameras"])
        lighting = random.choice(self.technical_specs["lighting"])
        composition = random.choice(self.technical_specs["composition"])
        
        prompt = f"""A hyper-realistic portrait of a {persona['appearance']}. She is wearing {persona['style']}. 
        The setting is {persona['setting']}. Her expression conveys {persona['mood']}.
        
        Technical specifications: Shot with {camera}, using {lighting}, composed with {composition}.
        
        The image should have professional studio quality, sharp focus on the eyes, beautiful skin texture details,
        perfect anatomy, and cinematic lighting. Style: photorealistic, high fashion photography, editorial quality,
        award-winning portrait photography."""
        
        return prompt.replace('\n        ', ' ').strip()
    
    def generate_super_prompts_batch(self) -> List[Dict[str, Any]]:
        """Generate a comprehensive batch of super prompts"""
        prompts = []
        timestamp = int(time.time())
        
        print("🎨 Generating super prompts...")
        print("=" * 60)
        
        # Generate persona-based prompts
        for persona_name in self.personas.keys():
            print(f"🎭 Generating: {persona_name}")
            
            # Crafted prompt
            crafted_prompt = self.craft_persona_prompt(persona_name)
            
            # Ollama-enhanced prompt
            ollama_prompt = self.generate_ollama_prompt(f"{persona_name} portrait")
            
            prompt_data = {
                "id": f"{persona_name.lower().replace(' ', '_')}_{timestamp}",
                "persona": persona_name,
                "crafted_prompt": crafted_prompt,
                "ollama_enhanced": ollama_prompt,
                "technical_notes": {
                    "recommended_steps": random.randint(16, 24),
                    "cfg_scale": round(random.uniform(3.0, 4.5), 1),
                    "resolution": random.choice(["832x1152", "1024x1024", "1152x832"]),
                    "lora_strength": round(random.uniform(0.6, 0.8), 1)
                },
                "timestamp": timestamp
            }
            
            prompts.append(prompt_data)
            print(f"✅ Generated prompts for {persona_name}")
            
        return prompts
    
    def save_prompts(self, prompts: List[Dict[str, Any]]) -> str:
        """Save prompts to JSON file"""
        filename = f"super_prompts_{int(time.time())}.json"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(prompts, f, indent=2)
        
        return str(filepath)
    
    def create_workflow_variants(self, prompt_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create ComfyUI workflow variants for the prompt"""
        workflow_base = {
            "3": {
                "inputs": {
                    "seed": random.randint(1, 1000000),
                    "steps": prompt_data["technical_notes"]["recommended_steps"],
                    "cfg": prompt_data["technical_notes"]["cfg_scale"],
                    "sampler_name": "euler",
                    "scheduler": "simple",
                    "denoise": 1,
                    "model": ["11", 0],
                    "positive": ["6", 0],
                    "negative": ["7", 0],
                    "latent_image": ["5", 0]
                },
                "class_type": "KSampler"
            },
            "4": {
                "inputs": {"ckpt_name": "flux1-dev-Q3_K_S.gguf"},
                "class_type": "CheckpointLoaderSimple"
            },
            "5": {
                "inputs": {
                    "width": int(prompt_data["technical_notes"]["resolution"].split('x')[0]),
                    "height": int(prompt_data["technical_notes"]["resolution"].split('x')[1]),
                    "batch_size": 1
                },
                "class_type": "EmptyLatentImage"
            },
            "6": {
                "inputs": {"text": prompt_data["crafted_prompt"], "clip": ["4", 1]},
                "class_type": "CLIPTextEncode"
            },
            "7": {
                "inputs": {
                    "text": "blurry, low quality, distorted, bad anatomy, extra limbs, missing limbs, poorly drawn hands, poorly drawn face, mutation, deformed, ugly, bad proportions",
                    "clip": ["4", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "8": {
                "inputs": {"samples": ["3", 0], "vae": ["4", 2]},
                "class_type": "VAEDecode"
            },
            "9": {
                "inputs": {"filename_prefix": f"super_prompt_{prompt_data['id']}", "images": ["8", 0]},
                "class_type": "SaveImage"
            },
            "10": {
                "inputs": {
                    "lora_name": "flux-RealismLora.safetensors",
                    "strength_model": prompt_data["technical_notes"]["lora_strength"],
                    "strength_clip": prompt_data["technical_notes"]["lora_strength"],
                    "model": ["4", 0],
                    "clip": ["4", 1]
                },
                "class_type": "LoraLoader"
            },
            "11": {
                "inputs": {
                    "lora_name": "Hyper-FLUX.1-dev-8steps-lora.safetensors",
                    "strength_model": 0.6,
                    "strength_clip": 0.6,
                    "model": ["10", 0],
                    "clip": ["10", 1]
                },
                "class_type": "LoraLoader"
            }
        }
        
        return workflow_base
    
    def export_for_comfyui(self, prompts: List[Dict[str, Any]]) -> str:
        """Export prompts as ComfyUI workflows"""
        workflows_dir = self.output_dir / "workflows"
        workflows_dir.mkdir(exist_ok=True)
        
        for prompt_data in prompts:
            workflow = self.create_workflow_variants(prompt_data)
            workflow_file = workflows_dir / f"{prompt_data['id']}_workflow.json"
            
            with open(workflow_file, 'w') as f:
                json.dump(workflow, f, indent=2)
        
        return str(workflows_dir)
    
    def generate_and_save_all(self) -> Dict[str, str]:
        """Generate all prompts and save them"""
        prompts = self.generate_super_prompts_batch()
        
        # Save prompts
        prompts_file = self.save_prompts(prompts)
        
        # Export workflows
        workflows_dir = self.export_for_comfyui(prompts)
        
        # Create summary
        summary = {
            "prompts_generated": len(prompts),
            "prompts_file": prompts_file,
            "workflows_directory": workflows_dir,
            "personas": list(self.personas.keys())
        }
        
        return summary


def main():
    """Main execution function"""
    print("🚀 Super Prompt Generator for FLUX.1-dev")
    print("=" * 50)
    
    generator = SuperPromptGenerator()
    
    try:
        results = generator.generate_and_save_all()
        
        print("\n🎉 Super Prompt Generation Complete!")
        print("=" * 50)
        print(f"✅ Generated {results['prompts_generated']} professional prompts")
        print(f"📄 Prompts saved to: {results['prompts_file']}")
        print(f"🔧 Workflows saved to: {results['workflows_directory']}")
        print("\n🎭 Generated personas:")
        for persona in results['personas']:
            print(f"   • {persona}")
        
        print("\n💡 Next steps:")
        print("1. Import workflows into ComfyUI")
        print("2. Load your FLUX.1-dev model and LoRAs")
        print("3. Generate stunning portraits!")
        print("4. Fine-tune parameters based on results")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️  Generation interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Error during generation: {str(e)}")
        return 1


if __name__ == "__main__":
    exit(main())