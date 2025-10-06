"""
AI Workspace - Professional FP8 Portrait Generation System

A comprehensive CUDA-only AI workspace optimized for RTX 4060 Ti 16GB,
featuring FLUX.1-dev FP8 Kontext with ComfyUI, advanced multi-image workflows,
and AI-powered prompt enhancement.
"""

__version__ = "2.0.0-clean"
__author__ = "AI Workspace Team"
__description__ = "Professional FP8 Portrait Generation System"

from .config.settings import Config
from .utils.logging import setup_logging
from .utils.exceptions import AIWorkspaceError

# Initialize logging
logger = setup_logging(__name__)

__all__ = [
    "Config",
    "setup_logging", 
    "AIWorkspaceError",
    "__version__",
]