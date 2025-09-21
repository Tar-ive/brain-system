#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
WHISPER_ROOT="$ROOT_DIR/whisper"
REPO_DIR="$WHISPER_ROOT/whisper.cpp"
MODEL_DIR="$WHISPER_ROOT/models"
REPO_URL="https://github.com/ggerganov/whisper.cpp"

MODEL_URL_DEFAULT="https://ggml.ggerganov.com/ggml-model-whisper-base.en.bin"
MODEL_URL="${WHISPER_MODEL_URL:-$MODEL_URL_DEFAULT}"
MODEL_BASENAME="$(basename "$MODEL_URL")"
MODEL_FILE="$MODEL_DIR/$MODEL_BASENAME"
BINARY_PATH="$REPO_DIR/build/bin/whisper-cli"

mkdir -p "$WHISPER_ROOT" "$MODEL_DIR"

if ! command -v cmake >/dev/null 2>&1; then
  echo "[setup_whisper] Missing dependency: cmake" >&2
  echo "Install via Homebrew: brew install cmake" >&2
  exit 1
fi

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "[setup_whisper] Missing dependency: ffmpeg" >&2
  echo "Install via Homebrew: brew install ffmpeg" >&2
  exit 1
fi

if [ ! -d "$REPO_DIR" ]; then
  echo "[setup_whisper] Cloning whisper.cpp…"
  git clone --depth 1 "$REPO_URL" "$REPO_DIR"
else
  echo "[setup_whisper] Updating whisper.cpp…"
  git -C "$REPO_DIR" pull --ff-only || true
fi

echo "[setup_whisper] Building whisper binary…"
cmake -S "$REPO_DIR" -B "$REPO_DIR/build" -DCMAKE_BUILD_TYPE=Release >/dev/null
cmake --build "$REPO_DIR/build" --target whisper-cli --config Release >/dev/null

if [ ! -f "$MODEL_FILE" ]; then
  echo "[setup_whisper] Downloading model: $MODEL_BASENAME"
  curl -L "$MODEL_URL" -o "$MODEL_FILE"
else
  echo "[setup_whisper] Model already present." 
fi

cat <<MSG

Whisper setup complete.
  Binary : $BINARY_PATH
  Model  : $MODEL_FILE

Set your .env values to:
  WHISPER_BINARY=$BINARY_PATH
  WHISPER_MODEL=$MODEL_FILE
MSG
