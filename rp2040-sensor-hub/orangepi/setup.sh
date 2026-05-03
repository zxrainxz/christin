#!/bin/bash
# Orange Pi Setup Script
# Инициализация окружения для работы с датчиками и Grafana

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_FILE="/var/log/sensor_setup.log"

# Функции логирования
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

error() {
    echo "[ERROR] $1" | tee -a "$LOG_FILE"
    exit 1
}

log "Starting Orange Pi Sensor Hub Setup..."

# Проверить права администратора
if [ "$EUID" -ne 0 ]; then 
    error "This script must be run as root"
fi

# Удалить устаревший репозиторий Grafana от прошлых попыток установки
rm -f /etc/apt/sources.list.d/grafana.list
rm -f /etc/apt/keyrings/grafana-archive-keyring.gpg

# Обновить пакеты
log "Updating system packages..."
apt-get update

# Установить зависимости
log "Installing dependencies..."
apt-get install -y \
    python3 python3-pip python3-venv \
    git curl wget \
    build-essential libssl-dev libffi-dev \
    python3-dev \
    influxdb influxdb-client

# Создать виртуальное окружение
log "Creating Python virtual environment..."
mkdir -p /opt/sensor_hub
python3 -m venv /opt/sensor_hub/venv

# Активировать окружение и установить пакеты
log "Installing Python packages..."
source /opt/sensor_hub/venv/bin/activate
pip install --upgrade pip
pip install \
    pyserial \
    influxdb \
    pyyaml \
    requests

# Создать структуру каталогов
log "Creating directory structure..."
mkdir -p /var/log/sensor_hub
mkdir -p /etc/sensor_hub
mkdir -p /opt/sensor_hub/scripts

# Скопировать скрипты
log "Copying scripts..."
cp "$SCRIPT_DIR/sensor_reader.py" /opt/sensor_hub/scripts/
cp "$SCRIPT_DIR/init_influxdb.py" /opt/sensor_hub/scripts/
cp "$SCRIPT_DIR/init_grafana.py" /opt/sensor_hub/scripts/
cp "$SCRIPT_DIR/install_grafana_influxdb.sh" /opt/sensor_hub/scripts/
chmod +x /opt/sensor_hub/scripts/sensor_reader.py
chmod +x /opt/sensor_hub/scripts/init_influxdb.py
chmod +x /opt/sensor_hub/scripts/init_grafana.py
chmod +x /opt/sensor_hub/scripts/install_grafana_influxdb.sh

# Установить Grafana из официального репозитория
log "Installing Grafana from official repository..."
bash /opt/sensor_hub/scripts/install_grafana_influxdb.sh

# Создать systemd сервис
log "Creating systemd service..."
cp "$SCRIPT_DIR/sensor-reader.service" /etc/systemd/system/sensor-reader.service

systemctl daemon-reload
systemctl enable sensor-reader.service

log "Setup completed successfully!"
log ""
log "Next steps:"
log "1. Initialize InfluxDB: /opt/sensor_hub/venv/bin/python3 /opt/sensor_hub/scripts/init_influxdb.py"
log "2. Initialize Grafana: /opt/sensor_hub/venv/bin/python3 /opt/sensor_hub/scripts/init_grafana.py"
log "3. Start the sensor reader: systemctl start sensor-reader"
log "4. Check logs: journalctl -u sensor-reader -f"
log "5. Access Grafana: http://192.168.0.202:3000"
