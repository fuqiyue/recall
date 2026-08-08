#!/bin/bash
# Recall CLI 快捷启动脚本 (Linux/macOS)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/scripts/recall.py" "$@"
