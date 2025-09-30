#!/usr/bin/env python3
"""
FP8 Installation Verification Script for AI Workspace

Validates that the workspace has been successfully migrated to FP8-only architecture.
Tests model files, ComfyUI health, workflow validity, and system resources.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import subprocess
import urllib.request
import urllib.error

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


class FP8Verifier:
    """Verification system for FP8 migration."""
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.comfyui_path = workspace_root / "ComfyUI"
        self.models_path = self.comfyui_path / "models"
        self.workflows_path = workspace_root / "workflows"
        
        self.results: List[Tuple[str, bool, str]] = []
        self.warnings: List[str] = []
    
    def log_test(self, name: str, passed: bool, details: str = ""):
        """Log a test result."""
        status = f"{GREEN}✓{RESET}" if passed else f"{RED}✗{RESET}"
        print(f"{status} {name}")
        if details:
            print(f"  {details}")
        self.results.append((name, passed, details))
    
    def log_warning(self, message: str):
        """Log a warning."""
        print(f"{YELLOW}⚠{RESET} {message}")
        self.warnings.append(message)
    
    def verify_fp8_models(self) -> bool:
        """Verify all required FP8 models are present with correct sizes."""
        print(f"\n{BLUE}=== Verifying FP8 Models ==={RESET}")
        
        expected_models = {
            "checkpoints/flux1-dev-kontext_fp8_scaled.safetensors": (11.5e9, 12.5e9),  # ~12GB
            "clip/t5xxl_fp8_e4m3fn.safetensors": (4.5e9, 5.5e9),  # ~4.9GB
            "clip/clip_l.safetensors": (200e6, 300e6),  # ~246MB
            "vae/ae.safetensors": (300e6, 400e6),  # ~335MB
        }
        
        all_present = True
        for model_path, (min_size, max_size) in expected_models.items():
            full_path = self.models_path / model_path
            
            if not full_path.exists():
                self.log_test(f"Model: {model_path}", False, f"File not found")
                all_present = False
                continue
            
            size = full_path.stat().st_size
            size_gb = size / 1e9
            
            if min_size <= size <= max_size:
                self.log_test(
                    f"Model: {model_path}",
                    True,
                    f"Size: {size_gb:.2f}GB"
                )
            else:
                self.log_test(
                    f"Model: {model_path}",
                    False,
                    f"Size {size_gb:.2f}GB outside expected range"
                )
                all_present = False
        
        return all_present
    
    def verify_no_gguf_models(self) -> bool:
        """Verify that no GGUF models remain in active directories."""
        print(f"\n{BLUE}=== Checking for GGUF Files ==={RESET}")
        
        gguf_files = list(self.models_path.rglob("*.gguf"))
        
        if not gguf_files:
            self.log_test("No GGUF files in models/", True, "Migration complete")
            return True
        else:
            details = f"Found {len(gguf_files)} GGUF files: " + ", ".join(
                f.name for f in gguf_files[:3]
            )
            if len(gguf_files) > 3:
                details += f" (and {len(gguf_files) - 3} more)"
            self.log_test("No GGUF files in models/", False, details)
            return False
    
    def verify_gguf_custom_node_disabled(self) -> bool:
        """Verify GGUF custom node is disabled."""
        print(f"\n{BLUE}=== Checking Custom Nodes ==={RESET}")
        
        custom_nodes_path = self.comfyui_path / "custom_nodes"
        gguf_node_active = (custom_nodes_path / "ComfyUI-GGUF").exists()
        gguf_node_disabled = (custom_nodes_path / "ComfyUI-GGUF.disabled").exists()
        
        if gguf_node_disabled and not gguf_node_active:
            self.log_test("GGUF custom node disabled", True)
            return True
        elif not gguf_node_active and not gguf_node_disabled:
            self.log_test("GGUF custom node removed", True)
            return True
        else:
            self.log_test(
                "GGUF custom node disabled",
                False,
                "ComfyUI-GGUF is still active"
            )
            return False
    
    def verify_comfyui_running(self) -> bool:
        """Check if ComfyUI server is accessible."""
        print(f"\n{BLUE}=== Checking ComfyUI Service ==={RESET}")
        
        try:
            with urllib.request.urlopen("http://localhost:8188/system_stats", timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read())
                    comfyui_version = data.get("system", {}).get("comfyui_version", "unknown")
                    pytorch_version = data.get("system", {}).get("pytorch_version", "unknown")
                    
                    self.log_test(
                        "ComfyUI server accessible",
                        True,
                        f"v{comfyui_version}, PyTorch {pytorch_version}"
                    )
                    
                    # Check GPU
                    devices = data.get("devices", [])
                    if devices:
                        gpu_name = devices[0].get("name", "unknown")
                        vram_total_gb = devices[0].get("vram_total", 0) / 1e9
                        self.log_test(
                            "GPU detected",
                            True,
                            f"{gpu_name}, {vram_total_gb:.1f}GB VRAM"
                        )
                    else:
                        self.log_warning("No GPU detected in ComfyUI")
                    
                    return True
        except (urllib.error.URLError, ConnectionRefusedError, TimeoutError) as e:
            self.log_test(
                "ComfyUI server accessible",
                False,
                f"Cannot connect: {e}"
            )
            return False
    
    def verify_ollama_service(self) -> bool:
        """Check if Ollama is running with required models."""
        print(f"\n{BLUE}=== Checking Ollama Service ==={RESET}")
        
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                models = result.stdout.lower()
                required_models = ["mistral", "llama3"]
                
                found_models = [m for m in required_models if m in models]
                
                if len(found_models) >= 1:
                    self.log_test(
                        "Ollama service running",
                        True,
                        f"Found models: {', '.join(found_models)}"
                    )
                    return True
                else:
                    self.log_test(
                        "Ollama service running",
                        False,
                        "No prompt expansion models found"
                    )
                    return False
            else:
                self.log_test(
                    "Ollama service running",
                    False,
                    "Cannot list models"
                )
                return False
                
        except (FileNotFoundError, subprocess.TimeoutExpired) as e:
            self.log_test(
                "Ollama service running",
                False,
                f"Error: {e}"
            )
            return False
    
    def verify_workflows(self) -> bool:
        """Verify workflows reference FP8 models and not GGUF."""
        print(f"\n{BLUE}=== Checking Workflows ==={RESET}")
        
        if not self.workflows_path.exists():
            self.log_test("Workflows directory", False, "Not found")
            return False
        
        workflow_files = list(self.workflows_path.glob("*.json"))
        
        if not workflow_files:
            self.log_test("Workflow files", False, "No workflows found")
            return False
        
        self.log_test(
            f"Workflow files found",
            True,
            f"{len(workflow_files)} workflows"
        )
        
        # Check for GGUF references
        gguf_workflows = []
        fp8_workflows = []
        
        for workflow_file in workflow_files:
            try:
                with open(workflow_file, 'r') as f:
                    content = f.read()
                    
                    if ".gguf" in content.lower() or "gguf" in content.lower():
                        gguf_workflows.append(workflow_file.name)
                    
                    if "fp8" in content.lower() or "flux1-dev-kontext_fp8" in content:
                        fp8_workflows.append(workflow_file.name)
                        
            except Exception as e:
                self.log_warning(f"Error reading {workflow_file.name}: {e}")
        
        # Report results
        if gguf_workflows:
            self.log_test(
                "Workflows use FP8 (no GGUF)",
                False,
                f"{len(gguf_workflows)} workflows still reference GGUF"
            )
            return False
        else:
            self.log_test(
                "Workflows use FP8 (no GGUF)",
                True,
                f"{len(fp8_workflows)} workflows reference FP8"
            )
            return True
    
    def verify_disk_space(self) -> bool:
        """Check available disk space."""
        print(f"\n{BLUE}=== Checking Disk Space ==={RESET}")
        
        try:
            result = subprocess.run(
                ["df", "-h", str(self.workspace_root)],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) >= 2:
                    parts = lines[1].split()
                    if len(parts) >= 4:
                        available = parts[3]
                        use_percent = parts[4]
                        
                        # Parse available space (e.g., "805G")
                        if 'G' in available:
                            avail_gb = float(available.rstrip('G'))
                            sufficient = avail_gb > 50  # Need at least 50GB
                        elif 'T' in available:
                            sufficient = True  # Over 1TB is definitely enough
                        else:
                            sufficient = False
                        
                        self.log_test(
                            "Disk space available",
                            sufficient,
                            f"{available} free ({use_percent} used)"
                        )
                        return sufficient
            
            self.log_warning("Could not determine disk space")
            return True  # Don't fail on this
            
        except Exception as e:
            self.log_warning(f"Error checking disk space: {e}")
            return True
    
    def print_summary(self):
        """Print overall summary."""
        print(f"\n{BLUE}{'=' * 60}{RESET}")
        print(f"{BLUE}=== FP8 Migration Verification Summary ==={RESET}")
        print(f"{BLUE}{'=' * 60}{RESET}\n")
        
        passed = sum(1 for _, result, _ in self.results if result)
        total = len(self.results)
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"Tests Passed: {passed}/{total} ({pass_rate:.1f}%)")
        
        if self.warnings:
            print(f"\nWarnings: {len(self.warnings)}")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        print()
        
        if pass_rate == 100:
            print(f"{GREEN}✓ All checks passed! FP8 migration successful.{RESET}")
            return 0
        elif pass_rate >= 80:
            print(f"{YELLOW}⚠ Most checks passed with some issues.{RESET}")
            return 1
        else:
            print(f"{RED}✗ Multiple issues detected. Review failures above.{RESET}")
            return 2
    
    def run_all_checks(self) -> int:
        """Run all verification checks."""
        print(f"{BLUE}FP8 Installation Verification{RESET}")
        print(f"Workspace: {self.workspace_root}\n")
        
        # Run all checks
        self.verify_fp8_models()
        self.verify_no_gguf_models()
        self.verify_gguf_custom_node_disabled()
        self.verify_comfyui_running()
        self.verify_ollama_service()
        self.verify_workflows()
        self.verify_disk_space()
        
        return self.print_summary()


def main():
    """Main entry point."""
    workspace_root = Path(__file__).parent.parent
    
    verifier = FP8Verifier(workspace_root)
    exit_code = verifier.run_all_checks()
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()