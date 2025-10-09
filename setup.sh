#!/usr/bin/env bash
set -euo pipefail

PYTHON=${PYTHON:-python3}
VENV_DIR=${VENV_DIR:-.venv}
REQ_FILE=${REQ_FILE:-requirements.txt}

echo "Using python: $PYTHON"
echo "Virtualenv dir: $VENV_DIR"
echo "Requirements file: $REQ_FILE"

if ! command -v $PYTHON &>/dev/null; then
  echo "Error: $PYTHON not found. Install Python or set PYTHON env variable."
  exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtual environment..."
  $PYTHON -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

python -m pip install --upgrade pip setuptools wheel
if [ -f "$REQ_FILE" ]; then
  echo "Installing from $REQ_FILE..."
  pip install -r "$REQ_FILE"
else
  echo "Warning: $REQ_FILE not found. Nothing to install."
fi

echo "Done. To activate venv: source $VENV_DIR/bin/activate"
