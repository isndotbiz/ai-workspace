#!/bin/bash
cd /home/jdm/ai-workspace
source venv/bin/activate
cd ComfyUI
python main.py --listen 0.0.0.0 --port 8188 --enable-cors-header
