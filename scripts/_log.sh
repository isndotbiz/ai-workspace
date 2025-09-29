#!/usr/bin/env bash
LOG=~/ai-workspace/setup-history.log
stamp(){ date '+%Y-%m-%d %H:%M:%S'; }
note(){ echo "[$(stamp)] $*" | tee -a "$LOG"; }