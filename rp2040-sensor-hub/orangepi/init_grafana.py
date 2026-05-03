#!/usr/bin/env python3
"""
Grafana Dashboard Generator
Автоматическое создание дашборда для визуализации датчиков
"""

import json
import requests
import sys

GRAFANA_URL = "http://localhost:3000"
GRAFANA_USER = "admin"
GRAFANA_PASSWORD = "admin"

def init_grafana():
    """Инициализировать Grafana"""
    
    print("Connecting to Grafana...")
    
    try:
        response = requests.get(f"{GRAFANA_URL}/api/health")
        if response.status_code == 200:
            print("✓ Connected to Grafana")
        else:
            print(f"✗ Grafana returned status {response.status_code}")
            sys.exit(1)
    except Exception as e:
        print(f"✗ Failed to connect to Grafana: {e}")
        print("  Make sure Grafana is running: systemctl start grafana-server")
        sys.exit(1)
    
    # Изменить пароль администратора
    print("\nSetting admin password...")
    try:
        response = requests.post(
            f"{GRAFANA_URL}/api/admin/users/1/password",
            json={"password": GRAFANA_PASSWORD},
            auth=(GRAFANA_USER, "admin")
        )
        print("✓ Admin password set")
    except:
        print("  (Password may already be set)")
    
    # Добавить InfluxDB как data source
    print("\nAdding InfluxDB data source...")
    
    datasource = {
        "name": "InfluxDB-Sensors",
        "type": "influxdb",
        "access": "proxy",
        "url": "http://localhost:8086",
        "database": "sensors",
        "isDefault": True
    }
    
    try:
        response = requests.post(
            f"{GRAFANA_URL}/api/datasources",
            json=datasource,
            auth=(GRAFANA_USER, GRAFANA_PASSWORD)
        )
        
        if response.status_code == 200:
            print("✓ InfluxDB data source added")
            datasource_id = response.json()['id']
        else:
            print(f"  Data source may already exist (status {response.status_code})")
            # Получить ID существующего источника
            response = requests.get(
                f"{GRAFANA_URL}/api/datasources/name/InfluxDB-Sensors",
                auth=(GRAFANA_USER, GRAFANA_PASSWORD)
            )
            datasource_id = response.json()['id'] if response.status_code == 200 else 1
    except Exception as e:
        print(f"  Error: {e}")
        datasource_id = 1
    
    # Создать дашборд
    print("\nCreating dashboard...")
    
    dashboard = {
        "dashboard": {
            "title": "Sensor Hub",
            "tags": ["rp2040", "sensors"],
            "timezone": "browser",
            "panels": [
                {
                    "id": 1,
                    "title": "Temperature SHT21",
                    "type": "graph",
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
                    "targets": [
                        {
                            "datasource": "InfluxDB-Sensors",
                            "measurement": "temperature_sht21",
                            "select": [[{"params": ["value"], "type": "field"}]]
                        }
                    ]
                },
                {
                    "id": 2,
                    "title": "Humidity SHT21",
                    "type": "graph",
                    "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0},
                    "targets": [
                        {
                            "datasource": "InfluxDB-Sensors",
                            "measurement": "humidity_sht21",
                            "select": [[{"params": ["value"], "type": "field"}]]
                        }
                    ]
                },
                {
                    "id": 3,
                    "title": "Temperature DS18B20",
                    "type": "graph",
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8},
                    "targets": [
                        {
                            "datasource": "InfluxDB-Sensors",
                            "measurement": "temperature_ds18b20",
                            "select": [[{"params": ["value"], "type": "field"}]]
                        }
                    ]
                }
            ],
            "refresh": "30s",
            "schemaVersion": 16,
            "version": 0
        },
        "overwrite": True
    }
    
    try:
        response = requests.post(
            f"{GRAFANA_URL}/api/dashboards/db",
            json=dashboard,
            auth=(GRAFANA_USER, GRAFANA_PASSWORD)
        )
        
        if response.status_code in [200, 201]:
            print("✓ Dashboard created/updated")
        else:
            print(f"✗ Error creating dashboard (status {response.status_code})")
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"✗ Error creating dashboard: {e}")
    
    print("\n✓ Grafana initialization completed!")
    print(f"\nAccess Grafana: {GRAFANA_URL}")
    print(f"Username: {GRAFANA_USER}")
    print(f"Password: {GRAFANA_PASSWORD}")

if __name__ == '__main__':
    init_grafana()
