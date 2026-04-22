#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-$HOME/e-ink}"
VENV="$PROJECT_DIR/.venv"

cd "$PROJECT_DIR"

echo "==> apt deps"
sudo apt-get update -qq
sudo apt-get install -y --no-install-recommends \
    python3-venv python3-pip \
    python3-numpy python3-pil \
    python3-rpi.gpio python3-spidev python3-smbus \
    fonts-dejavu-core

echo "==> venv at $VENV (with system site-packages so RPi.GPIO is reachable)"
if [ ! -d "$VENV" ]; then
    python3 -m venv --system-site-packages "$VENV"
fi

# shellcheck disable=SC1091
source "$VENV/bin/activate"
pip install --upgrade pip wheel
pip install -e .

echo
echo "==> Done.  Try:"
echo "    source $VENV/bin/activate && eink info && eink hello"
