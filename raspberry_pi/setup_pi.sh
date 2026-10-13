#!/usr/bin/env bash
# ==============================================================================
# Factory Energy Autopilot — Raspberry Pi 4B Setup & Service Installer
# ==============================================================================
set -e

echo "🏭 Installing Factory Energy Autopilot Telemetry Service on Raspberry Pi..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 1. Ensure user has serial port permissions
if ! groups $USER | grep &>/dev/null '\bdialout\b'; then
    echo "⚠️ Adding user $USER to dialout group for RS-485 USB access..."
    sudo usermod -a -G dialout $USER
    echo "ℹ️ Note: You may need to log out and back in for group permissions to take effect."
fi

# 2. Setup Python Virtual Environment
if [ ! -d ".venv" ]; then
    echo "📦 Creating Python virtual environment in .venv..."
    python3 -m venv .venv
fi

echo "📦 Installing Python dependencies..."
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt

# 3. Environment configuration
if [ ! -f ".env" ]; then
    echo "📝 Copying .env.example to .env..."
    cp .env.example .env
    echo "⚠️ Please edit .env with your backend API URL and Google service account path!"
fi

# 4. Systemd service configuration
SERVICE_FILE="energy-autopilot-telemetry.service"
if [ -f "$SERVICE_FILE" ]; then
    echo "⚙️ Configuring systemd service..."
    sudo cp "$SERVICE_FILE" /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable energy-autopilot-telemetry.service
    echo "✅ Systemd service installed. Start with: sudo systemctl start energy-autopilot-telemetry.service"
fi

echo "=============================================================================="
echo "🎉 Setup complete! You can run the service directly with:"
echo "   $SCRIPT_DIR/.venv/bin/python3 main.py"
echo "Or check systemd service with:"
echo "   sudo systemctl status energy-autopilot-telemetry.service"
echo "=============================================================================="
