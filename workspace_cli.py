#!/usr/bin/env python3
"""
AI Workspace CLI Management Tool
===============================
Command-line interface for managing the AI workspace, ComfyUI operations,
model management, and workflow execution.
"""

import os
import sys
import json
import click
import requests
import subprocess
from pathlib import Path
from datetime import datetime
import time

# Configuration
WORKSPACE_DIR = Path.cwd()
COMFYUI_URL = "http://localhost:8188"
MODELS_DIR = WORKSPACE_DIR / "ComfyUI" / "models"
WORKFLOWS_DIR = WORKSPACE_DIR / "workflows"
OUTPUT_DIR = WORKSPACE_DIR / "ComfyUI" / "output"

class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    NC = '\033[0m'

def print_status(message, status='info'):
    """Print colored status messages"""
    colors = {
        'info': Colors.BLUE,
        'success': Colors.GREEN,
        'warning': Colors.YELLOW,
        'error': Colors.RED
    }
    color = colors.get(status, Colors.NC)
    print(f"{color}{message}{Colors.NC}")

def check_comfyui_running():
    """Check if ComfyUI server is running"""
    try:
        response = requests.get(f"{COMFYUI_URL}/system_stats", timeout=5)
        return response.status_code == 200
    except:
        return False

@click.group()
@click.version_option(version='1.0.0')
def cli():
    """AI Workspace CLI - Manage your ComfyUI development environment"""
    pass

@cli.group()
def server():
    """ComfyUI server management commands"""
    pass

@server.command()
@click.option('--port', '-p', default=8188, help='Port to run ComfyUI server on')
@click.option('--background', '-b', is_flag=True, help='Run server in background')
def start(port, background):
    """Start ComfyUI server"""
    if check_comfyui_running():
        print_status("ComfyUI server is already running", 'warning')
        return
    
    print_status(f"Starting ComfyUI server on port {port}...", 'info')
    
    # Activate environment and start server
    cmd = [
        'bash', '-c',
        f'cd {WORKSPACE_DIR} && source venv/bin/activate && '
        f'export CUDA_VISIBLE_DEVICES=0 && '
        f'python ComfyUI/main.py --listen 0.0.0.0 --port {port}'
    ]
    
    if background:
        with open('comfyui_server.log', 'w') as f:
            subprocess.Popen(cmd, stdout=f, stderr=f)
        print_status("ComfyUI server started in background", 'success')
        print_status(f"Check status with: workspace_cli server status", 'info')
    else:
        subprocess.run(cmd)

@server.command()
def stop():
    """Stop ComfyUI server"""
    try:
        result = subprocess.run(['pkill', '-f', 'ComfyUI/main.py'], capture_output=True)
        if result.returncode == 0:
            print_status("ComfyUI server stopped", 'success')
        else:
            print_status("No ComfyUI server process found", 'warning')
    except Exception as e:
        print_status(f"Error stopping server: {e}", 'error')

@server.command()
def status():
    """Check ComfyUI server status"""
    if check_comfyui_running():
        try:
            response = requests.get(f"{COMFYUI_URL}/system_stats")
            stats = response.json()
            system = stats.get('system', {})
            devices = stats.get('devices', [])
            
            print_status("✅ ComfyUI server is running", 'success')
            print(f"   Version: {system.get('comfyui_version', 'unknown')}")
            print(f"   PyTorch: {system.get('pytorch_version', 'unknown')}")
            
            if devices:
                device = devices[0]
                vram_free = device.get('vram_free', 0) / (1024**3)
                vram_total = device.get('vram_total', 0) / (1024**3)
                print(f"   GPU: {device.get('name', 'unknown')}")
                print(f"   VRAM: {vram_free:.1f}GB free / {vram_total:.1f}GB total")
        except Exception as e:
            print_status(f"Server running but error getting details: {e}", 'warning')
    else:
        print_status("❌ ComfyUI server is not running", 'error')

