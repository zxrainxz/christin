#!/bin/bash
# Deploy to Orange Pi
# Загрузка и настройка на Orange Pi 4 LTS

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Параметры подключения
ORANGEPI_HOST="${1:-192.168.0.202}"
ORANGEPI_USER="${2:-root}"
ORANGEPI_PASSWORD="${3:-mxbjtjud6s}"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║       Orange Pi Sensor Hub Deployment                      ║"
echo "╚════════════════════════════════════════════════════════════╝"

echo ""
echo "🔌 Connecting to Orange Pi..."
echo "   Host: $ORANGEPI_HOST"
echo "   User: $ORANGEPI_USER"

# Проверить SSH доступ
if ! ssh -o ConnectTimeout=5 "$ORANGEPI_USER@$ORANGEPI_HOST" exit 2>/dev/null; then
    echo "❌ Cannot connect to Orange Pi at $ORANGEPI_HOST"
    echo ""
    echo "Usage: $0 [HOST] [USER] [PASSWORD]"
    echo "Default: $0 192.168.0.202 root mxbjtjud6s"
    exit 1
fi

echo "✓ SSH connection successful"

# Создать директорию на Orange Pi
echo ""
echo "📁 Creating project directory..."
ssh "$ORANGEPI_USER@$ORANGEPI_HOST" "mkdir -p /opt/sensor_hub/{scripts,config}"

# Загрузить файлы
echo ""
echo "📤 Uploading files..."
scp -r "$PROJECT_DIR/orangepi/" "$ORANGEPI_USER@$ORANGEPI_HOST:/opt/sensor_hub/"
scp "$PROJECT_DIR/README.md" "$ORANGEPI_USER@$ORANGEPI_HOST:/opt/sensor_hub/"
scp -r "$PROJECT_DIR/docs/" "$ORANGEPI_USER@$ORANGEPI_HOST:/opt/sensor_hub/"

echo "✓ Files uploaded"

# Сделать скрипты исполняемыми
echo ""
echo "🔐 Setting permissions..."
ssh "$ORANGEPI_USER@$ORANGEPI_HOST" << 'EOF'
chmod +x /opt/sensor_hub/orangepi/*.sh
chmod +x /opt/sensor_hub/orangepi/*.py
EOF

# Запустить установку
echo ""
echo "⚙️  Running setup script..."
ssh "$ORANGEPI_USER@$ORANGEPI_HOST" "cd /opt/sensor_hub && sudo bash orangepi/setup.sh"

# Инициализировать InfluxDB
echo ""
echo "🗄️  Initializing InfluxDB..."
ssh "$ORANGEPI_USER@$ORANGEPI_HOST" "sudo python3 /opt/sensor_hub/orangepi/init_influxdb.py" || echo "   (Skipping, may already be initialized)"

# Инициализировать Grafana
echo ""
echo "📊 Initializing Grafana..."
ssh "$ORANGEPI_USER@$ORANGEPI_HOST" "sleep 5 && sudo python3 /opt/sensor_hub/orangepi/init_grafana.py" || echo "   (Skipping, may need manual setup)"

# Запустить сервис
echo ""
echo "▶️  Starting sensor reader service..."
ssh "$ORANGEPI_USER@$ORANGEPI_HOST" "sudo systemctl start sensor-reader"
sleep 2

# Проверить статус
echo ""
echo "✅ Checking service status..."
ssh "$ORANGEPI_USER@$ORANGEPI_HOST" "sudo systemctl status sensor-reader --no-pager || true"

# Вывести информацию
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║              Deployment Complete!                          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Access Grafana:"
echo "   URL: http://$ORANGEPI_HOST:3000"
echo "   User: admin"
echo "   Pass: admin (change at first login!)"
echo ""
echo "📋 Check logs:"
echo "   ssh root@$ORANGEPI_HOST 'journalctl -u sensor-reader -f'"
echo ""
echo "🔧 View sensor data:"
echo "   ssh root@$ORANGEPI_HOST 'tail -f /var/log/sensor_data.csv'"
echo ""
echo "🚀 Next steps:"
echo "   1. Connect RP2040 via USB to Orange Pi"
echo "   2. Check logs to verify data reception"
echo "   3. Open Grafana and view real-time data"
echo ""
