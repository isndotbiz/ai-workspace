"""
ComfyUI Management System

Centralized ComfyUI operations with CUDA-only enforcement and FP8 optimization.
"""

import asyncio
import json
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple
import requests
from dataclasses import dataclass

from ..config.settings import get_config
from ..utils.exceptions import ComfyUIError, ComfyUIConnectionError, ComfyUITimeoutError, CUDAError
from ..utils.logging import get_logger, log_performance


@dataclass
class GenerationSettings:
    """Image generation settings"""
    prompt: str
    negative_prompt: str = ""
    steps: int = 28
    cfg_scale: float = 3.5
    seed: int = -1
    batch_size: int = 1
    width: int = 1024
    height: int = 1024
    sampler: str = "euler"
    scheduler: str = "normal"
    turbo_lora_strength: float = 0.6


@dataclass
class GenerationResult:
    """Generation result with metadata"""
    images: List[Path]
    settings: GenerationSettings
    execution_time: float
    workflow_id: str
    metadata: Dict[str, Any]


class ComfyUIManager:
    """
    Unified ComfyUI Management System
    
    Handles all ComfyUI operations including startup, model management,
    workflow execution, and CUDA validation.
    """
    
    def __init__(self):
        self.config = get_config()
        self.logger = get_logger(f"{__name__}.ComfyUIManager")
        self.process: Optional[subprocess.Popen] = None
        self.is_running = False
        
    def __enter__(self):
        self.start_server()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_server()
    
    @log_performance
    def validate_cuda(self) -> None:
        """Validate CUDA availability before operations"""
        if not self.config.cuda_only:
            return
            
        try:
            import torch
            if not torch.cuda.is_available():
                raise CUDAError(
                    "CUDA not available but required for FP8 operations",
                    {"cuda_only": True, "torch_version": torch.__version__}
                )
            
            self.logger.info(f"CUDA validated: {torch.cuda.get_device_name(0)}")
            
        except ImportError:
            raise CUDAError("PyTorch not available for CUDA validation")
    
    @log_performance
    def validate_models(self) -> Dict[str, bool]:
        """Validate all required FP8 models are present"""
        model_status = {}
        
        models_to_check = [
            ("fp8", "FP8 Kontext Model"),
            ("t5", "T5-XXL FP8 Encoder"),
            ("clip", "CLIP-L Encoder"),
            ("vae", "VAE Decoder"),
            ("turbo_lora", "Turbo LoRA")
        ]
        
        for model_key, description in models_to_check:
            try:
                model_path = self.config.get_model_path(model_key)
                exists = model_path.exists()
                model_status[model_key] = exists
                
                if exists:
                    size_gb = model_path.stat().st_size / (1024**3)
                    self.logger.debug(f"✅ {description}: {size_gb:.1f}GB")
                else:
                    self.logger.warning(f"❌ {description}: Missing at {model_path}")
                    
            except Exception as e:
                self.logger.error(f"Error checking {description}: {e}")
                model_status[model_key] = False
        
        missing_models = [k for k, v in model_status.items() if not v]
        if missing_models:
            self.logger.error(f"Missing required models: {missing_models}")
        
        return model_status
    
    @log_performance
    def start_server(self) -> None:
        """Start ComfyUI server with FP8 optimizations"""
        if self.is_running:
            self.logger.info("ComfyUI server already running")
            return
        
        # Validate prerequisites
        self.validate_cuda()
        model_status = self.validate_models()
        
        if not all(model_status.values()):
            raise ComfyUIError("Cannot start server: Missing required models")
        
        # Kill any existing ComfyUI processes
        self._kill_existing_processes()
        
        # Start server
        cmd = [
            "python", "main.py",
            "--listen", self.config.comfyui.host,
            "--port", str(self.config.comfyui.port),
            "--fp8_e4m3fn-unet",  # Enable FP8 optimization
        ]
        
        if self.config.comfyui.enable_cors:
            cmd.extend(["--enable-cors-header", "*"])
        
        self.logger.info(f"Starting ComfyUI server: {' '.join(cmd)}")
        
        try:
            self.process = subprocess.Popen(
                cmd,
                cwd=self.config.comfyui_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for server to be ready
            self._wait_for_server()
            self.is_running = True
            self.logger.info(f"ComfyUI server started at {self.config.comfyui.url}")
            
        except Exception as e:
            raise ComfyUIError(f"Failed to start ComfyUI server: {e}")
    
    def _kill_existing_processes(self) -> None:
        """Kill any existing ComfyUI processes"""
        try:
            subprocess.run(
                ["pkill", "-f", "ComfyUI/main.py"],
                capture_output=True,
                timeout=5
            )
            time.sleep(2)
        except subprocess.TimeoutExpired:
            pass
    
    def _wait_for_server(self) -> None:
        """Wait for ComfyUI server to be ready"""
        timeout = self.config.comfyui.startup_timeout
        start_time = time.time()
        
        self.logger.info("Waiting for ComfyUI server to start...")
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(
                    f"{self.config.comfyui.url}/system_stats",
                    timeout=2
                )
                if response.status_code == 200:
                    self.logger.info("ComfyUI server is ready")
                    return
                    
            except requests.RequestException:
                pass
            
            time.sleep(1)
            
        raise ComfyUITimeoutError(f"Server failed to start within {timeout}s")
    
    @log_performance
    def stop_server(self) -> None:
        """Stop ComfyUI server gracefully"""
        if not self.is_running:
            return
            
        if self.process:
            self.logger.info("Stopping ComfyUI server...")
            self.process.terminate()
            
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.logger.warning("Force killing ComfyUI server")
                self.process.kill()
                self.process.wait()
        
        self._kill_existing_processes()
        self.is_running = False
        self.process = None
        self.logger.info("ComfyUI server stopped")
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get ComfyUI system statistics"""
        if not self.is_running:
            raise ComfyUIConnectionError("Server not running")
        
        try:
            response = requests.get(
                f"{self.config.comfyui.url}/system_stats",
                timeout=self.config.comfyui.api_timeout
            )
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            raise ComfyUIConnectionError(f"Failed to get system stats: {e}")
    
    def validate_workflow(self, workflow: Dict[str, Any]) -> bool:
        """Validate workflow JSON structure"""
        required_keys = ["1", "2", "3"]  # Basic node structure
        
        if not isinstance(workflow, dict):
            return False
            
        # Check for required nodes
        for key in required_keys:
            if key not in workflow:
                self.logger.warning(f"Missing required node: {key}")
                return False
        
        return True
    
    @log_performance
    def generate_image(
        self,
        settings: GenerationSettings,
        workflow_path: Optional[Path] = None
    ) -> GenerationResult:
        """
        Generate image using ComfyUI workflow
        
        Args:
            settings: Generation settings
            workflow_path: Custom workflow file (optional)
            
        Returns:
            GenerationResult with images and metadata
        """
        if not self.is_running:
            self.start_server()
        
        # Load workflow
        if workflow_path is None:
            workflow_path = self.config.workflows_dir / "flux_kontext_fp8.json"
        
        if not workflow_path.exists():
            raise ComfyUIError(f"Workflow not found: {workflow_path}")
        
        with open(workflow_path) as f:
            workflow = json.load(f)
        
        if not self.validate_workflow(workflow):
            raise ComfyUIError(f"Invalid workflow: {workflow_path}")
        
        # Update workflow with settings
        workflow = self._update_workflow_settings(workflow, settings)
        
        # Execute workflow
        start_time = time.time()
        workflow_id = f"gen_{int(time.time())}"
        
        try:
            # Queue workflow
            response = requests.post(
                f"{self.config.comfyui.url}/prompt",
                json={"prompt": workflow},
                timeout=self.config.comfyui.api_timeout
            )
            response.raise_for_status()
            
            prompt_data = response.json()
            prompt_id = prompt_data.get("prompt_id")
            
            if not prompt_id:
                raise ComfyUIError("No prompt ID returned from server")
            
            self.logger.info(f"Generation started: {prompt_id}")
            
            # Wait for completion and collect results
            images = self._wait_for_generation(prompt_id)
            execution_time = time.time() - start_time
            
            result = GenerationResult(
                images=images,
                settings=settings,
                execution_time=execution_time,
                workflow_id=workflow_id,
                metadata={
                    "prompt_id": prompt_id,
                    "workflow_path": str(workflow_path),
                    "timestamp": time.time()
                }
            )
            
            self.logger.info(f"Generation completed in {execution_time:.2f}s: {len(images)} images")
            return result
            
        except Exception as e:
            raise ComfyUIError(f"Generation failed: {e}")
    
    def _update_workflow_settings(
        self,
        workflow: Dict[str, Any],
        settings: GenerationSettings
    ) -> Dict[str, Any]:
        """Update workflow with generation settings"""
        
        # Node mapping (adjust based on your workflow)
        node_mappings = {
            "3": {"inputs": {"text": settings.prompt}},  # Prompt
            "6": {"inputs": {"guidance": settings.cfg_scale}},  # CFG
            "7": {"inputs": {"batch_size": settings.batch_size}},  # Batch
            "8": {"inputs": {"steps": settings.steps}},  # Steps
        }
        
        # Update seed if specified
        if settings.seed > 0:
            node_mappings["9"] = {"inputs": {"seed": settings.seed}}
        
        # Apply updates
        for node_id, updates in node_mappings.items():
            if node_id in workflow:
                workflow[node_id]["inputs"].update(updates["inputs"])
        
        return workflow
    
    def _wait_for_generation(self, prompt_id: str, timeout: int = 300) -> List[Path]:
        """Wait for generation to complete and return image paths"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Check if generation is complete
                response = requests.get(
                    f"{self.config.comfyui.url}/history/{prompt_id}",
                    timeout=self.config.comfyui.api_timeout
                )
                
                if response.status_code == 200:
                    history = response.json()
                    if prompt_id in history:
                        outputs = history[prompt_id].get("outputs", {})
                        if outputs:
                            return self._collect_output_images(outputs)
                
            except requests.RequestException:
                pass
            
            time.sleep(2)
        
        raise ComfyUITimeoutError(f"Generation timeout after {timeout}s")
    
    def _collect_output_images(self, outputs: Dict[str, Any]) -> List[Path]:
        """Collect generated image files"""
        images = []
        output_dir = self.config.comfyui_dir / "output"
        
        for node_id, node_output in outputs.items():
            if "images" in node_output:
                for image_info in node_output["images"]:
                    filename = image_info.get("filename")
                    if filename:
                        image_path = output_dir / filename
                        if image_path.exists():
                            images.append(image_path)
        
        return images
    
    @log_performance
    def batch_generate(
        self,
        settings_list: List[GenerationSettings],
        workflow_path: Optional[Path] = None
    ) -> List[GenerationResult]:
        """Generate multiple images with different settings"""
        results = []
        
        for i, settings in enumerate(settings_list):
            self.logger.info(f"Generating batch {i+1}/{len(settings_list)}")
            
            try:
                result = self.generate_image(settings, workflow_path)
                results.append(result)
                
            except Exception as e:
                self.logger.error(f"Batch generation {i+1} failed: {e}")
                continue
        
        return results
    
    def cleanup(self) -> None:
        """Cleanup resources"""
        self.stop_server()


# Convenience functions for common operations
def quick_generate(
    prompt: str,
    steps: int = 28,
    cfg_scale: float = 3.5,
    batch_size: int = 1
) -> GenerationResult:
    """Quick image generation with default settings"""
    settings = GenerationSettings(
        prompt=prompt,
        steps=steps,
        cfg_scale=cfg_scale,
        batch_size=batch_size
    )
    
    with ComfyUIManager() as manager:
        return manager.generate_image(settings)


def test_connection() -> bool:
    """Test ComfyUI server connection"""
    try:
        with ComfyUIManager() as manager:
            stats = manager.get_system_stats()
            return True
    except Exception:
        return False