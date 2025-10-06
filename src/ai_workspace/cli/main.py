"""
AI Workspace CLI - Main Interface

Unified command-line interface for all AI workspace operations.
"""

import sys
import argparse
import json
from pathlib import Path
from typing import Optional, List, Dict, Any

from ..config.settings import get_config, Config
from ..comfyui.manager import ComfyUIManager, GenerationSettings, quick_generate
from ..utils.logging import setup_logging, get_logger, log_system_info
from ..utils.exceptions import AIWorkspaceError, ConfigurationError


class AIWorkspaceCLI:
    """Main CLI application"""
    
    def __init__(self):
        self.config = get_config()
        self.logger = get_logger("ai_workspace.cli")
        
    def setup_arguments(self) -> argparse.ArgumentParser:
        """Setup command-line arguments"""
        parser = argparse.ArgumentParser(
            description="AI Workspace - Professional FP8 Portrait Generation System",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s generate "cyberpunk warrior princess" --steps 32 --cfg 4.0
  %(prog)s server start
  %(prog)s validate --models
  %(prog)s config show
            """
        )
        
        parser.add_argument(
            "--config", 
            type=Path, 
            help="Configuration file path"
        )
        parser.add_argument(
            "--log-level", 
            choices=["DEBUG", "INFO", "WARNING", "ERROR"],
            default="INFO",
            help="Logging level"
        )
        parser.add_argument(
            "--verbose", "-v", 
            action="store_true",
            help="Verbose output"
        )
        
        subparsers = parser.add_subparsers(dest="command", help="Available commands")
        
        # Generate command
        gen_parser = subparsers.add_parser("generate", help="Generate images")
        gen_parser.add_argument("prompt", help="Text prompt for generation")
        gen_parser.add_argument("--steps", type=int, default=28, help="Diffusion steps")
        gen_parser.add_argument("--cfg", type=float, default=3.5, help="CFG scale")
        gen_parser.add_argument("--batch-size", type=int, default=1, help="Number of images")
        gen_parser.add_argument("--seed", type=int, default=-1, help="Random seed")
        gen_parser.add_argument("--width", type=int, default=1024, help="Image width")
        gen_parser.add_argument("--height", type=int, default=1024, help="Image height")
        gen_parser.add_argument("--workflow", type=Path, help="Custom workflow file")
        gen_parser.add_argument("--output-dir", type=Path, help="Output directory")
        
        # Server management
        server_parser = subparsers.add_parser("server", help="Server management")
        server_subparsers = server_parser.add_subparsers(dest="server_action")
        server_subparsers.add_parser("start", help="Start ComfyUI server")
        server_subparsers.add_parser("stop", help="Stop ComfyUI server")
        server_subparsers.add_parser("status", help="Server status")
        server_subparsers.add_parser("restart", help="Restart server")
        
        # Validation
        validate_parser = subparsers.add_parser("validate", help="System validation")
        validate_parser.add_argument("--cuda", action="store_true", help="Validate CUDA")
        validate_parser.add_argument("--models", action="store_true", help="Validate models")
        validate_parser.add_argument("--config-only", action="store_true", help="Validate config only")
        validate_parser.add_argument("--all", action="store_true", help="Validate everything")
        
        # Configuration
        config_parser = subparsers.add_parser("config", help="Configuration management")
        config_subparsers = config_parser.add_subparsers(dest="config_action")
        config_subparsers.add_parser("show", help="Show current configuration")
        config_subparsers.add_parser("init", help="Initialize default configuration")
        
        save_parser = config_subparsers.add_parser("save", help="Save configuration")
        save_parser.add_argument("path", type=Path, help="Configuration file path")
        
        load_parser = config_subparsers.add_parser("load", help="Load configuration")
        load_parser.add_argument("path", type=Path, help="Configuration file path")
        
        # Batch operations
        batch_parser = subparsers.add_parser("batch", help="Batch operations")
        batch_parser.add_argument("config_file", type=Path, help="Batch configuration JSON")
        batch_parser.add_argument("--max-concurrent", type=int, default=1, help="Max concurrent generations")
        
        # System info
        subparsers.add_parser("info", help="System information")
        
        # Test
        test_parser = subparsers.add_parser("test", help="System tests")
        test_parser.add_argument("--quick", action="store_true", help="Quick test")
        test_parser.add_argument("--full", action="store_true", help="Full system test")
        
        return parser
    
    def run(self, args: Optional[List[str]] = None) -> int:
        """Run CLI application"""
        parser = self.setup_arguments()
        parsed_args = parser.parse_args(args)
        
        # Setup logging
        log_level = "DEBUG" if parsed_args.verbose else parsed_args.log_level
        setup_logging("ai_workspace", level=log_level)
        
        try:
            # Load configuration
            if parsed_args.config:
                self.config = Config.load(parsed_args.config)
            
            # Route to appropriate handler
            if parsed_args.command == "generate":
                return self.handle_generate(parsed_args)
            elif parsed_args.command == "server":
                return self.handle_server(parsed_args)
            elif parsed_args.command == "validate":
                return self.handle_validate(parsed_args)
            elif parsed_args.command == "config":
                return self.handle_config(parsed_args)
            elif parsed_args.command == "batch":
                return self.handle_batch(parsed_args)
            elif parsed_args.command == "info":
                return self.handle_info(parsed_args)
            elif parsed_args.command == "test":
                return self.handle_test(parsed_args)
            else:
                parser.print_help()
                return 1
                
        except AIWorkspaceError as e:
            self.logger.error(f"AI Workspace Error: {e}")
            if parsed_args.verbose and e.details:
                self.logger.error(f"Details: {e.details}")
            return 1
        except KeyboardInterrupt:
            self.logger.info("Operation cancelled by user")
            return 130
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            if parsed_args.verbose:
                import traceback
                traceback.print_exc()
            return 1
    
    def handle_generate(self, args) -> int:
        """Handle image generation"""
        self.logger.info(f"Generating image: {args.prompt}")
        
        settings = GenerationSettings(
            prompt=args.prompt,
            steps=args.steps,
            cfg_scale=args.cfg,
            batch_size=args.batch_size,
            seed=args.seed,
            width=args.width,
            height=args.height
        )
        
        try:
            with ComfyUIManager() as manager:
                result = manager.generate_image(settings, args.workflow)
                
                self.logger.info(f"Generation completed in {result.execution_time:.2f}s")
                self.logger.info(f"Generated {len(result.images)} images:")
                
                for image_path in result.images:
                    print(f"  📸 {image_path}")
                    
                    # Copy to output directory if specified
                    if args.output_dir:
                        args.output_dir.mkdir(parents=True, exist_ok=True)
                        output_path = args.output_dir / image_path.name
                        output_path.write_bytes(image_path.read_bytes())
                        print(f"  📁 Copied to: {output_path}")
                
                return 0
                
        except Exception as e:
            self.logger.error(f"Generation failed: {e}")
            return 1
    
    def handle_server(self, args) -> int:
        """Handle server management"""
        if args.server_action == "start":
            try:
                manager = ComfyUIManager()
                manager.start_server()
                self.logger.info("ComfyUI server started successfully")
                return 0
            except Exception as e:
                self.logger.error(f"Failed to start server: {e}")
                return 1
                
        elif args.server_action == "stop":
            try:
                manager = ComfyUIManager()
                manager.stop_server()
                self.logger.info("ComfyUI server stopped")
                return 0
            except Exception as e:
                self.logger.error(f"Failed to stop server: {e}")
                return 1
                
        elif args.server_action == "status":
            try:
                manager = ComfyUIManager()
                if manager.is_running:
                    stats = manager.get_system_stats()
                    print("🟢 ComfyUI server is running")
                    print(f"   URL: {manager.config.comfyui.url}")
                    
                    if "system" in stats:
                        system = stats["system"]
                        print(f"   GPU: {system.get('gpu_name', 'Unknown')}")
                        print(f"   VRAM: {system.get('vram_total', 0)/1024/1024/1024:.1f}GB")
                else:
                    print("🔴 ComfyUI server is not running")
                return 0
            except Exception as e:
                print("🔴 ComfyUI server is not running")
                if args.verbose:
                    self.logger.error(f"Status check failed: {e}")
                return 1
                
        elif args.server_action == "restart":
            try:
                manager = ComfyUIManager()
                manager.stop_server()
                manager.start_server()
                self.logger.info("ComfyUI server restarted")
                return 0
            except Exception as e:
                self.logger.error(f"Failed to restart server: {e}")
                return 1
        
        return 0
    
    def handle_validate(self, args) -> int:
        """Handle system validation"""
        try:
            manager = ComfyUIManager()
            success = True
            
            if args.config_only or args.all:
                print("📋 Validating configuration...")
                try:
                    self.config.validate()
                    print("   ✅ Configuration valid")
                except Exception as e:
                    print(f"   ❌ Configuration error: {e}")
                    success = False
            
            if args.cuda or args.all:
                print("🔥 Validating CUDA...")
                try:
                    manager.validate_cuda()
                    print("   ✅ CUDA available")
                except Exception as e:
                    print(f"   ❌ CUDA error: {e}")
                    success = False
            
            if args.models or args.all:
                print("📦 Validating models...")
                model_status = manager.validate_models()
                
                for model_key, status in model_status.items():
                    status_icon = "✅" if status else "❌"
                    print(f"   {status_icon} {model_key}: {'OK' if status else 'Missing'}")
                
                if not all(model_status.values()):
                    success = False
            
            return 0 if success else 1
            
        except Exception as e:
            self.logger.error(f"Validation failed: {e}")
            return 1
    
    def handle_config(self, args) -> int:
        """Handle configuration management"""
        if args.config_action == "show":
            print("📋 Current Configuration:")
            config_dict = self.config.to_dict()
            print(json.dumps(config_dict, indent=2, default=str))
            return 0
            
        elif args.config_action == "init":
            config_path = Path.cwd() / "configs" / "ai_workspace.yaml"
            try:
                config_path.parent.mkdir(parents=True, exist_ok=True)
                self.config.save(config_path)
                print(f"📁 Configuration initialized: {config_path}")
                return 0
            except Exception as e:
                self.logger.error(f"Failed to initialize config: {e}")
                return 1
                
        elif args.config_action == "save":
            try:
                self.config.save(args.path)
                print(f"📁 Configuration saved: {args.path}")
                return 0
            except Exception as e:
                self.logger.error(f"Failed to save config: {e}")
                return 1
                
        elif args.config_action == "load":
            try:
                self.config = Config.load(args.path)
                print(f"📁 Configuration loaded: {args.path}")
                return 0
            except Exception as e:
                self.logger.error(f"Failed to load config: {e}")
                return 1
        
        return 0
    
    def handle_batch(self, args) -> int:
        """Handle batch operations"""
        try:
            with open(args.config_file) as f:
                batch_config = json.load(f)
            
            settings_list = []
            for item in batch_config.get("generations", []):
                settings = GenerationSettings(**item)
                settings_list.append(settings)
            
            self.logger.info(f"Starting batch generation: {len(settings_list)} items")
            
            with ComfyUIManager() as manager:
                results = manager.batch_generate(settings_list)
                
                self.logger.info(f"Batch completed: {len(results)} successful generations")
                
                for i, result in enumerate(results):
                    print(f"Batch {i+1}: {len(result.images)} images in {result.execution_time:.2f}s")
                    for image_path in result.images:
                        print(f"  📸 {image_path}")
                
                return 0
                
        except Exception as e:
            self.logger.error(f"Batch processing failed: {e}")
            return 1
    
    def handle_info(self, args) -> int:
        """Handle system information"""
        print("🖥️  AI Workspace System Information")
        print("=" * 40)
        
        log_system_info()
        
        try:
            self.config.validate()
            print("📋 Configuration: ✅ Valid")
        except Exception as e:
            print(f"📋 Configuration: ❌ {e}")
        
        return 0
    
    def handle_test(self, args) -> int:
        """Handle system tests"""
        if args.quick:
            print("🧪 Running quick test...")
            try:
                result = quick_generate("test prompt", steps=1)
                print(f"✅ Quick test passed: {len(result.images)} images generated")
                return 0
            except Exception as e:
                print(f"❌ Quick test failed: {e}")
                return 1
                
        elif args.full:
            print("🧪 Running full system test...")
            # Implement comprehensive test suite
            return self.handle_validate(argparse.Namespace(
                config_only=False, cuda=True, models=True, all=True
            ))
        
        return 0


def main():
    """Main entry point"""
    cli = AIWorkspaceCLI()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())