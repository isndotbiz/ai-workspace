"""
AI Workspace Exception Hierarchy

Custom exceptions for better error handling and debugging.
"""

from typing import Optional, Any, Dict


class AIWorkspaceError(Exception):
    """Base exception for AI Workspace"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def __str__(self) -> str:
        if self.details:
            return f"{self.message} (Details: {self.details})"
        return self.message


class ConfigurationError(AIWorkspaceError):
    """Configuration-related errors"""
    pass


class ComfyUIError(AIWorkspaceError):
    """ComfyUI-related errors"""
    pass


class ComfyUIConnectionError(ComfyUIError):
    """ComfyUI connection failures"""
    pass


class ComfyUITimeoutError(ComfyUIError):
    """ComfyUI operation timeouts"""
    pass


class WorkflowError(AIWorkspaceError):
    """Workflow execution errors"""
    pass


class WorkflowValidationError(WorkflowError):
    """Workflow validation failures"""
    pass


class ModelError(AIWorkspaceError):
    """Model-related errors"""
    pass


class ModelNotFoundError(ModelError):
    """Model file not found"""
    pass


class CUDAError(AIWorkspaceError):
    """CUDA-related errors"""
    pass


class OllamaError(AIWorkspaceError):
    """Ollama AI service errors"""
    pass


class OllamaConnectionError(OllamaError):
    """Ollama connection failures"""
    pass


class PromptError(AIWorkspaceError):
    """Prompt processing errors"""
    pass


class GenerationError(AIWorkspaceError):
    """Image generation errors"""
    pass


class ValidationError(AIWorkspaceError):
    """Input validation errors"""
    pass


# Error codes for programmatic handling
ERROR_CODES = {
    'CONFIG_INVALID': 1001,
    'CONFIG_MISSING': 1002,
    'CUDA_UNAVAILABLE': 2001,
    'MODEL_MISSING': 2002,
    'COMFYUI_CONNECTION': 3001,
    'COMFYUI_TIMEOUT': 3002,
    'WORKFLOW_INVALID': 4001,
    'WORKFLOW_FAILED': 4002,
    'OLLAMA_UNAVAILABLE': 5001,
    'PROMPT_INVALID': 5002,
    'GENERATION_FAILED': 6001,
    'VALIDATION_FAILED': 7001,
}


def get_error_code(error_type: str) -> Optional[int]:
    """Get error code for error type"""
    return ERROR_CODES.get(error_type.upper())


def create_error(error_type: str, message: str, details: Optional[Dict[str, Any]] = None) -> AIWorkspaceError:
    """Create appropriate error based on type"""
    error_map = {
        'configuration': ConfigurationError,
        'comfyui': ComfyUIError,
        'comfyui_connection': ComfyUIConnectionError,
        'comfyui_timeout': ComfyUITimeoutError,
        'workflow': WorkflowError,
        'workflow_validation': WorkflowValidationError,
        'model': ModelError,
        'model_not_found': ModelNotFoundError,
        'cuda': CUDAError,
        'ollama': OllamaError,
        'ollama_connection': OllamaConnectionError,
        'prompt': PromptError,
        'generation': GenerationError,
        'validation': ValidationError,
    }
    
    error_class = error_map.get(error_type, AIWorkspaceError)
    return error_class(message, details)