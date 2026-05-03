#!/bin/bash
# Simplified Orange Pi Setup - Focus on RP2040 data collection
# No Grafana/InfluxDB in this version (install them separately if needed)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_FILE="/var/log/sensor_setup.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

error() {
    echo "[ERROR] $1" | tee -a "$LOG_FILE"
    exit 1
}

log "Starting Orange Pi Sensor Hub Setup (Simplified)..."

# Check root
if [ "$EUID" -ne 0 ]; then 
    error "This script must be run as root"
fi

# Update packages
log "Updating system packages..."
apt-get update -qq
apt-get upgrade -y -qq 2>&1 | grep -v "^Unpacking\|^Setting up" || true

# Install only essential dependencies
log "Installing Python dependencies..."
apt-get install -y -qq \
    python3 python3-pip python3-venv \
    python3-dev \
    git curl wget 2>&1 | grep -E "^(Processing|Setting)" || true

# Create virtual environment
log "Creating Python virtual environment..."
mkdir -p /opt/sensor_hub
python3 -m venv /opt/sensor_hub/venv || true

# Install Python packages
log "Installing Python packages..."
source /opt/sensor_hub/venv/bin/activate
pip install --quiet --upgrade pip setuptools wheel
pip install --quiet \
    pyserial \
    pyyaml \
    requests || true

# Create directory structure
log "Creating directory structure..."
mkdir -p /var/log/sensor_hub
mkdir -p /etc/sensor_hub
mkdir -p /opt/sensor_hub/scripts

# Copy scripts
log "Copying scripts..."
cp "$SCRIPT_DIR/sensor_reader.py" /opt/sensor_hub/scripts/
chmod +x /opt/sensor_hub/scripts/sensor_reader.py

# Create systemd service
log "Creating systemd service..."
cat > /etc/systemd/system/sensor-reader.service << 'EOF'
[Unit]
Description=RP2040 Sensor Reader
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=root
Group=dialout
WorkingDirectory=/opt/sensor_hub
ExecStart=/opt/sensor_hub/venv/bin/python3 /opt/sensor_hub/scripts/sensor_reader.py

Restart=on-failure
RestartSec=10
StartLimitInterval=60s
StartLimitBurst=3

StandardOutput=journal
StandardError=journal
SyslogIdentifier=sensor-reader

Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable sensor-reader.service

log "✓ Basic setup completed!"

# Create summary
cat > /tmp/setup_summary.txt << 'EOF'
╔════════════════════════════════════════════════════════════╗
║        Orange Pi Setup Completed (Simplified)              ║
╚════════════════════════════════════════════════════════════╝

✓ Python environment ready
✓ Sensor reader service configured
✓ Data logging to CSV enabled

NEXT STEPS:
1. Connect RP2040 via USB to Orange Pi
2. Start the sensor reader:
   sudo systemctl start sensor-reader

3. View sensor data:
   tail -f /var/log/sensor_data.csv

4. Check service logs:
   sudo journalctl -u sensor-reader -f

OPTIONAL - Install Grafana for visualization:
1. Add Grafana repository:
   apt-get install -y software-properties-common
   add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"

2. Install Grafana:
   apt-get update
   apt-get install -y grafana-server

3. Install InfluxDB:
   apt-get install -y influxdb

4. Initialize InfluxDB:
   python3 /opt/sensor_hub/scripts/init_influxdb.py

5. Initialize Grafana:
   python3 /opt/sensor_hub/scripts/init_grafana.py

════════════════════════════════════════════════════════════
EOF

cat /tmp/setup_summary.txt
log "Setup log saved to: $LOG_FILE"
