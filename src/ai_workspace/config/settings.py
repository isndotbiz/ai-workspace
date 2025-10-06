"""
Configuration Management System

Centralized settings for AI Workspace with validation and type safety.
"""

from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
import os
import yaml
import json

from ..utils.exceptions import ConfigurationError


@dataclass
class ModelConfig:
    """FP8 Model configuration"""
    fp8_model_path: str = "ComfyUI/models/checkpoints/flux1-dev-kontext_fp8_scaled.safetensors"
    t5_encoder_path: str = "ComfyUI/models/clip/t5xxl_fp8_e4m3fn.safetensors"
    clip_encoder_path: str = "ComfyUI/models/clip/clip_l.safetensors"
    vae_path: str = "ComfyUI/models/vae/ae.safetensors"
    turbo_lora_path: str = "ComfyUI/models/loras/FLUX.1-Turbo-Alpha.safetensors"


@dataclass
class ComfyUIConfig:
    """ComfyUI server configuration"""
    host: str = "0.0.0.0"
    port: int = 8188
    startup_timeout: int = 30
    api_timeout: int = 10
    enable_cors: bool = True
    
    @property
    def url(self) -> str:
        return f"http://127.0.0.1:{self.port}"


@dataclass
class OllamaConfig:
    """Ollama AI configuration"""
    host: str = "127.0.0.1"
    port: int = 11434
    default_model: str = "mistral:7b"
    timeout: int = 30
    max_tokens: int = 512


@dataclass
class WorkflowConfig:
    """Default workflow settings"""
    default_steps: int = 28
    default_cfg: float = 3.5
    default_batch_size: int = 1
    default_resolution: tuple = (1024, 1024)
    multi_image_steps: int = 32
    multi_image_cfg: float = 4.0


@dataclass
class Config:
    """Main configuration class"""
    
    # Base paths
    workspace_dir: Path = field(default_factory=lambda: Path.cwd())
    comfyui_dir: Path = field(default_factory=lambda: Path.cwd() / "ComfyUI")
    workflows_dir: Path = field(default_factory=lambda: Path.cwd() / "workflows_clean")
    output_dir: Path = field(default_factory=lambda: Path.cwd() / "output")
    
    # Subconfigs
    models: ModelConfig = field(default_factory=ModelConfig)
    comfyui: ComfyUIConfig = field(default_factory=ComfyUIConfig)
    ollama: OllamaConfig = field(default_factory=OllamaConfig)
    workflow: WorkflowConfig = field(default_factory=WorkflowConfig)
    
    # System settings
    cuda_only: bool = True
    debug: bool = False
    log_level: str = "INFO"
    
    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> "Config":
        """Load configuration from file or create default"""
        if config_path and config_path.exists():
            return cls.from_file(config_path)
        return cls()
    
    @classmethod
    def from_file(cls, config_path: Path) -> "Config":
        """Load configuration from YAML or JSON file"""
        try:
            if config_path.suffix.lower() in ['.yaml', '.yml']:
                with open(config_path) as f:
                    data = yaml.safe_load(f)
            elif config_path.suffix.lower() == '.json':
                with open(config_path) as f:
                    data = json.load(f)
            else:
                raise ConfigurationError(f"Unsupported config format: {config_path.suffix}")
                
            return cls.from_dict(data)
        except Exception as e:
            raise ConfigurationError(f"Failed to load config from {config_path}: {e}")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        """Create config from dictionary"""
        # Convert paths to Path objects
        for key in ['workspace_dir', 'comfyui_dir', 'workflows_dir', 'output_dir']:
            if key in data:
                data[key] = Path(data[key])
        
        # Handle nested configs
        if 'models' in data:
            data['models'] = ModelConfig(**data['models'])
        if 'comfyui' in data:
            data['comfyui'] = ComfyUIConfig(**data['comfyui'])
        if 'ollama' in data:
            data['ollama'] = OllamaConfig(**data['ollama'])
        if 'workflow' in data:
            data['workflow'] = WorkflowConfig(**data['workflow'])
            
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, Path):
                result[key] = str(value)
            elif hasattr(value, '__dict__'):
                result[key] = value.__dict__
            else:
                result[key] = value
        return result
    
    def save(self, config_path: Path) -> None:
        """Save configuration to file"""
        try:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            if config_path.suffix.lower() in ['.yaml', '.yml']:
                with open(config_path, 'w') as f:
                    yaml.safe_dump(self.to_dict(), f, indent=2)
            elif config_path.suffix.lower() == '.json':
                with open(config_path, 'w') as f:
                    json.dump(self.to_dict(), f, indent=2)
            else:
                raise ConfigurationError(f"Unsupported config format: {config_path.suffix}")
                
        except Exception as e:
            raise ConfigurationError(f"Failed to save config to {config_path}: {e}")
    
    def validate(self) -> None:
        """Validate configuration settings"""
        # Check CUDA requirement
        if self.cuda_only:
            try:
                import torch
                if not torch.cuda.is_available():
                    raise ConfigurationError("CUDA required but not available")
            except ImportError:
                raise ConfigurationError("PyTorch not available for CUDA validation")
        
        # Check required paths
        if not self.comfyui_dir.exists():
            raise ConfigurationError(f"ComfyUI directory not found: {self.comfyui_dir}")
        
        # Validate model paths
        model_paths = [
            self.comfyui_dir / self.models.fp8_model_path.replace('ComfyUI/', ''),
            self.comfyui_dir / self.models.t5_encoder_path.replace('ComfyUI/', ''),
            self.comfyui_dir / self.models.clip_encoder_path.replace('ComfyUI/', ''),
            self.comfyui_dir / self.models.vae_path.replace('ComfyUI/', ''),
        ]
        
        missing_models = [p for p in model_paths if not p.exists()]
        if missing_models:
            raise ConfigurationError(f"Missing model files: {missing_models}")
    
    def get_model_path(self, model_type: str) -> Path:
        """Get absolute path for a model"""
        model_mapping = {
            'fp8': self.models.fp8_model_path,
            't5': self.models.t5_encoder_path,
            'clip': self.models.clip_encoder_path,
            'vae': self.models.vae_path,
            'turbo_lora': self.models.turbo_lora_path,
        }
        
        if model_type not in model_mapping:
            raise ConfigurationError(f"Unknown model type: {model_type}")
        
        rel_path = model_mapping[model_type].replace('ComfyUI/', '')
        return self.comfyui_dir / rel_path


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get global configuration instance"""
    global _config
    if _config is None:
        config_path = Path.cwd() / "configs" / "ai_workspace.yaml"
        _config = Config.load(config_path)
    return _config


def set_config(config: Config) -> None:
    """Set global configuration instance"""
    global _config
    _config = config