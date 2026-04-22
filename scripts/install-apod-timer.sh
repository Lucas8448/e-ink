#!/usr/bin/env bash
# Install the daily APOD systemd timer on the Pi.
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-$HOME/e-ink}"

sudo install -m 0644 "$PROJECT_DIR/systemd/eink-apod.service" /etc/systemd/system/eink-apod.service
sudo install -m 0644 "$PROJECT_DIR/systemd/eink-apod.timer"   /etc/systemd/system/eink-apod.timer
sudo systemctl daemon-reload
sudo systemctl enable --now eink-apod.timer

echo
systemctl list-timers eink-apod.timer --no-pager
echo
echo "==> To run once now:  sudo systemctl start eink-apod.service"
echo "==> Logs:              journalctl -u eink-apod.service -f"
echo "==> For a personal NASA key, write KEY=... to $PROJECT_DIR/.env as:"
echo "    NASA_API_KEY=your_key_here"
