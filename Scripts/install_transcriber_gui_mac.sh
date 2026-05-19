#!/bin/bash
# install_transcriber_gui_mac.sh
# Audio Transcriber GUI Installer for macOS (automatic model install)

echo "========================================"
echo "Audio Transcriber GUI Setup (macOS)"
echo "========================================"

PROJECT_DIR=$(pwd)/..

# --- Create required folders ---
mkdir -p "$PROJECT_DIR/Input" "$PROJECT_DIR/Done" "$PROJECT_DIR/Logs" "$PROJECT_DIR/Archive" "$PROJECT_DIR/Assets"

# --- Check Python ---
if ! command -v python3 &> /dev/null
then
    read -p "Python3 is not installed. Install it? [y/N]: " install_python
    if [[ "$install_python" =~ ^[Yy]$ ]]; then
        echo "Installing Python3..."
        brew install python
    else
        echo "Python3 is required. Exiting."
        exit 1
    fi
fi

# --- Check ffmpeg ---
if ! command -v ffmpeg &> /dev/null || ! command -v ffprobe &> /dev/null
then
    read -p "FFmpeg not found. Install via Homebrew? [y/N]: " install_ff
    if [[ "$install_ff" =~ ^[Yy]$ ]]; then
        brew install ffmpeg
    else
        echo "FFmpeg is required. Exiting."
        exit 1
    fi
fi

# --- Python dependencies ---
echo
echo "Installing Python dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install --user faster-whisper tqdm huggingface_hub PyQt5
python3 -m pip install --user PyQt5

# --- Download all models automatically ---
echo
echo "Downloading Whisper models..."
cd "$PROJECT_DIR/Scripts"
python3 preload_models.py small medium large

# --- Create Desktop shortcut ---
DESKTOP=~/Desktop
SHORTCUT="$DESKTOP/Transcribe_GUI.command"
echo
echo "Creating Desktop shortcut..."
cat > "$SHORTCUT" <<EOL
#!/bin/bash
cd "$PROJECT_DIR/Scripts"
python3 transcribe_gui.py
EOL

chmod +x "$SHORTCUT"
echo "Shortcut created: $SHORTCUT"
echo
echo "Installation completed successfully!"
