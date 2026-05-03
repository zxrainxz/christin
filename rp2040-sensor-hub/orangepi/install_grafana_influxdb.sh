#!/bin/bash
set -e

LOGFILE=/var/log/sensor_install_grafana.log
exec > >(tee -a "$LOGFILE") 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting Grafana/InfluxDB install"

if [ "$EUID" -ne 0 ]; then
  echo "This script must be run as root"
  exit 1
fi

rm -f /etc/apt/sources.list.d/grafana.list
rm -f /etc/apt/keyrings/grafana-archive-keyring.gpg

apt-get update
apt-get install -y apt-transport-https gnupg2 wget ca-certificates software-properties-common
apt-get install -y influxdb influxdb-client curl

install_grafana_docker() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Falling back to official Grafana Docker image"

  apt-get install -y docker.io
  systemctl enable docker
  systemctl restart docker

  docker volume create grafana-storage >/dev/null 2>&1 || true
  docker rm -f grafana >/dev/null 2>&1 || true
  docker run -d \
    --name grafana \
    --restart unless-stopped \
    --network host \
    --volume grafana-storage:/var/lib/grafana \
    grafana/grafana-enterprise >/dev/null
}

mkdir -p /etc/apt/keyrings
if ! curl -fsSL https://apt.grafana.com/gpg-full.key -o /etc/apt/keyrings/grafana.asc; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Could not download Grafana apt key"
  install_grafana_docker
  systemctl enable influxdb
  systemctl restart influxdb
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Grafana/InfluxDB install completed"
  exit 0
fi

chmod 644 /etc/apt/keyrings/grafana.asc
cat > /etc/apt/sources.list.d/grafana.list <<'EOF'
deb [signed-by=/etc/apt/keyrings/grafana.asc] https://apt.grafana.com stable main
EOF

if ! apt-get update; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Grafana apt repository is unavailable"
  rm -f /etc/apt/sources.list.d/grafana.list
  install_grafana_docker
  systemctl enable influxdb
  systemctl restart influxdb
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Grafana/InfluxDB install completed"
  exit 0
fi

apt-get install -y grafana

systemctl enable influxdb
systemctl enable grafana-server
systemctl restart influxdb
systemctl restart grafana-server

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Grafana/InfluxDB install completed"
exit 0
