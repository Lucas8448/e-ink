#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-$HOME/e-ink}"

if [ -d "$PROJECT_DIR/.venv" ]; then
    echo "==> Removing venv $PROJECT_DIR/.venv"
    rm -rf "$PROJECT_DIR/.venv"
fi

if [ -f /etc/systemd/system/eink.service ]; then
    sudo systemctl disable --now eink.service || true
    sudo rm -f /etc/systemd/system/eink.service
    sudo systemctl daemon-reload
fi

echo "==> Done. Project files at $PROJECT_DIR were left in place."
