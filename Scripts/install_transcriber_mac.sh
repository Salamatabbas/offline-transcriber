#!/bin/zsh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
chmod +x "$SCRIPT_DIR"/*.sh 2>/dev/null

echo
echo "=================================================="
echo "       Audio Transcriber Setup for macOS"
echo "=================================================="
echo
echo "This installer will prepare:"
echo "  - FFmpeg"
echo "  - Python dependencies"
echo "  - Transcription model files"
echo
echo "Please keep this window open until setup finishes."
echo

echo "[1/4] Checking Homebrew..."

if ! command -v brew >/dev/null 2>&1; then
  echo
  echo "ERROR: Homebrew was not found."
  echo "Please install Homebrew first:"
  echo
  echo '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
  echo
  exit 1
fi

echo "     Homebrew OK."

echo
echo "[2/4] Checking FFmpeg..."

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "     FFmpeg not found. Installing FFmpeg..."
  brew install ffmpeg >/dev/null 2>&1

  if ! command -v ffmpeg >/dev/null 2>&1; then
    echo
    echo "ERROR: FFmpeg installation failed."
    echo "Please check Homebrew and try again."
    echo
    exit 1
  fi

  echo "     FFmpeg installed successfully."
else
  echo "     FFmpeg already installed."
fi

if ! command -v ffprobe >/dev/null 2>&1; then
  echo
  echo "ERROR: FFprobe was not found."
  echo "FFprobe is normally installed together with FFmpeg."
  echo "Please run: brew install ffmpeg"
  echo
  exit 1
fi

echo
echo "[3/4] Checking Python..."

if ! command -v python3 >/dev/null 2>&1; then
  echo "     Python3 not found. Installing Python..."
  brew install python >/dev/null 2>&1

  if ! command -v python3 >/dev/null 2>&1; then
    echo
    echo "ERROR: Python installation failed."
    echo "Please install Python manually and run this installer again."
    echo
    exit 1
  fi
fi

echo "     Python OK."

echo
echo "     Installing Python dependencies. Please wait..."

python3 -m ensurepip --upgrade >/dev/null 2>&1 || true
python3 -m pip install --upgrade pip >/dev/null 2>&1
python3 -m pip install --upgrade faster-whisper tqdm huggingface_hub >/dev/null 2>&1

echo "     Dependencies installed successfully."
<<<<<<< HEAD

echo
echo "[4/4] Choose transcription model:"
echo
echo "  1) Fast      - small"
echo "  2) Balanced  - medium"
echo "  3) Accurate  - large"
echo "  4) All Models"
echo "  5) I already have the models - skip model download"
echo

read "MODELCHOICE?Enter choice [1-5]: "

echo
=======

echo
echo "[4/4] Choose transcription model:"
echo
echo "  1) Fast      - small"
echo "  2) Balanced  - medium"
echo "  3) Accurate  - large"
echo "  4) All Models"
echo

read "MODELCHOICE?Enter choice [1-4]: "

echo
>>>>>>> cd71e1c2dded91ecd666e7375fbb0333ca2b7dff
echo "     Downloading selected model(s)."
echo "     This may take several minutes. Please wait..."

case "$MODELCHOICE" in
  1)
    python3 "$SCRIPT_DIR/preload_models.py" small >/dev/null 2>&1
    ;;
  2)
    python3 "$SCRIPT_DIR/preload_models.py" medium >/dev/null 2>&1
    ;;
  3)
    python3 "$SCRIPT_DIR/preload_models.py" large >/dev/null 2>&1
    ;;
  4)
    python3 "$SCRIPT_DIR/preload_models.py" small medium large >/dev/null 2>&1
    ;;
<<<<<<< HEAD
  5)
    echo "     Model download skipped."
    ;;
=======
>>>>>>> cd71e1c2dded91ecd666e7375fbb0333ca2b7dff
  *)
    echo "     Invalid choice. Using medium model."
    python3 "$SCRIPT_DIR/preload_models.py" medium >/dev/null 2>&1
    ;;
esac

echo "     Model setup completed."
<<<<<<< HEAD

echo
echo "     Initializing project folders..."

python3 "$SCRIPT_DIR/transcribe.py" --init >/dev/null 2>&1



echo
echo "Creating Desktop launcher..."

PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
DESKTOP_DIR="$HOME/Desktop"
APP_DIR="$DESKTOP_DIR/Transcribe.app"
APP_CONTENTS="$APP_DIR/Contents"
APP_MACOS="$APP_CONTENTS/MacOS"
APP_RESOURCES="$APP_CONTENTS/Resources"

# Clean old fallback launcher from previous versions.
rm -f "$DESKTOP_DIR/Transcribe.command"
rm -rf "$APP_DIR"

mkdir -p "$APP_MACOS" "$APP_RESOURCES"

if [ -f "$PROJECT_DIR/Assets/transcribe.icns" ]; then
  cp "$PROJECT_DIR/Assets/transcribe.icns" "$APP_RESOURCES/transcribe.icns"
fi

cat > "$APP_CONTENTS/Info.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleName</key>
  <string>Transcribe</string>
  <key>CFBundleDisplayName</key>
  <string>Transcribe</string>
  <key>CFBundleIdentifier</key>
  <string>local.offline-transcriber.launcher</string>
  <key>CFBundleVersion</key>
  <string>1.3.3</string>
  <key>CFBundleExecutable</key>
  <string>Transcribe</string>
  <key>CFBundleIconFile</key>
  <string>transcribe</string>
</dict>
</plist>
EOF

cat > "$APP_MACOS/Transcribe" <<EOF
#!/bin/zsh
/usr/bin/osascript <<APPLESCRIPT
tell application "Terminal"
  activate
  do script "cd \\"$SCRIPT_DIR\\"; clear; echo '=================================================='; echo '       Offline Transcriber'; echo '=================================================='; echo ''; echo 'Put your audio files in:'; echo '  $PROJECT_DIR/Input'; echo ''; echo 'Common commands:'; echo ''; echo '  ./transcribe_mac.sh'; echo '  ./transcribe_mac.sh -single audio.mp3'; echo '  ./transcribe_mac.sh -single audio.mp3 -translate'; echo '  ./transcribe_mac.sh -single audio.mp3 -srt'; echo '  ./transcribe_mac.sh -large'; echo ''; echo 'You are now in the Scripts folder.'; echo 'Type a command above and press Enter.'; echo ''"
end tell
APPLESCRIPT
EOF

chmod +x "$APP_MACOS/Transcribe"

echo "Desktop launcher created: Transcribe.app"
=======

echo
echo "     Initializing project folders..."

python3 "$SCRIPT_DIR/transcribe.py" --init >/dev/null 2>&1
>>>>>>> cd71e1c2dded91ecd666e7375fbb0333ca2b7dff

echo
echo "=================================================="
echo "       Installation completed"
echo "       Setup is ready to use"
echo "       Enjoy transcribing!"
echo "=================================================="
echo
echo "You can now place audio files in the Input folder"
echo "and run:"
echo
echo "  ./transcribe_mac.sh"
echo
