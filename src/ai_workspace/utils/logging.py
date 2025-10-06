"""
Centralized Logging System

Professional logging with rotation, levels, and structured output.
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional, Union
import sys
from datetime import datetime


class ColoredFormatter(logging.Formatter):
    """Colored console formatter for better readability"""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        # Add color to levelname
        if record.levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[record.levelname]}"
                f"{record.levelname:8}"
                f"{self.COLORS['RESET']}"
            )
        
        return super().format(record)


def setup_logging(
    name: str = "ai_workspace",
    level: Union[str, int] = logging.INFO,
    log_dir: Optional[Path] = None,
    console: bool = True,
    file_logging: bool = True,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Setup centralized logging system
    
    Args:
        name: Logger name
        level: Logging level
        log_dir: Directory for log files
        console: Enable console logging
        file_logging: Enable file logging  
        max_bytes: Max bytes per log file
        backup_count: Number of backup files
        
    Returns:
        Configured logger instance
    """
    
    # Convert string level to int
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Setup log directory
    if log_dir is None:
        log_dir = Path.cwd() / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # Console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        
        console_format = ColoredFormatter(
            '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)
    
    # File handler with rotation
    if file_logging:
        log_file = log_dir / f"{name}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        
        file_format = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
    
    # Error file handler (separate file for errors)
    if file_logging:
        error_log_file = log_dir / f"{name}_errors.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_format)
        logger.addHandler(error_handler)
    
    logger.info(f"Logging initialized for {name} (level: {logging.getLevelName(level)})")
    return logger


def get_logger(name: str = None) -> logging.Logger:
    """Get logger instance (creates if doesn't exist)"""
    if name is None:
        name = "ai_workspace"
    
    logger = logging.getLogger(name)
    if not logger.handlers:
        # Setup with default configuration if not already configured
        setup_logging(name)
    
    return logger


class LogContext:
    """Context manager for temporary log level changes"""
    
    def __init__(self, logger: logging.Logger, level: Union[str, int]):
        self.logger = logger
        self.original_level = logger.level
        
        if isinstance(level, str):
            level = getattr(logging, level.upper(), logging.INFO)
        self.new_level = level
    
    def __enter__(self):
        self.logger.setLevel(self.new_level)
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.setLevel(self.original_level)


def log_performance(func):
    """Decorator to log function performance"""
    import functools
    import time
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        start_time = time.time()
        
        try:
            logger.debug(f"Starting {func.__name__}")
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            logger.debug(f"Completed {func.__name__} in {duration:.3f}s")
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed {func.__name__} after {duration:.3f}s: {e}")
            raise
    
    return wrapper


def log_system_info():
    """Log system information for debugging"""
    logger = get_logger("ai_workspace.system")
    
    try:
        import torch
        import platform
        import psutil
        
        logger.info(f"Platform: {platform.platform()}")
        logger.info(f"Python: {sys.version}")
        logger.info(f"PyTorch: {torch.__version__}")
        logger.info(f"CUDA Available: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
            logger.info(f"CUDA Version: {torch.version.cuda}")
        
        logger.info(f"CPU Count: {psutil.cpu_count()}")
        memory = psutil.virtual_memory()
        logger.info(f"RAM: {memory.total / 1024**3:.1f}GB (available: {memory.available / 1024**3:.1f}GB)")
        
    except ImportError as e:
        logger.warning(f"Could not log system info: {e}")


# Initialize default logger
_default_logger = None

def init_logging(level: str = "INFO", log_dir: Optional[Path] = None) -> None:
    """Initialize default logging configuration"""
    global _default_logger
    _default_logger = setup_logging("ai_workspace", level=level, log_dir=log_dir)