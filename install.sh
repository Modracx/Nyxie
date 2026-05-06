#!/usr/bin/env bash
# Usage: cd /var/www/project/nyxie/Nyxie && bash install.sh [--enable-service]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_DIR="$SCRIPT_DIR/nyxie_venv"
LEGACY_VENV_DIR="$SCRIPT_DIR/venv"
BIN_DIR="$HOME/.local/bin"
SYSTEMD_DIR="$HOME/.config/systemd/user"
MODEL_FILE="$ROOT_DIR/piper_models/en_GB-cori-high.onnx"
CONFIG_FILE="$ROOT_DIR/piper_models/en_GB-cori-high.onnx.json"
PYTHON_BIN="${PYTHON_BIN:-python3}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    echo "python3 is required but was not found."
    exit 1
fi

if [[ ! -f "$MODEL_FILE" || ! -f "$CONFIG_FILE" ]]; then
    echo "Missing Piper voice model files."
    echo "Expected:"
    echo "  $MODEL_FILE"
    echo "  $CONFIG_FILE"
    exit 1
fi

mkdir -p "$BIN_DIR"

if [[ ! -d "$VENV_DIR" && -d "$LEGACY_VENV_DIR" ]]; then
    echo "Renaming existing virtual environment to $VENV_DIR"
    mv "$LEGACY_VENV_DIR" "$VENV_DIR"
fi

if [[ ! -d "$VENV_DIR" ]]; then
    echo "Creating virtual environment at $VENV_DIR"
    "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

echo "Installing Python dependencies"
"$VENV_DIR/bin/python" -m pip install --upgrade pip
"$VENV_DIR/bin/pip" install piper-tts SpeechRecognition

if "$VENV_DIR/bin/pip" install PyAudio; then
    echo "PyAudio installed. Microphone input should be available."
else
    echo "PyAudio could not be installed."
    echo "Nyxie will still run, but microphone input will fall back unless PortAudio headers are installed."
    echo "On Ubuntu, install:"
    echo "  sudo apt install portaudio19-dev"
fi

python_launcher="#!/usr/bin/env bash
exec \"$VENV_DIR/bin/python\" \"$SCRIPT_DIR/assistant.py\" \"\$@\""
printf '%s\n' "$python_launcher" > "$BIN_DIR/nyxie-assistant"
chmod +x "$BIN_DIR/nyxie-assistant"

echo "Launcher installed at $BIN_DIR/nyxie-assistant"

if ! "$VENV_DIR/bin/python" -c "import speech_recognition" >/dev/null 2>&1; then
    echo "SpeechRecognition did not install correctly."
fi

if ! "$VENV_DIR/bin/python" -c "import piper" >/dev/null 2>&1; then
    echo "Piper Python package is not available in the venv."
fi

if ! "$PYTHON_BIN" -c "import gi" >/dev/null 2>&1; then
    echo "GTK4 Python bindings are missing for the splash screen."
    echo "Install them with:"
    echo "  sudo apt install python3-gi gir1.2-gtk-4.0"
fi

if ! command -v pw-play >/dev/null 2>&1 && ! command -v paplay >/dev/null 2>&1 && ! command -v aplay >/dev/null 2>&1 && ! command -v play >/dev/null 2>&1; then
    echo "No audio playback tool was found."
    echo "Install one of these packages on Ubuntu:"
    echo "  sudo apt install pipewire-bin"
    echo "  sudo apt install alsa-utils"
    echo "  sudo apt install sox"
fi

if [[ "${1:-}" == "--enable-service" ]]; then
    mkdir -p "$SYSTEMD_DIR"
    service_file="[Unit]
Description=Nyxie Ubuntu voice assistant
After=graphical-session.target

[Service]
Type=simple
ExecStart=$VENV_DIR/bin/python $SCRIPT_DIR/assistant.py
Restart=on-failure
RestartSec=5
Environment=DISPLAY=:0

[Install]
WantedBy=default.target"
    printf '%s\n' "$service_file" > "$SYSTEMD_DIR/nyxie.service"
    systemctl --user daemon-reload
    systemctl --user enable nyxie.service
    echo "Enabled user service nyxie.service"
fi

echo "Install complete."
echo "Run: nyxie-assistant"
