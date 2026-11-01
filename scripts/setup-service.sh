#!/usr/bin/env bash
set -e

# Dynamically resolve current user and repository root directory
CURRENT_USER="$(whoami)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "=========================================="
echo "Configuring pydah-ai systemd service"
echo "  User:      ${CURRENT_USER}"
echo "  Directory: ${PROJECT_DIR}"
echo "=========================================="

mkdir -p "${PROJECT_DIR}/logs"

SERVICE_FILE="/etc/systemd/system/pydah-ai.service"

sudo tee "${SERVICE_FILE}" > /dev/null <<EOF
[Unit]
Description=Pydah AI Central GenAI Engine Service
After=network.target

[Service]
Type=simple
User=${CURRENT_USER}
WorkingDirectory=${PROJECT_DIR}
EnvironmentFile=${PROJECT_DIR}/.env
ExecStart=${PROJECT_DIR}/.venv/bin/uvicorn src.api:app --host 0.0.0.0 --port 8000 --workers 1
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo "==> Reloading systemd daemon..."
sudo systemctl daemon-reload

echo "==> Enabling pydah-ai on system startup..."
sudo systemctl enable pydah-ai

echo "==> Restarting pydah-ai service..."
sudo systemctl restart pydah-ai

echo "==> Checking service status..."
sudo systemctl status pydah-ai --no-pager

