#!/bin/zsh
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
chmod +x "$SCRIPT_DIR"/*.sh 2>/dev/null

echo "========================================"
echo "Audio Transcriber Setup (macOS)"
echo "========================================"
echo

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 was not found."
  echo "Please install Python 3 and run this installer again."
  exit 1
fi

if ! command -v brew >/dev/null 2>&1; then
  echo "Homebrew was not found."
  echo "Please install Homebrew from https://brew.sh and run this installer again."
  exit 1
fi

echo "Checking FFmpeg..."
brew install ffmpeg >/dev/null 2>&1

echo "Installing Python dependencies..."
python3 -m pip install --upgrade pip >/dev/null 2>&1
python3 -m pip install --upgrade faster-whisper tqdm huggingface_hub >/dev/null 2>&1

echo
echo "Choose model download option:"
echo "1) Fast      (small)"
echo "2) Balanced  (medium)"
echo "3) Accurate  (large)"
echo "4) All Models (larger download)"
read "MODELCHOICE?Enter choice [1-4]: "

if [[ "$MODELCHOICE" == "1" ]]; then
  python3 "$SCRIPT_DIR/preload_models.py" small
elif [[ "$MODELCHOICE" == "2" ]]; then
  python3 "$SCRIPT_DIR/preload_models.py" medium
elif [[ "$MODELCHOICE" == "3" ]]; then
  python3 "$SCRIPT_DIR/preload_models.py" large
elif [[ "$MODELCHOICE" == "4" ]]; then
  python3 "$SCRIPT_DIR/preload_models.py" small medium large
else
  echo "Invalid choice. Using medium."
  python3 "$SCRIPT_DIR/preload_models.py" medium
fi

echo
echo "Initializing project folders..."
python3 "$SCRIPT_DIR/transcribe.py" --init

echo
echo "Installation finished."