@server.command()
def restart():
    """Restart ComfyUI server"""
    print_status("Restarting ComfyUI server...", 'info')
    stop.invoke(click.Context(stop))
    time.sleep(2)
    start.invoke(click.Context(start), port=8188, background=True)

@cli.group()
def models():
    """Model management commands"""
    pass

@models.command('list')
def models_list():
    """List available models"""
    if not check_comfyui_running():
        print_status("ComfyUI server not running. Start it first.", 'error')
        return
    
    try:
        response = requests.get(f"{COMFYUI_URL}/object_info")
        info = response.json()
        
        print_status("📋 Available Models:", 'info')
        
        # Checkpoints
        if 'CheckpointLoaderSimple' in info:
            checkpoints = info['CheckpointLoaderSimple']['input']['required']['ckpt_name'][0]
            print(f"\n  {Colors.CYAN}Checkpoints:{Colors.NC}")
            for ckpt in checkpoints:
                print(f"    • {ckpt}")
        
        # UNET Models
        if 'UNETLoader' in info:
            unet_models = info['UNETLoader']['input']['required']['unet_name'][0]
            if unet_models:
                print(f"\n  {Colors.CYAN}UNET Models:{Colors.NC}")
                for unet in unet_models:
                    print(f"    • {unet}")
        
        # LoRAs
        if 'LoraLoader' in info:
            loras = info['LoraLoader']['input']['required']['lora_name'][0]
            if loras:
                print(f"\n  {Colors.CYAN}LoRAs:{Colors.NC}")
                for lora in loras:
                    print(f"    • {lora}")
        
        # VAE Models
        if 'VAELoader' in info:
            vaes = info['VAELoader']['input']['required']['vae_name'][0]
            if vaes:
                print(f"\n  {Colors.CYAN}VAE Models:{Colors.NC}")
                for vae in vaes:
                    if vae != 'pixel_space':  # Skip built-in option
                        print(f"    • {vae}")
                        
    except Exception as e:
        print_status(f"Error listing models: {e}", 'error')

@models.command()
def info():
    """Show model file information"""
    print_status("📊 Model File Information:", 'info')
    
    model_dirs = {
        'Checkpoints': MODELS_DIR / 'checkpoints',
        'UNET': MODELS_DIR / 'unet', 
        'CLIP': MODELS_DIR / 'clip',
        'VAE': MODELS_DIR / 'vae',
        'LoRAs': MODELS_DIR / 'loras'
    }
    
    total_size = 0
    for category, path in model_dirs.items():
        if path.exists():
            files = list(path.glob('*.safetensors')) + list(path.glob('*.ckpt'))
            if files:
                print(f"\n  {Colors.CYAN}{category}:{Colors.NC}")
                category_size = 0
                for file in files:
                    if file.name.startswith('put_') or file.stat().st_size == 0:
                        continue
                    size_mb = file.stat().st_size / (1024 * 1024)
                    category_size += size_mb
                    total_size += size_mb
                    print(f"    • {file.name}: {size_mb:.1f}MB")
                if category_size > 0:
                    print(f"    {Colors.YELLOW}Subtotal: {category_size/1024:.1f}GB{Colors.NC}")
    
    print(f"\n  {Colors.GREEN}Total Model Size: {total_size/1024:.1f}GB{Colors.NC}")

@cli.group()
def workflows():
    """Workflow management commands"""
    pass

@workflows.command('list')
def workflows_list():
    """List available workflows"""
    workflow_files = list(WORKFLOWS_DIR.glob('*.json'))
    
    if workflow_files:
        print_status("📋 Available Workflows:", 'info')
        for workflow in sorted(workflow_files):
            size_kb = workflow.stat().st_size / 1024
            print(f"  • {workflow.name} ({size_kb:.1f}KB)")
    else:
        print_status("No workflows found in workflows/ directory", 'warning')

