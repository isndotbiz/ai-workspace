#!/usr/bin/env python3
"""
Comprehensive AI Workspace Test Suite
====================================
Thorough testing of all components, dependencies, and functionality.
Ensures system integrity and readiness for production use.
"""

import os
import sys
import json
import time
import subprocess
import requests
from pathlib import Path
import hashlib
import yaml
import torch
from datetime import datetime

# Test configuration
TEST_CONFIG = {
    'timeout_seconds': 300,
    'required_vram_gb': 15,  # RTX 4060 Ti should show ~15GB available
    'min_free_disk_gb': 10,
    'test_image_generation': True,
    'test_api_endpoints': True,
    'validate_model_integrity': True
}

class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    NC = '\033[0m'  # No Color

class TestResults:
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.warnings = 0
        self.start_time = time.time()
        self.results = []
        
    def add_result(self, test_name, status, message, details=None):
        self.tests_run += 1
        result = {
            'test': test_name,
            'status': status,
            'message': message,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.results.append(result)
        
        if status == 'PASS':
            self.tests_passed += 1
            print(f"{Colors.GREEN}✅ PASS{Colors.NC} | {test_name}: {message}")
        elif status == 'FAIL':
            self.tests_failed += 1
            print(f"{Colors.RED}❌ FAIL{Colors.NC} | {test_name}: {message}")
            if details:
                print(f"   {Colors.RED}Details: {details}{Colors.NC}")
        elif status == 'WARN':
            self.warnings += 1
            print(f"{Colors.YELLOW}⚠️  WARN{Colors.NC} | {test_name}: {message}")
        elif status == 'INFO':
            print(f"{Colors.BLUE}ℹ️  INFO{Colors.NC} | {test_name}: {message}")
            
    def generate_report(self):
        duration = time.time() - self.start_time
        return {
            'summary': {
                'total_tests': self.tests_run,
                'passed': self.tests_passed,
                'failed': self.tests_failed,
                'warnings': self.warnings,
                'duration_seconds': round(duration, 2),
                'success_rate': round((self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0, 1)
            },
            'results': self.results,
            'generated_at': datetime.now().isoformat()
        }

def test_environment_setup(results):
    """Test basic environment and directory structure"""
    print(f"\n{Colors.CYAN}=== Environment Setup Tests ==={Colors.NC}")
    
    # Test working directory
    cwd = Path.cwd()
    if cwd.name == 'ai-workspace':
        results.add_result('workspace_directory', 'PASS', f'In correct workspace: {cwd}')
    else:
        results.add_result('workspace_directory', 'FAIL', f'Not in ai-workspace directory: {cwd}')
    
    # Test directory structure
    required_dirs = [
        'venv', 'ComfyUI', 'workflows', 
        'ComfyUI/models', 'ComfyUI/models/checkpoints', 
        'ComfyUI/models/clip', 'ComfyUI/models/vae', 
        'ComfyUI/models/loras', 'ComfyUI/models/unet'
    ]
    
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists() and path.is_dir():
            results.add_result(f'directory_{dir_path.replace("/", "_")}', 'PASS', f'Directory exists: {dir_path}')
        else:
            results.add_result(f'directory_{dir_path.replace("/", "_")}', 'FAIL', f'Missing directory: {dir_path}')
    
    # Test essential files
    required_files = [
        'README.md', 'CHANGELOG.md', 'requirements.txt',
        'activate_workspace.sh', 'sync_to_github.sh',
        '.gitignore'
    ]
    
    for file_path in required_files:
        path = Path(file_path)
        if path.exists() and path.is_file():
            results.add_result(f'file_{file_path.replace(".", "_")}', 'PASS', f'File exists: {file_path}')
        else:
            results.add_result(f'file_{file_path.replace(".", "_")}', 'FAIL', f'Missing file: {file_path}')

def test_system_resources(results):
    """Test system resources and GPU availability"""
    print(f"\n{Colors.CYAN}=== System Resources Tests ==={Colors.NC}")
    
    # Test Python version
    python_version = sys.version_info
    if python_version >= (3, 8):
        results.add_result('python_version', 'PASS', f'Python {python_version.major}.{python_version.minor}.{python_version.micro}')
    else:
        results.add_result('python_version', 'FAIL', f'Python version too old: {python_version}')
    
    # Test disk space
    try:
        disk_usage = os.statvfs('.')
        free_gb = (disk_usage.f_bavail * disk_usage.f_frsize) / (1024**3)
        if free_gb >= TEST_CONFIG['min_free_disk_gb']:
            results.add_result('disk_space', 'PASS', f'{free_gb:.1f}GB free disk space')
        else:
            results.add_result('disk_space', 'WARN', f'Low disk space: {free_gb:.1f}GB')
    except Exception as e:
        results.add_result('disk_space', 'FAIL', f'Could not check disk space: {e}')
    
    # Test CUDA and GPU
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        
        results.add_result('cuda_available', 'PASS', f'CUDA available with {gpu_name}')
        
        if gpu_memory >= TEST_CONFIG['required_vram_gb']:
            results.add_result('gpu_memory', 'PASS', f'{gpu_memory:.1f}GB VRAM available')
        else:
            results.add_result('gpu_memory', 'WARN', f'Limited VRAM: {gpu_memory:.1f}GB')
    else:
        results.add_result('cuda_available', 'FAIL', 'CUDA not available')

def test_python_environment(results):
    """Test Python virtual environment and dependencies"""
    print(f"\n{Colors.CYAN}=== Python Environment Tests ==={Colors.NC}")
    
    # Test virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        results.add_result('virtual_env', 'PASS', 'Running in virtual environment')
    else:
        results.add_result('virtual_env', 'WARN', 'Not in virtual environment')
    
    # Test critical dependencies
    critical_deps = {
        'torch': '2.0.0',
        'torchvision': '0.15.0', 
        'numpy': '1.20.0',
        'requests': '2.25.0',
        'yaml': '5.4.0',
        'safetensors': '0.3.0'
    }
    
    for pkg_name, min_version in critical_deps.items():
        try:
            pkg = __import__(pkg_name)
            if hasattr(pkg, '__version__'):
                version = pkg.__version__
                results.add_result(f'dependency_{pkg_name}', 'PASS', f'{pkg_name} {version}')
            else:
                results.add_result(f'dependency_{pkg_name}', 'PASS', f'{pkg_name} imported successfully')
        except ImportError as e:
            results.add_result(f'dependency_{pkg_name}', 'FAIL', f'Cannot import {pkg_name}: {e}')

def test_model_files(results):
    """Test AI model files integrity and availability"""
    print(f"\n{Colors.CYAN}=== Model Files Tests ==={Colors.NC}")
    
    # Expected model files with sizes (in MB)
    expected_models = {
        'ComfyUI/models/checkpoints/flux1-dev.safetensors': {'min_size': 20000, 'max_size': 25000},
        'ComfyUI/models/unet/flux1-dev.safetensors': {'min_size': 20000, 'max_size': 25000},
        'ComfyUI/models/clip/clip_l.safetensors': {'min_size': 200, 'max_size': 300},
        'ComfyUI/models/clip/t5xxl_fp8_e4m3fn.safetensors': {'min_size': 4000, 'max_size': 5000},
        'ComfyUI/models/vae/ae.safetensors': {'min_size': 300, 'max_size': 400},
        'ComfyUI/models/loras/flux-add-details.safetensors': {'min_size': 600, 'max_size': 700},
        'ComfyUI/models/loras/flux-antiblur.safetensors': {'min_size': 600, 'max_size': 700}
    }
    
    for model_path, size_info in expected_models.items():
        path = Path(model_path)
        if path.exists():
            size_mb = path.stat().st_size / (1024 * 1024)
            if size_info['min_size'] <= size_mb <= size_info['max_size']:
                results.add_result(f'model_{path.name}', 'PASS', f'{path.name}: {size_mb:.1f}MB')
                
                # Test file integrity if requested
                if TEST_CONFIG['validate_model_integrity']:
                    try:
                        # Quick integrity check - can we read the file header?
                        with open(path, 'rb') as f:
                            header = f.read(1024)
                            if len(header) == 1024:
                                results.add_result(f'integrity_{path.name}', 'PASS', f'{path.name} readable')
                            else:
                                results.add_result(f'integrity_{path.name}', 'FAIL', f'{path.name} corrupted')
                    except Exception as e:
                        results.add_result(f'integrity_{path.name}', 'FAIL', f'{path.name} read error: {e}')
            else:
                results.add_result(f'model_{path.name}', 'FAIL', f'{path.name}: Wrong size {size_mb:.1f}MB')
        else:
            results.add_result(f'model_{path.name}', 'FAIL', f'Missing model: {path.name}')

def test_comfyui_server(results):
    """Test ComfyUI server functionality"""
    print(f"\n{Colors.CYAN}=== ComfyUI Server Tests ==={Colors.NC}")
    
    # Check if server is running
    try:
        response = requests.get('http://localhost:8188/system_stats', timeout=5)
        if response.status_code == 200:
            stats = response.json()
            results.add_result('comfyui_server', 'PASS', 'ComfyUI server responding')
            
            # Test system stats
            system_info = stats.get('system', {})
            comfyui_version = system_info.get('comfyui_version', 'unknown')
            pytorch_version = system_info.get('pytorch_version', 'unknown')
            
            results.add_result('comfyui_version', 'INFO', f'ComfyUI {comfyui_version}')
            results.add_result('pytorch_version', 'INFO', f'PyTorch {pytorch_version}')
            
            # Test device info
            devices = stats.get('devices', [])
            if devices:
                device = devices[0]
                device_name = device.get('name', 'unknown')
                vram_total = device.get('vram_total', 0) / (1024**3)
                vram_free = device.get('vram_free', 0) / (1024**3)
                
                results.add_result('gpu_detection', 'PASS', f'GPU detected: {device_name}')
                results.add_result('vram_status', 'PASS', f'VRAM: {vram_free:.1f}GB free / {vram_total:.1f}GB total')
            else:
                results.add_result('gpu_detection', 'FAIL', 'No GPU devices detected by ComfyUI')
        else:
            results.add_result('comfyui_server', 'FAIL', f'Server returned {response.status_code}')
    except requests.exceptions.RequestException as e:
        results.add_result('comfyui_server', 'FAIL', f'Cannot connect to ComfyUI server: {e}')
        return
    
    # Test API endpoints if server is available
    if TEST_CONFIG['test_api_endpoints']:
        api_endpoints = [
            ('/queue', 'Queue API'),
            ('/object_info', 'Object Info API'),
            ('/history', 'History API'),
            ('/system_stats', 'System Stats API')
        ]
        
        for endpoint, description in api_endpoints:
            try:
                response = requests.get(f'http://localhost:8188{endpoint}', timeout=5)
                if response.status_code == 200:
                    results.add_result(f'api_{endpoint.replace("/", "_")}', 'PASS', f'{description} working')
                else:
                    results.add_result(f'api_{endpoint.replace("/", "_")}', 'FAIL', f'{description} returned {response.status_code}')
            except Exception as e:
                results.add_result(f'api_{endpoint.replace("/", "_")}', 'FAIL', f'{description} error: {e}')

def test_model_loading(results):
    """Test model loading in ComfyUI"""
    print(f"\n{Colors.CYAN}=== Model Loading Tests ==={Colors.NC}")
    
    try:
        # Get object info to check available models
        response = requests.get('http://localhost:8188/object_info', timeout=10)
        if response.status_code == 200:
            info = response.json()
            
            # Test UNETLoader
            if 'UNETLoader' in info:
                unet_models = info['UNETLoader']['input']['required']['unet_name'][0]
                if 'flux1-dev.safetensors' in unet_models:
                    results.add_result('unet_model_detection', 'PASS', 'Flux.1-dev UNET model detected')
                else:
                    results.add_result('unet_model_detection', 'FAIL', f'Flux model not in UNET loader: {unet_models}')
            else:
                results.add_result('unet_loader', 'FAIL', 'UNETLoader not available')
            
            # Test DualCLIPLoader
            if 'DualCLIPLoader' in info:
                clip_info = info['DualCLIPLoader']['input']['required']
                clip1_models = clip_info.get('clip_name1', [[], {}])[0]
                clip2_models = clip_info.get('clip_name2', [[], {}])[0]
                
                if 'clip_l.safetensors' in clip1_models and 't5xxl_fp8_e4m3fn.safetensors' in clip2_models:
                    results.add_result('clip_models_detection', 'PASS', 'CLIP models detected')
                else:
                    results.add_result('clip_models_detection', 'FAIL', 'CLIP models not detected')
            
            # Test LoraLoader
            if 'LoraLoader' in info:
                lora_models = info['LoraLoader']['input']['required']['lora_name'][0]
                expected_loras = ['flux-add-details.safetensors', 'flux-antiblur.safetensors']
                found_loras = [lora for lora in expected_loras if lora in lora_models]
                
                if len(found_loras) == len(expected_loras):
                    results.add_result('lora_detection', 'PASS', f'All LoRAs detected: {found_loras}')
                else:
                    missing = set(expected_loras) - set(found_loras)
                    results.add_result('lora_detection', 'FAIL', f'Missing LoRAs: {missing}')
            
            # Test VAELoader
            if 'VAELoader' in info:
                vae_models = info['VAELoader']['input']['required']['vae_name'][0]
                if 'ae.safetensors' in vae_models:
                    results.add_result('vae_detection', 'PASS', 'Flux VAE detected')
                else:
                    results.add_result('vae_detection', 'FAIL', 'Flux VAE not detected')
                    
        else:
            results.add_result('model_loading_api', 'FAIL', f'Cannot get object info: {response.status_code}')
            
    except Exception as e:
        results.add_result('model_loading_test', 'FAIL', f'Model loading test failed: {e}')

def test_image_generation(results):
    """Test actual image generation capability"""
    if not TEST_CONFIG['test_image_generation']:
        results.add_result('image_generation', 'INFO', 'Image generation test skipped by config')
        return
        
    print(f"\n{Colors.CYAN}=== Image Generation Tests ==={Colors.NC}")
    
    # Load working Flux workflow from file and downscale for a quick test
    workflow_path = Path('workflows/luxury_entrepreneur_portrait.json')
    with open(workflow_path, 'r') as f:
        test_workflow = json.load(f)
    
    # Override a few params to make the test faster and smaller if nodes exist
    try:
        if '8' in test_workflow and 'inputs' in test_workflow['8']:
            test_workflow['8']['inputs']['width'] = 512
            test_workflow['8']['inputs']['height'] = 512
        if '9' in test_workflow and 'inputs' in test_workflow['9']:
            test_workflow['9']['inputs']['steps'] = 8
            test_workflow['9']['inputs']['cfg'] = 3.0
    except Exception:
        pass
    
    
    try:
        # Submit test workflow
        payload = {'prompt': test_workflow, 'client_id': 'test_client'}
        response = requests.post('http://localhost:8188/prompt', json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            prompt_id = result['prompt_id']
            results.add_result('workflow_submission', 'PASS', f'Test workflow submitted: {prompt_id}')
            
            # Wait for completion (generous timeout for full Flux generation)
            start_time = time.time()
            timeout = 120  # 2 minutes for test image with LoRAs
            
            while time.time() - start_time < timeout:
                time.sleep(2)
                history_response = requests.get(f'http://localhost:8188/history/{prompt_id}')
                if history_response.status_code == 200:
                    history = history_response.json()
                    if prompt_id in history and history[prompt_id].get('outputs'):
                        elapsed = time.time() - start_time
                        results.add_result('image_generation', 'PASS', f'Test image generated in {elapsed:.1f}s')
                        
                        # Check output file
                        outputs = history[prompt_id]['outputs']
                        for node_id, output in outputs.items():
                            if 'images' in output:
                                for img in output['images']:
                                    img_path = Path('ComfyUI/output') / img['filename']
                                    if img_path.exists():
                                        size_mb = img_path.stat().st_size / (1024 * 1024)
                                        results.add_result('output_file', 'PASS', f'Output file: {img["filename"]} ({size_mb:.2f}MB)')
                                    else:
                                        results.add_result('output_file', 'FAIL', f'Output file not found: {img["filename"]}')
                        break
            else:
                results.add_result('image_generation', 'FAIL', 'Test image generation timed out')
                
        else:
            results.add_result('workflow_submission', 'FAIL', f'Failed to submit workflow: {response.status_code}')
            
    except Exception as e:
        results.add_result('image_generation', 'FAIL', f'Image generation test error: {e}')

def test_git_repository(results):
    """Test Git repository setup and version control"""
    print(f"\n{Colors.CYAN}=== Git Repository Tests ==={Colors.NC}")
    
    # Test if git repo exists
    if Path('.git').exists():
        results.add_result('git_repo', 'PASS', 'Git repository initialized')
    else:
        results.add_result('git_repo', 'FAIL', 'Not a Git repository')
        return
    
    # Test git configuration
    try:
        result = subprocess.run(['git', 'config', 'user.name'], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            results.add_result('git_user_name', 'PASS', f'Git user.name: {result.stdout.strip()}')
        else:
            results.add_result('git_user_name', 'FAIL', 'Git user.name not configured')
            
        result = subprocess.run(['git', 'config', 'user.email'], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            results.add_result('git_user_email', 'PASS', f'Git user.email: {result.stdout.strip()}')
        else:
            results.add_result('git_user_email', 'FAIL', 'Git user.email not configured')
    except Exception as e:
        results.add_result('git_config', 'FAIL', f'Cannot check git config: {e}')
    
    # Test .gitignore
    gitignore_path = Path('.gitignore')
    if gitignore_path.exists():
        with open(gitignore_path, 'r') as f:
            gitignore_content = f.read()
            
        # Check for important exclusions
        important_exclusions = [
            '*.safetensors',
            'venv/',
            'ComfyUI/models/',
            'ComfyUI/output/',
        ]
        
        missing_exclusions = [exc for exc in important_exclusions if exc not in gitignore_content]
        if not missing_exclusions:
            results.add_result('gitignore_content', 'PASS', '.gitignore properly configured')
        else:
            results.add_result('gitignore_content', 'WARN', f'Missing exclusions: {missing_exclusions}')
    else:
        results.add_result('gitignore_file', 'FAIL', '.gitignore file missing')

def test_workspace_scripts(results):
    """Test workspace management scripts"""
    print(f"\n{Colors.CYAN}=== Workspace Scripts Tests ==={Colors.NC}")
    
    scripts_to_test = [
        'activate_workspace.sh',
        'sync_to_github.sh',
        'start_comfyui.sh',
        'test_models.py'
    ]
    
    for script in scripts_to_test:
        script_path = Path(script)
        if script_path.exists():
            # Check if executable
            if os.access(script_path, os.X_OK):
                results.add_result(f'script_{script.replace(".", "_")}', 'PASS', f'{script} exists and executable')
            else:
                results.add_result(f'script_{script.replace(".", "_")}', 'WARN', f'{script} exists but not executable')
        else:
            results.add_result(f'script_{script.replace(".", "_")}', 'FAIL', f'{script} missing')

def main():
    """Run comprehensive test suite"""
    print(f"{Colors.WHITE}🧪 AI Workspace Comprehensive Test Suite{Colors.NC}")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Test configuration: {TEST_CONFIG}")
    print()
    
    results = TestResults()
    
    # Run test suites
    try:
        test_environment_setup(results)
        test_system_resources(results)
        test_python_environment(results)
        test_model_files(results)
        test_comfyui_server(results)
        test_model_loading(results)
        test_image_generation(results)
        test_git_repository(results)
        test_workspace_scripts(results)
        
    except KeyboardInterrupt:
        print(f"\\n{Colors.YELLOW}Test suite interrupted by user{Colors.NC}")
    except Exception as e:
        print(f"\\n{Colors.RED}Test suite crashed: {e}{Colors.NC}")
        results.add_result('test_suite', 'FAIL', f'Test suite crashed: {e}')
    
    # Generate final report
    print(f"\\n{Colors.WHITE}=== TEST RESULTS SUMMARY ==={Colors.NC}")
    report = results.generate_report()
    summary = report['summary']
    
    print(f"Total Tests: {summary['total_tests']}")
    print(f"{Colors.GREEN}Passed: {summary['passed']}{Colors.NC}")
    print(f"{Colors.RED}Failed: {summary['failed']}{Colors.NC}")
    print(f"{Colors.YELLOW}Warnings: {summary['warnings']}{Colors.NC}")
    print(f"Success Rate: {summary['success_rate']}%")
    print(f"Duration: {summary['duration_seconds']}s")
    
    # Save detailed report
    report_path = Path('test_reports') / f"comprehensive_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_path.parent.mkdir(exist_ok=True)
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\\nDetailed report saved: {report_path}")
    
    # Exit with appropriate code
    if summary['failed'] == 0:
        print(f"\\n{Colors.GREEN}🎉 All tests passed! System is ready for production.{Colors.NC}")
        sys.exit(0)
    else:
        print(f"\\n{Colors.RED}⚠️ {summary['failed']} test(s) failed. Please review and fix issues.{Colors.NC}")
        sys.exit(1)

if __name__ == "__main__":
    main()