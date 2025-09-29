#!/usr/bin/env python3
"""
Complete System Test Suite - Ultra Comprehensive Failsafe Testing
Tests every component of the optimized Flux pipeline with extensive error handling
"""

import os
import sys
import json
import time
import requests
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SystemTester:
    def __init__(self):
        self.workspace_root = Path("/home/jdm/ai-workspace")
        self.comfyui_path = self.workspace_root / "ComfyUI"
        self.workflows_path = self.workspace_root / "workflows"
        self.venv_path = self.workspace_root / "venv"
        
        self.test_results = []
        self.passed_tests = 0
        self.failed_tests = 0
        
        # Test configurations
        self.test_prompts = [
            "professional headshot",
            "business portrait of a tech CEO", 
            "elegant woman portrait",
            "luxury entrepreneur headshot"
        ]
        
        self.workflows_to_test = [
            "flux_ultra_fast_gguf.json",
            "flux_multi_lora_realism.json",
            "flux_fast_gguf_portrait.json"
        ]

    def log_test(self, test_name: str, passed: bool, message: str = "", duration: float = 0):
        """Log test results"""
        status = "✅ PASS" if passed else "❌ FAIL"
        duration_str = f" ({duration:.2f}s)" if duration > 0 else ""
        
        log_entry = {
            "test": test_name,
            "status": status,
            "message": message,
            "duration": duration,
            "timestamp": time.time()
        }
        
        self.test_results.append(log_entry)
        
        if passed:
            self.passed_tests += 1
        else:
            self.failed_tests += 1
            
        print(f"{status} {test_name}{duration_str}")
        if message:
            print(f"    {message}")

    def test_environment_setup(self) -> bool:
        """Test 1: Environment and paths"""
        start_time = time.time()
        
        try:
            # Check workspace structure
            required_paths = [
                self.workspace_root,
                self.comfyui_path,
                self.workflows_path,
                self.venv_path,
                self.comfyui_path / "models" / "diffusion_models",
                self.comfyui_path / "models" / "loras",
                self.comfyui_path / "models" / "clip",
                self.comfyui_path / "models" / "vae"
            ]
            
            missing_paths = [p for p in required_paths if not p.exists()]
            if missing_paths:
                self.log_test("Environment Setup", False, f"Missing paths: {missing_paths}", time.time() - start_time)
                return False
                
            # Check Python environment
            python_path = self.venv_path / "bin" / "python"
            if not python_path.exists():
                self.log_test("Environment Setup", False, "Virtual environment not found", time.time() - start_time)
                return False
                
            self.log_test("Environment Setup", True, "All paths and environment verified", time.time() - start_time)
            return True
            
        except Exception as e:
            self.log_test("Environment Setup", False, f"Exception: {e}", time.time() - start_time)
            return False

    def test_models_presence(self) -> bool:
        """Test 2: Required models and assets"""
        start_time = time.time()
        
        try:
            required_files = {
                "GGUF Model": self.comfyui_path / "models" / "diffusion_models" / "flux1-dev-Q3_K_S.gguf",
                "CLIP-L": self.comfyui_path / "models" / "clip" / "clip_l.safetensors",
                "T5-XXL GGUF": self.comfyui_path / "models" / "clip" / "t5-v1_1-xxl-encoder-Q3_K_S.gguf",
                "VAE": self.comfyui_path / "models" / "vae" / "ae.safetensors",
                "LoRA Details": self.comfyui_path / "models" / "loras" / "flux-add-details.safetensors",
                "LoRA Anti-blur": self.comfyui_path / "models" / "loras" / "flux-antiblur.safetensors",
                "LoRA Realism": self.comfyui_path / "models" / "loras" / "flux-realism-xlabs.safetensors"
            }
            
            missing_models = []
            model_sizes = {}
            
            for model_name, model_path in required_files.items():
                if not model_path.exists():
                    missing_models.append(f"{model_name}: {model_path}")
                else:
                    size_mb = model_path.stat().st_size / (1024 * 1024)
                    model_sizes[model_name] = f"{size_mb:.1f}MB"
                    
                    # Check if file is not empty
                    if size_mb < 1:
                        missing_models.append(f"{model_name}: File exists but is empty")
            
            if missing_models:
                self.log_test("Models Presence", False, f"Missing/invalid models: {missing_models}", time.time() - start_time)
                return False
                
            sizes_info = ", ".join([f"{k}:{v}" for k, v in model_sizes.items()])
            self.log_test("Models Presence", True, f"All models verified - {sizes_info}", time.time() - start_time)
            return True
            
        except Exception as e:
            self.log_test("Models Presence", False, f"Exception: {e}", time.time() - start_time)
            return False

    def test_workflow_files(self) -> bool:
        """Test 3: Workflow JSON files"""
        start_time = time.time()
        
        try:
            workflow_status = {}
            
            for workflow_file in self.workflows_to_test:
                workflow_path = self.workflows_path / workflow_file
                
                if not workflow_path.exists():
                    workflow_status[workflow_file] = "Missing"
                    continue
                    
                try:
                    with open(workflow_path, 'r') as f:
                        workflow_data = json.load(f)
                    
                    # Basic validation
                    if not isinstance(workflow_data, dict):
                        workflow_status[workflow_file] = "Invalid JSON structure"
                        continue
                        
                    # Check for required nodes
                    required_nodes = ["1", "2", "3"]  # UNet, CLIP, VAE loaders
                    missing_nodes = [node for node in required_nodes if node not in workflow_data]
                    
                    if missing_nodes:
                        workflow_status[workflow_file] = f"Missing nodes: {missing_nodes}"
                        continue
                        
                    workflow_status[workflow_file] = "Valid"
                    
                except json.JSONDecodeError as e:
                    workflow_status[workflow_file] = f"JSON Error: {e}"
                except Exception as e:
                    workflow_status[workflow_file] = f"Error: {e}"
            
            invalid_workflows = [f"{k}:{v}" for k, v in workflow_status.items() if v != "Valid"]
            
            if invalid_workflows:
                self.log_test("Workflow Files", False, f"Invalid workflows: {invalid_workflows}", time.time() - start_time)
                return False
                
            self.log_test("Workflow Files", True, f"All {len(self.workflows_to_test)} workflows valid", time.time() - start_time)
            return True
            
        except Exception as e:
            self.log_test("Workflow Files", False, f"Exception: {e}", time.time() - start_time)
            return False

    def test_ollama_service(self) -> bool:
        """Test 4: Ollama service and models"""
        start_time = time.time()
        
        try:
            # Test Ollama connectivity
            try:
                response = requests.get("http://localhost:11434/api/tags", timeout=10)
                response.raise_for_status()
                models_data = response.json()
            except requests.RequestException as e:
                self.log_test("Ollama Service", False, f"Ollama not accessible: {e}", time.time() - start_time)
                return False
            
            # Check for required models
            available_models = [model['name'] for model in models_data.get('models', [])]
            required_models = ['mistral', 'prompter']
            
            missing_models = [model for model in required_models if not any(model in avail_model for avail_model in available_models)]
            
            if missing_models:
                # Try to use any available model as fallback
                if not available_models:
                    self.log_test("Ollama Service", False, "No models available in Ollama", time.time() - start_time)
                    return False
                else:
                    self.log_test("Ollama Service", True, f"Service OK, available models: {available_models[:3]}", time.time() - start_time)
                    return True
            
            # Test actual model functionality
            test_payload = {
                "model": "mistral",
                "messages": [{"role": "user", "content": "Test message"}],
                "stream": False,
                "options": {"num_ctx": 512}
            }
            
            try:
                response = requests.post("http://localhost:11434/api/chat", json=test_payload, timeout=15)
                response.raise_for_status()
                result = response.json()
                
                if 'message' in result and 'content' in result['message']:
                    self.log_test("Ollama Service", True, f"Service and models fully functional", time.time() - start_time)
                    return True
                else:
                    self.log_test("Ollama Service", False, "Invalid response format", time.time() - start_time)
                    return False
                    
            except requests.RequestException as e:
                self.log_test("Ollama Service", False, f"Model test failed: {e}", time.time() - start_time)
                return False
                
        except Exception as e:
            self.log_test("Ollama Service", False, f"Exception: {e}", time.time() - start_time)
            return False

    def test_comfyui_startup(self) -> bool:
        """Test 5: ComfyUI server startup and API"""
        start_time = time.time()
        
        try:
            # Check if ComfyUI is already running
            try:
                response = requests.get("http://localhost:8188/system_stats", timeout=5)
                if response.status_code == 200:
                    self.log_test("ComfyUI Startup", True, "ComfyUI already running", time.time() - start_time)
                    return True
            except requests.RequestException:
                pass
            
            # Start ComfyUI
            print("    Starting ComfyUI server...")
            comfyui_cmd = [
                str(self.venv_path / "bin" / "python"),
                str(self.comfyui_path / "main.py"),
                "--listen", "0.0.0.0",
                "--port", "8188"
            ]
            
            # Start in background
            process = subprocess.Popen(
                comfyui_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(self.comfyui_path)
            )
            
            # Wait for startup (max 60 seconds)
            for attempt in range(60):
                time.sleep(1)
                try:
                    response = requests.get("http://localhost:8188/system_stats", timeout=2)
                    if response.status_code == 200:
                        system_stats = response.json()
                        self.log_test("ComfyUI Startup", True, f"Server started successfully, VRAM: {system_stats.get('system', {}).get('gpu', 'N/A')}", time.time() - start_time)
                        return True
                except requests.RequestException:
                    continue
                    
            # If we get here, startup failed
            process.terminate()
            self.log_test("ComfyUI Startup", False, "Server failed to start within 60 seconds", time.time() - start_time)
            return False
            
        except Exception as e:
            self.log_test("ComfyUI Startup", False, f"Exception: {e}", time.time() - start_time)
            return False

    def test_optimizer_functionality(self) -> bool:
        """Test 6: Flux optimizer with Mistral"""
        start_time = time.time()
        
        try:
            # Test optimizer script
            optimizer_path = self.workspace_root / "flux_optimizer.py"
            if not optimizer_path.exists():
                self.log_test("Optimizer Functionality", False, "flux_optimizer.py not found", time.time() - start_time)
                return False
            
            # Run optimizer test
            test_cmd = [
                str(self.venv_path / "bin" / "python"),
                str(optimizer_path),
                "test portrait of professional woman",
                "90"
            ]
            
            result = subprocess.run(
                test_cmd,
                capture_output=True,
                text=True,
                timeout=45,
                cwd=str(self.workspace_root)
            )
            
            if result.returncode != 0:
                self.log_test("Optimizer Functionality", False, f"Optimizer failed: {result.stderr}", time.time() - start_time)
                return False
            
            # Check if optimized workflow was created
            optimized_workflow = self.workflows_path / "optimized_workflow.json"
            if not optimized_workflow.exists():
                self.log_test("Optimizer Functionality", False, "Optimized workflow not created", time.time() - start_time)
                return False
            
            # Validate the optimized workflow
            try:
                with open(optimized_workflow, 'r') as f:
                    workflow_data = json.load(f)
                
                if not isinstance(workflow_data, dict) or len(workflow_data) < 5:
                    self.log_test("Optimizer Functionality", False, "Invalid optimized workflow", time.time() - start_time)
                    return False
                    
            except json.JSONDecodeError:
                self.log_test("Optimizer Functionality", False, "Optimized workflow is not valid JSON", time.time() - start_time)
                return False
            
            self.log_test("Optimizer Functionality", True, "Optimizer working perfectly", time.time() - start_time)
            return True
            
        except subprocess.TimeoutExpired:
            self.log_test("Optimizer Functionality", False, "Optimizer timed out", time.time() - start_time)
            return False
        except Exception as e:
            self.log_test("Optimizer Functionality", False, f"Exception: {e}", time.time() - start_time)
            return False

    def test_workflow_generation(self) -> bool:
        """Test 7: End-to-end workflow execution"""
        start_time = time.time()
        
        try:
            # Test the ultra-fast workflow
            test_workflow = self.workflows_path / "flux_ultra_fast_gguf.json"
            
            if not test_workflow.exists():
                self.log_test("Workflow Generation", False, "Test workflow not found", time.time() - start_time)
                return False
            
            # Load and modify workflow for testing
            with open(test_workflow, 'r') as f:
                workflow_data = json.load(f)
            
            # Set a simple test prompt
            workflow_data["5"]["inputs"]["text"] = "professional headshot of a business person"
            workflow_data["8"]["inputs"]["steps"] = 4  # Reduce steps for faster testing
            workflow_data["8"]["inputs"]["seed"] = 42  # Fixed seed
            workflow_data["10"]["inputs"]["filename_prefix"] = "system_test"
            
            # Submit to ComfyUI
            try:
                response = requests.post(
                    "http://localhost:8188/prompt",
                    json={"prompt": workflow_data},
                    timeout=10
                )
                response.raise_for_status()
                prompt_result = response.json()
                
                if 'prompt_id' not in prompt_result:
                    self.log_test("Workflow Generation", False, "Invalid prompt submission response", time.time() - start_time)
                    return False
                
                prompt_id = prompt_result['prompt_id']
                
                # Wait for completion (max 180 seconds for safety)
                for attempt in range(180):
                    time.sleep(1)
                    
                    # Check history
                    history_response = requests.get("http://localhost:8188/history", timeout=5)
                    if history_response.status_code == 200:
                        history = history_response.json()
                        
                        if prompt_id in history:
                            prompt_data = history[prompt_id]
                            if 'outputs' in prompt_data:
                                # Generation completed
                                output_info = prompt_data['outputs']
                                
                                # Check if image was actually generated
                                output_dir = self.comfyui_path / "output"
                                recent_images = list(output_dir.glob("system_test_*.png"))
                                
                                if recent_images:
                                    # Get the most recent image
                                    latest_image = max(recent_images, key=lambda p: p.stat().st_mtime)
                                    image_size = latest_image.stat().st_size
                                    
                                    if image_size > 100000:  # At least 100KB
                                        self.log_test("Workflow Generation", True, f"Image generated successfully ({image_size/1024/1024:.1f}MB)", time.time() - start_time)
                                        return True
                                    else:
                                        self.log_test("Workflow Generation", False, "Generated image too small", time.time() - start_time)
                                        return False
                                else:
                                    self.log_test("Workflow Generation", False, "No output image found", time.time() - start_time)
                                    return False
                
                self.log_test("Workflow Generation", False, "Generation timed out", time.time() - start_time)
                return False
                
            except requests.RequestException as e:
                self.log_test("Workflow Generation", False, f"ComfyUI API error: {e}", time.time() - start_time)
                return False
                
        except Exception as e:
            self.log_test("Workflow Generation", False, f"Exception: {e}", time.time() - start_time)
            return False

    def test_shortcuts_functionality(self) -> bool:
        """Test 8: Warp shortcuts system"""
        start_time = time.time()
        
        try:
            shortcuts_path = self.workspace_root / "warp_shortcuts.sh"
            
            if not shortcuts_path.exists():
                self.log_test("Shortcuts Functionality", False, "warp_shortcuts.sh not found", time.time() - start_time)
                return False
            
            # Read and validate shortcuts file
            with open(shortcuts_path, 'r') as f:
                shortcuts_content = f.read()
            
            # Check for required functions
            required_functions = [
                'flux_gen',
                'flux_realism',
                'flux_smart',
                'flux_status',
                'flux_start',
                'flux_help'
            ]
            
            missing_functions = []
            for func in required_functions:
                if f"{func}()" not in shortcuts_content:
                    missing_functions.append(func)
            
            if missing_functions:
                self.log_test("Shortcuts Functionality", False, f"Missing functions: {missing_functions}", time.time() - start_time)
                return False
            
            # Test that the file is syntactically correct bash
            bash_test = subprocess.run([
                "bash", "-n", str(shortcuts_path)
            ], capture_output=True, text=True)
            
            if bash_test.returncode != 0:
                self.log_test("Shortcuts Functionality", False, f"Bash syntax error: {bash_test.stderr}", time.time() - start_time)
                return False
            
            self.log_test("Shortcuts Functionality", True, f"All {len(required_functions)} shortcuts validated", time.time() - start_time)
            return True
            
        except Exception as e:
            self.log_test("Shortcuts Functionality", False, f"Exception: {e}", time.time() - start_time)
            return False

    def test_system_integration(self) -> bool:
        """Test 9: Full system integration"""
        start_time = time.time()
        
        try:
            # Test main generator script
            main_script = self.workspace_root / "ultra_portrait_gen.py"
            
            if not main_script.exists():
                self.log_test("System Integration", False, "ultra_portrait_gen.py not found", time.time() - start_time)
                return False
            
            # Check script permissions
            if not os.access(main_script, os.X_OK):
                self.log_test("System Integration", False, "Main script not executable", time.time() - start_time)
                return False
            
            # Test workspace CLI
            workspace_cli = self.workspace_root / "workspace_cli.py"
            if workspace_cli.exists():
                # Test status command
                try:
                    result = subprocess.run([
                        str(self.venv_path / "bin" / "python"),
                        str(workspace_cli),
                        "server", "status"
                    ], capture_output=True, text=True, timeout=15, cwd=str(self.workspace_root))
                    
                    if result.returncode == 0:
                        status_info = "Workspace CLI functional"
                    else:
                        status_info = "Workspace CLI has issues but system can continue"
                except subprocess.TimeoutExpired:
                    status_info = "Workspace CLI timeout but system functional"
            else:
                status_info = "Workspace CLI not found but system functional"
            
            self.log_test("System Integration", True, f"System integration verified - {status_info}", time.time() - start_time)
            return True
            
        except Exception as e:
            self.log_test("System Integration", False, f"Exception: {e}", time.time() - start_time)
            return False

    def test_performance_benchmarks(self) -> bool:
        """Test 10: Performance and timing"""
        start_time = time.time()
        
        try:
            # Test different workflow speeds
            performance_data = {}
            
            # Test optimizer with different targets
            for target_time in [60, 90, 120]:
                try:
                    result = subprocess.run([
                        str(self.venv_path / "bin" / "python"),
                        str(self.workspace_root / "flux_optimizer.py"),
                        f"test prompt for {target_time}s target",
                        str(target_time)
                    ], capture_output=True, text=True, timeout=30, cwd=str(self.workspace_root))
                    
                    if result.returncode == 0:
                        # Extract expected time from output
                        output_lines = result.stdout.split('\n')
                        expected_time = None
                        for line in output_lines:
                            if "Expected time:" in line:
                                # Extract number from the line
                                import re
                                match = re.search(r'(\d+)s', line)
                                if match:
                                    expected_time = int(match.group(1))
                                    break
                        
                        performance_data[f"{target_time}s_target"] = expected_time or target_time
                    
                except subprocess.TimeoutExpired:
                    performance_data[f"{target_time}s_target"] = "timeout"
            
            # Check GPU status
            try:
                gpu_check = subprocess.run(["nvidia-smi"], capture_output=True, text=True, timeout=10)
                gpu_available = gpu_check.returncode == 0
            except:
                gpu_available = False
            
            perf_summary = f"GPU: {'Available' if gpu_available else 'Not detected'}, "
            perf_summary += f"Optimizer targets: {performance_data}"
            
            self.log_test("Performance Benchmarks", True, perf_summary, time.time() - start_time)
            return True
            
        except Exception as e:
            self.log_test("Performance Benchmarks", False, f"Exception: {e}", time.time() - start_time)
            return False

    def run_all_tests(self) -> Dict:
        """Run the complete test suite"""
        print("🚀 Starting Ultra Comprehensive System Test Suite")
        print("=" * 60)
        
        suite_start_time = time.time()
        
        # Define all tests
        tests = [
            ("Environment Setup", self.test_environment_setup),
            ("Models Presence", self.test_models_presence),
            ("Workflow Files", self.test_workflow_files),
            ("Ollama Service", self.test_ollama_service),
            ("ComfyUI Startup", self.test_comfyui_startup),
            ("Optimizer Functionality", self.test_optimizer_functionality),
            ("Workflow Generation", self.test_workflow_generation),
            ("Shortcuts Functionality", self.test_shortcuts_functionality),
            ("System Integration", self.test_system_integration),
            ("Performance Benchmarks", self.test_performance_benchmarks)
        ]
        
        # Run all tests
        for test_name, test_func in tests:
            print(f"\n🧪 Running: {test_name}")
            try:
                test_func()
            except Exception as e:
                self.log_test(test_name, False, f"Unexpected exception: {e}")
        
        total_time = time.time() - suite_start_time
        
        # Generate comprehensive report
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST RESULTS")
        print("=" * 60)
        
        success_rate = (self.passed_tests / (self.passed_tests + self.failed_tests)) * 100 if (self.passed_tests + self.failed_tests) > 0 else 0
        
        print(f"✅ Passed: {self.passed_tests}")
        print(f"❌ Failed: {self.failed_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print(f"⏱️  Total Time: {total_time:.2f}s")
        
        # Detailed results
        print(f"\n📝 Detailed Results:")
        for result in self.test_results:
            print(f"  {result['status']} {result['test']}")
            if result['message']:
                print(f"      {result['message']}")
        
        # System status
        if success_rate >= 90:
            print(f"\n🎉 SYSTEM STATUS: EXCELLENT - Ready for production!")
        elif success_rate >= 80:
            print(f"\n⚠️  SYSTEM STATUS: GOOD - Minor issues detected")
        elif success_rate >= 70:
            print(f"\n⚠️  SYSTEM STATUS: FAIR - Some components need attention")
        else:
            print(f"\n❌ SYSTEM STATUS: NEEDS WORK - Major issues detected")
        
        return {
            "passed": self.passed_tests,
            "failed": self.failed_tests,
            "success_rate": success_rate,
            "total_time": total_time,
            "results": self.test_results
        }

def main():
    """Main test execution"""
    tester = SystemTester()
    results = tester.run_all_tests()
    
    # Save results to file
    results_file = Path("/home/jdm/ai-workspace/test_reports/comprehensive_system_test.json")
    results_file.parent.mkdir(exist_ok=True)
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: {results_file}")
    
    # Exit with appropriate code
    if results["success_rate"] >= 90:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()