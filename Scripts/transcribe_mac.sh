#!/bin/zsh
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
chmod +x "$SCRIPT_DIR"/*.sh 2>/dev/null
python3 "$SCRIPT_DIR/transcribe.py" "$@"
