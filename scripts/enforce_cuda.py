#!/usr/bin/env python3
import torch
import sys

if not torch.cuda.is_available():
    print("❌ CUDA not available!")
    print("This system is configured for CUDA-only operation.")
    print("CPU-only inference is disabled for FP8 efficiency.")
    sys.exit(1)

print("✅ CUDA verified - starting application...")
