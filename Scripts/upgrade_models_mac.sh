#!/bin/zsh
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
chmod +x "$SCRIPT_DIR"/*.sh 2>/dev/null

echo "========================================"
echo "Model Upgrade Tool (macOS)"
echo "========================================"
echo

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 was not found."
  echo "Please install Python 3 and run this tool again."
  exit 1
fi

download_model() {
  MODEL="$1"
  echo "Downloading model: $MODEL"
  python3 "$SCRIPT_DIR/preload_models.py" "$MODEL"
}

if [ "$#" -gt 0 ]; then
  for arg in "$@"
  do
    case "$arg" in
      -small) download_model "small" ;;
      -medium) download_model "medium" ;;
      -large) download_model "large" ;;
      *) echo "Unknown option: $arg" ;;
    esac
  done
  echo
  echo "Upgrade finished."
  exit 0
fi

echo "Choose model to install:"
echo "1) Fast      (small)"
echo "2) Balanced  (medium)"
echo "3) Accurate  (large)"
echo "4) All Models"
read "choice?Enter choice [1-4]: "

case "$choice" in
  1) download_model "small" ;;
  2) download_model "medium" ;;
  3) download_model "large" ;;
  4)
    download_model "small"
    download_model "medium"
    download_model "large"
    ;;
  *) echo "Invalid choice" ;;
esac

echo
echo "Upgrade finished."
