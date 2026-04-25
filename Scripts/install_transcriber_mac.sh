#!/bin/zsh

set -e

echo "========================================"
echo "Audio Transcriber Setup (macOS)"
echo "========================================"
echo

# ============================
# Ensure Homebrew
# ============================

if ! command -v brew >/dev/null 2>&1; then
  echo "Homebrew not found."
  echo "Please install Homebrew first:"
  echo '  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
  exit 1
fi

# ============================
# FFmpeg Check & Install
# ============================

echo "Checking FFmpeg..."

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "FFmpeg not found. Installing with Homebrew..."
  brew install ffmpeg

  if ! command -v ffmpeg >/dev/null 2>&1; then
    echo "FFmpeg installation failed."
    exit 1
  fi

  echo "FFmpeg installed successfully."
else
  echo "FFmpeg already installed."
fi

# ffprobe check (should come with ffmpeg)
if ! command -v ffprobe >/dev/null 2>&1; then
  echo "FFprobe not found. Reinstalling FFmpeg..."
  brew reinstall ffmpeg
fi

# ============================
# Python Check
# ============================

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python3 not found."
  echo "Installing Python via Homebrew..."
  brew install python
fi

echo "Upgrading pip and installing dependencies..."
python3 -m pip install --upgrade pip >/dev/null 2>&1
python3 -m pip install --upgrade faster-whisper tqdm huggingface_hub >/dev/null 2>&1

# ============================
# Model Selection
# ============================

echo
echo "Choose model download option:"
echo "1) Fast      (small)"
echo "2) Balanced  (medium)"
echo "3) Accurate  (large)"
echo "4) All Models (larger download)"

read "MODELCHOICE?Enter choice [1-4]: "

echo "This may take several minutes depending on model size."

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

case "$MODELCHOICE" in
  1)
    python3 "$SCRIPT_DIR/preload_models.py" small
    ;;
  2)
    python3 "$SCRIPT_DIR/preload_models.py" medium
    ;;
  3)
    python3 "$SCRIPT_DIR/preload_models.py" large
    ;;
  4)
    python3 "$SCRIPT_DIR/preload_models.py" small medium large
    ;;
  *)
    echo "Invalid choice. Using medium."
    python3 "$SCRIPT_DIR/preload_models.py" medium
    ;;
esac

# ============================
# Initialize Project
# ============================

echo
echo "Initializing project folders..."
python3 "$SCRIPT_DIR/transcribe.py" --init

echo
echo "Installation finished."
echo "You can now run the transcriber."
