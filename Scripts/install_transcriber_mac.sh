#!/bin/zsh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
chmod +x "$SCRIPT_DIR"/*.sh 2>/dev/null

echo "========================================"
echo "Audio Transcriber Setup (macOS)"
echo "========================================"
echo

# ============================
# Homebrew Check
# ============================

if ! command -v brew >/dev/null 2>&1; then
  echo "Homebrew was not found."
  echo "Homebrew is required to install FFmpeg."
  echo

  read "INSTALL_BREW?Do you want to install Homebrew now? [y/N]: "

  if [[ "$INSTALL_BREW" == "y" || "$INSTALL_BREW" == "Y" ]]; then
    echo "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  else
    echo
    echo "Installation cancelled."
    echo "Thank you. Please install Homebrew later from:"
    echo "https://brew.sh"
    exit 0
  fi
fi

# ============================
# FFmpeg Check & Install
# ============================

echo "Checking FFmpeg..."

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "FFmpeg not found. Installing FFmpeg with Homebrew..."
  brew install ffmpeg

  if ! command -v ffmpeg >/dev/null 2>&1; then
    echo
    echo "FFmpeg installation failed or ffmpeg is not available in PATH."
    echo "Please check your Homebrew installation and run this installer again."
    exit 1
  fi

  echo "FFmpeg installed successfully."
else
  echo "FFmpeg already installed."
fi

if ! command -v ffprobe >/dev/null 2>&1; then
  echo
  echo "FFprobe was not found."
  echo "FFprobe is normally installed together with FFmpeg."
  echo "Please run: brew install ffmpeg"
  exit 1
fi

# ============================
# Python Check & Optional Install
# ============================

if ! command -v python3 >/dev/null 2>&1; then
  echo
  echo "Python 3 was not found."
  echo "This program requires Python 3."
  echo

  read "INSTALL_PYTHON?Do you want to install Python 3 with Homebrew now? [y/N]: "

  if [[ "$INSTALL_PYTHON" == "y" || "$INSTALL_PYTHON" == "Y" ]]; then
    echo "Installing Python 3..."
    brew install python

    if ! command -v python3 >/dev/null 2>&1; then
      echo
      echo "Python 3 was installed, but it is not available in this terminal yet."
      echo "Please close this terminal, open a new one, and run this installer again."
      exit 0
    fi
  else
    echo
    echo "Installation cancelled."
    echo "Thank you. Please install Python 3 later, then run this installer again."
    exit 0
  fi
fi

echo "Python 3 found."

# ============================
# Python Dependencies
# ============================

echo "Installing Python dependencies..."
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
echo "Installation finished successfully."
echo "You can now run the transcriber."
