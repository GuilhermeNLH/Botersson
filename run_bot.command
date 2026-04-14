#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo "  Botersson macOS Launcher"
echo "========================================"
echo

if ! command -v python3 >/dev/null 2>&1; then
  echo "[ERROR] python3 not found. Install Python 3.10+ and try again."
  read -r -p "Press Enter to exit..."
  exit 1
fi

if [ ! -f "venv/bin/python" ]; then
  echo "[INFO] Creating virtual environment..."
  python3 -m venv venv
fi

echo "[INFO] Upgrading pip..."
"$SCRIPT_DIR/venv/bin/python" -m pip install --upgrade pip

echo "[INFO] Installing dependencies..."
"$SCRIPT_DIR/venv/bin/python" -m pip install -r requirements.txt

if [ ! -f ".env" ]; then
  echo "[INFO] Creating .env from .env.example..."
  cp .env.example .env
  echo
  echo "[ATTENTION] Set DISCORD_TOKEN in .env before starting."
  echo "File: $SCRIPT_DIR/.env"
  read -r -p "Press Enter to exit..."
  exit 1
fi

if ! command -v ollama >/dev/null 2>&1; then
  echo "[WARN] Ollama not found in PATH."
  echo "Install Ollama from https://ollama.com and run: ollama serve"
else
  if ! curl -fsS "http://localhost:11434/api/tags" >/dev/null 2>&1; then
    echo "[INFO] Starting Ollama in background..."
    nohup ollama serve >/tmp/botersson-ollama.log 2>&1 &
    sleep 1
  else
    echo "[INFO] Ollama is already running."
  fi
fi

echo
echo "[INFO] Starting Botersson..."
"$SCRIPT_DIR/venv/bin/python" run.py
EXIT_CODE=$?

echo
echo "[INFO] Botersson finished with exit code $EXIT_CODE."
read -r -p "Press Enter to close..."
exit "$EXIT_CODE"