@workflows.command()
@click.argument('workflow_name')
@click.option('--wait', '-w', is_flag=True, help='Wait for completion')
def run(workflow_name, wait):
    """Run a workflow"""
    if not check_comfyui_running():
        print_status("ComfyUI server not running. Start it first.", 'error')
        return
    
    # Find workflow file
    workflow_path = WORKFLOWS_DIR / workflow_name
    if not workflow_path.suffix:
        workflow_path = workflow_path.with_suffix('.json')
    
    if not workflow_path.exists():
        print_status(f"Workflow not found: {workflow_path}", 'error')
        return
    
    try:
        # Load workflow
        with open(workflow_path, 'r') as f:
            workflow_data = json.load(f)
        
        # Submit to ComfyUI
        payload = {
            'prompt': workflow_data,
            'client_id': f'cli_{int(time.time())}'
        }
        
        print_status(f"🚀 Running workflow: {workflow_name}", 'info')
        response = requests.post(f"{COMFYUI_URL}/prompt", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            prompt_id = result['prompt_id']
            print_status(f"✅ Workflow submitted: {prompt_id}", 'success')
            
            if wait:
                print_status("⏳ Waiting for completion...", 'info')
                start_time = time.time()
                
                while time.time() - start_time < 300:  # 5 minute timeout
                    time.sleep(2)
                    history_response = requests.get(f"{COMFYUI_URL}/history/{prompt_id}")
                    if history_response.status_code == 200:
                        history = history_response.json()
                        if prompt_id in history and history[prompt_id].get('outputs'):
                            elapsed = time.time() - start_time
                            print_status(f"✅ Completed in {elapsed:.1f}s", 'success')
                            
                            # Show outputs
                            outputs = history[prompt_id]['outputs']
                            for node_id, output in outputs.items():
                                if 'images' in output:
                                    for img in output['images']:
                                        print(f"   📸 Generated: {img['filename']}")
                            break
                    
                    if time.time() - start_time > 30:  # Show progress every 30s
                        elapsed = time.time() - start_time
                        print_status(f"   Still running... ({elapsed:.0f}s)", 'info')
                else:
                    print_status("⏰ Workflow timed out", 'warning')
        else:
            print_status(f"❌ Failed to submit workflow: {response.status_code}", 'error')
            if response.headers.get('content-type', '').startswith('application/json'):
                error_info = response.json()
                print(f"   Error: {error_info}")
            
    except Exception as e:
        print_status(f"Error running workflow: {e}", 'error')

@workflows.command()
@click.argument('workflow_name')
def validate(workflow_name):
    """Validate a workflow file"""
    workflow_path = WORKFLOWS_DIR / workflow_name
    if not workflow_path.suffix:
        workflow_path = workflow_path.with_suffix('.json')
    
    if not workflow_path.exists():
        print_status(f"Workflow not found: {workflow_path}", 'error')
        return
    
    try:
        with open(workflow_path, 'r') as f:
            workflow_data = json.load(f)
        
        print_status(f"📋 Validating workflow: {workflow_name}", 'info')
        
        # Basic structure validation
        if not isinstance(workflow_data, dict):
            print_status("❌ Workflow must be a JSON object", 'error')
            return
        
        nodes = len(workflow_data)
        print(f"   Nodes: {nodes}")
        
        # Check node structure
        valid_nodes = 0
        for node_id, node_data in workflow_data.items():
            if 'inputs' in node_data and 'class_type' in node_data:
                valid_nodes += 1
            else:
                print_status(f"   ⚠️  Node {node_id} missing required fields", 'warning')
        
        if valid_nodes == nodes:
            print_status("✅ Workflow structure is valid", 'success')
        else:
            print_status(f"⚠️  {nodes - valid_nodes} node(s) have issues", 'warning')
            
    except json.JSONDecodeError as e:
        print_status(f"❌ Invalid JSON: {e}", 'error')
    except Exception as e:
        print_status(f"❌ Validation error: {e}", 'error')

@cli.group()
def test():
    """Testing and validation commands"""
    pass

@test.command()
@click.option('--comprehensive', '-c', is_flag=True, help='Run comprehensive test suite')
@click.option('--quick', '-q', is_flag=True, help='Run quick basic tests only')
def run(comprehensive, quick):
    """Run test suite"""
    if comprehensive:
        print_status("🧪 Running comprehensive test suite...", 'info')
        result = subprocess.run([sys.executable, 'test_comprehensive.py'])
        sys.exit(result.returncode)
    elif quick:
        print_status("⚡ Running quick tests...", 'info')
        result = subprocess.run([sys.executable, 'test_models.py'])
        sys.exit(result.returncode)
    else:
        print_status("🧪 Running basic test suite...", 'info')
        result = subprocess.run([sys.executable, 'test_models.py'])
        sys.exit(result.returncode)

@cli.group()
def git():
    """Git and version control commands"""
    pass

@git.command()
@click.option('--message', '-m', help='Commit message')
def sync(message):
    """Sync workspace to Git (excluding models)"""
    if not message:
        message = f"Workspace sync: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    try:
        result = subprocess.run(['./sync_to_github.sh', message])
        if result.returncode == 0:
            print_status("✅ Workspace synced successfully", 'success')
        else:
            print_status("❌ Sync failed", 'error')
    except Exception as e:
        print_status(f"Error running sync: {e}", 'error')

@git.command()
def status():
    """Show Git repository status"""
    try:
        result = subprocess.run(['git', 'status', '--short'], capture_output=True, text=True)
        if result.stdout.strip():
            print_status("📊 Git Status:", 'info')
            print(result.stdout)
        else:
            print_status("✅ Working tree clean", 'success')
    except Exception as e:
        print_status(f"Error checking Git status: {e}", 'error')

@cli.command()
def init():
    """Initialize/setup the workspace"""
    print_status("🚀 Initializing AI Workspace...", 'info')
    
    # Check if in correct directory
    if not (WORKSPACE_DIR / 'ComfyUI').exists():
        print_status("❌ ComfyUI directory not found. Are you in the ai-workspace directory?", 'error')
        return
    
    # Create necessary directories
    dirs_to_create = [
        'test_reports',
        'backups',
        'exports',
        'ComfyUI/models/unet'  # In case it's missing
    ]
    
    for dir_path in dirs_to_create:
        path = WORKSPACE_DIR / dir_path
        path.mkdir(exist_ok=True)
        print(f"   ✅ Created: {dir_path}")
    
    # Make scripts executable
    scripts = ['activate_workspace.sh', 'sync_to_github.sh', 'start_comfyui.sh', 'test_comprehensive.py', 'workspace_cli.py']
    for script in scripts:
        script_path = WORKSPACE_DIR / script
        if script_path.exists():
            os.chmod(script_path, 0o755)
            print(f"   ✅ Made executable: {script}")
    
    print_status("✅ Workspace initialization complete!", 'success')

@cli.command()
def info():
    """Show workspace information"""
    print_status("📊 AI Workspace Information", 'info')
    print(f"   Directory: {WORKSPACE_DIR}")
    print(f"   ComfyUI: {'✅ Found' if (WORKSPACE_DIR / 'ComfyUI').exists() else '❌ Not found'}")
    print(f"   Virtual Environment: {'✅ Found' if (WORKSPACE_DIR / 'venv').exists() else '❌ Not found'}")
    print(f"   Git Repository: {'✅ Yes' if (WORKSPACE_DIR / '.git').exists() else '❌ No'}")
    
    # Check workflows
    workflows_count = len(list(WORKFLOWS_DIR.glob('*.json')))
    print(f"   Workflows: {workflows_count} available")
    
    # Check models
    total_models = 0
    for model_dir in ['checkpoints', 'unet', 'clip', 'vae', 'loras']:
        path = MODELS_DIR / model_dir
        if path.exists():
            models = [f for f in path.glob('*.safetensors') if not f.name.startswith('put_')]
            total_models += len(models)
    
    print(f"   Models: {total_models} installed")
    
    # Check server status
    server_status = "🟢 Running" if check_comfyui_running() else "🔴 Stopped"
    print(f"   ComfyUI Server: {server_status}")

if __name__ == '__main__':
    cli()