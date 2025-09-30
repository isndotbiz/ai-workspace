#!/usr/bin/env python3
"""
Convert ComfyUI workflows from GGUF to FP8 model references.

This script updates workflow JSON files to replace:
- UnetLoaderGGUF → UNETLoader with FP8 models
- DualCLIPLoaderGGUF → DualCLIPLoader with FP8 T5
- GGUF model file references → FP8 safetensors files
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any

# Define model replacements
MODEL_REPLACEMENTS = {
    # GGUF UNet → FP8 UNet
    "flux1-dev-Q3_K_S.gguf": "flux1-dev-kontext_fp8_scaled.safetensors",
    "flux1-dev-Q4_K_S.gguf": "flux1-dev-kontext_fp8_scaled.safetensors",
    "flux1-dev-Q5_K_S.gguf": "flux1-dev-kontext_fp8_scaled.safetensors",
    "flux1-dev-Q6_K.gguf": "flux1-dev-kontext_fp8_scaled.safetensors",
    "flux1-dev-Q8_0.gguf": "flux1-dev-kontext_fp8_scaled.safetensors",
    
    # GGUF T5 → FP8 T5
    "t5-v1_1-xxl-encoder-Q3_K_S.gguf": "t5xxl_fp8_e4m3fn.safetensors",
    "t5-v1_1-xxl-encoder-Q4_K_S.gguf": "t5xxl_fp8_e4m3fn.safetensors",
    "t5-v1_1-xxl-encoder-Q5_K_S.gguf": "t5xxl_fp8_e4m3fn.safetensors",
    "t5xxl-Q3_K_S.gguf": "t5xxl_fp8_e4m3fn.safetensors",
}

# Node class type replacements
CLASS_TYPE_REPLACEMENTS = {
    "UnetLoaderGGUF": "UNETLoader",
    "DualCLIPLoaderGGUF": "DualCLIPLoader",
}


def convert_workflow(workflow_data: Dict[str, Any]) -> tuple[Dict[str, Any], bool]:
    """
    Convert a workflow from GGUF to FP8 models.
    
    Returns:
        Tuple of (converted_workflow, was_modified)
    """
    modified = False
    
    for node_id, node_data in workflow_data.items():
        if not isinstance(node_data, dict):
            continue
            
        # Check and replace class_type
        class_type = node_data.get("class_type", "")
        if class_type in CLASS_TYPE_REPLACEMENTS:
            node_data["class_type"] = CLASS_TYPE_REPLACEMENTS[class_type]
            modified = True
            
            # Update title metadata if it references GGUF
            if "_meta" in node_data and "title" in node_data["_meta"]:
                title = node_data["_meta"]["title"]
                if "GGUF" in title:
                    node_data["_meta"]["title"] = title.replace("GGUF", "FP8")
                    modified = True
        
        # Convert UnetLoaderGGUF → UNETLoader with FP8 settings
        if class_type == "UnetLoaderGGUF" or node_data.get("class_type") == "UNETLoader":
            inputs = node_data.get("inputs", {})
            
            # Replace GGUF unet model references
            if "unet_name" in inputs:
                old_model = inputs["unet_name"]
                if old_model in MODEL_REPLACEMENTS:
                    inputs["unet_name"] = MODEL_REPLACEMENTS[old_model]
                    modified = True
                elif ".gguf" in old_model.lower():
                    # Generic GGUF fallback
                    inputs["unet_name"] = "flux1-dev-kontext_fp8_scaled.safetensors"
                    modified = True
            
            # Add weight_dtype for FP8 if using UNETLoader
            if node_data.get("class_type") == "UNETLoader":
                if "weight_dtype" not in inputs:
                    inputs["weight_dtype"] = "fp8_e4m3fn"
                    modified = True
        
        # Convert DualCLIPLoaderGGUF → DualCLIPLoader
        if class_type == "DualCLIPLoaderGGUF" or node_data.get("class_type") == "DualCLIPLoader":
            inputs = node_data.get("inputs", {})
            
            # Replace GGUF CLIP models
            for key in ["clip_name1", "clip_name2"]:
                if key in inputs:
                    old_model = inputs[key]
                    if old_model in MODEL_REPLACEMENTS:
                        inputs[key] = MODEL_REPLACEMENTS[old_model]
                        modified = True
                    elif ".gguf" in old_model.lower() and "t5" in old_model.lower():
                        inputs[key] = "t5xxl_fp8_e4m3fn.safetensors"
                        modified = True
    
    return workflow_data, modified


def process_workflow_file(filepath: Path, dry_run: bool = False) -> bool:
    """
    Process a single workflow file.
    
    Returns:
        True if file was modified, False otherwise
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            workflow_data = json.load(f)
        
        converted_data, was_modified = convert_workflow(workflow_data)
        
        if was_modified:
            if dry_run:
                print(f"[DRY RUN] Would modify: {filepath.name}")
            else:
                # Backup original
                backup_path = filepath.with_suffix('.json.gguf_backup')
                if not backup_path.exists():
                    with open(backup_path, 'w', encoding='utf-8') as f:
                        json.dump(workflow_data, f, indent=2)
                
                # Write converted workflow
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(converted_data, f, indent=2)
                
                print(f"✓ Converted: {filepath.name}")
            return True
        else:
            print(f"- Skipped (no GGUF references): {filepath.name}")
            return False
            
    except Exception as e:
        print(f"✗ Error processing {filepath.name}: {e}", file=sys.stderr)
        return False


def main():
    """Main conversion function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Convert ComfyUI workflows from GGUF to FP8 models"
    )
    parser.add_argument(
        "workflows_dir",
        type=Path,
        nargs="?",
        default=Path(__file__).parent.parent / "workflows",
        help="Directory containing workflow JSON files (default: ../workflows)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without modifying files"
    )
    parser.add_argument(
        "--file",
        type=Path,
        help="Convert a specific workflow file instead of entire directory"
    )
    
    args = parser.parse_args()
    
    if args.file:
        # Process single file
        if not args.file.exists():
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            sys.exit(1)
        
        modified = process_workflow_file(args.file, dry_run=args.dry_run)
        sys.exit(0 if modified else 1)
    
    # Process directory
    workflows_dir = args.workflows_dir
    if not workflows_dir.exists():
        print(f"Error: Directory not found: {workflows_dir}", file=sys.stderr)
        sys.exit(1)
    
    # Find all JSON workflow files
    workflow_files = sorted(workflows_dir.glob("*.json"))
    
    if not workflow_files:
        print(f"No workflow files found in {workflows_dir}")
        sys.exit(0)
    
    print(f"\nFound {len(workflow_files)} workflow files")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE CONVERSION'}\n")
    
    modified_count = 0
    for filepath in workflow_files:
        if process_workflow_file(filepath, dry_run=args.dry_run):
            modified_count += 1
    
    print(f"\nSummary: {modified_count}/{len(workflow_files)} workflows modified")
    
    if args.dry_run:
        print("\nThis was a dry run. Run without --dry-run to apply changes.")
    else:
        print("\nBackups saved with .gguf_backup extension")
        print("Original GGUF models archived in archives/gguf_rollback/")


if __name__ == "__main__":
    main()