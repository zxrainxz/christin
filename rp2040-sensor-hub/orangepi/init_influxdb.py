#!/usr/bin/env python3
"""
InfluxDB Initialization Script
Создание БД, пользователей и retention policies
"""

import sys
import os
import time
from influxdb import InfluxDBClient

INFLUXDB_HOST = "localhost"
INFLUXDB_PORT = 8086
INFLUXDB_DB = "sensors"

def init_influxdb():
    """Инициализировать InfluxDB"""
    
    print("Connecting to InfluxDB...")
    
    try:
        client = InfluxDBClient(host=INFLUXDB_HOST, port=INFLUXDB_PORT)
        client.ping()
        print("✓ Connected to InfluxDB")
    except Exception as e:
        print(f"✗ Failed to connect to InfluxDB: {e}")
        sys.exit(1)
    
    # Создать БД
    print("\nCreating database...")
    try:
        dbs = client.get_list_database()
        if {'name': INFLUXDB_DB} not in dbs:
            client.create_database(INFLUXDB_DB)
            print(f"✓ Created database: {INFLUXDB_DB}")
        else:
            print(f"✓ Database already exists: {INFLUXDB_DB}")
    except Exception as e:
        print(f"✗ Error creating database: {e}")
        sys.exit(1)
    
    # Создать retention policy (30 дней)
    print("\nCreating retention policy...")
    try:
        client.switch_database(INFLUXDB_DB)
        retention_policies = client.get_list_retention_policies()
        
        policy_exists = False
        for policy in retention_policies:
            if policy['name'] == '30d':
                policy_exists = True
                break
        
        if not policy_exists:
            client.create_retention_policy('30d', '30d', 1, INFLUXDB_DB, default=True)
            print("✓ Created retention policy: 30 days")
        else:
            print("✓ Retention policy already exists")
    except Exception as e:
        print(f"✗ Error creating retention policy: {e}")
        sys.exit(1)
    
    # Создать непрерывный запрос (CQ) для средних значений каждые 5 минут
    print("\nCreating continuous queries...")
    try:
        # Для температуры SHT21
        cq_temp_sht21 = """
        CREATE CONTINUOUS QUERY "cq_temp_sht21_5m" ON "sensors"
        BEGIN
            SELECT MEAN("value") as "mean"
            INTO "temperature_sht21_5m"
            FROM "temperature_sht21"
            GROUP BY time(5m), *
        END
        """
        
        # Для влажности SHT21
        cq_humid_sht21 = """
        CREATE CONTINUOUS QUERY "cq_humid_sht21_5m" ON "sensors"
        BEGIN
            SELECT MEAN("value") as "mean"
            INTO "humidity_sht21_5m"
            FROM "humidity_sht21"
            GROUP BY time(5m), *
        END
        """
        
        # Для температуры DS18B20
        cq_temp_ds18b20 = """
        CREATE CONTINUOUS QUERY "cq_temp_ds18b20_5m" ON "sensors"
        BEGIN
            SELECT MEAN("value") as "mean"
            INTO "temperature_ds18b20_5m"
            FROM "temperature_ds18b20"
            GROUP BY time(5m), *
        END
        """
        
        # Выполнить запросы
        existing_cqs = client.query('SHOW CONTINUOUS QUERIES')
        
        cq_names = []
        if 'sensors' in existing_cqs:
            for cq in existing_cqs.get('sensors', []):
                cq_names.append(cq.get('name'))
        
        for query in [cq_temp_sht21, cq_humid_sht21, cq_temp_ds18b20]:
            try:
                client.query(query)
                print("✓ Continuous query created")
            except:
                pass  # CQ может уже существовать
        
    except Exception as e:
        print(f"Warning: Error creating continuous queries: {e}")
    
    print("\n✓ InfluxDB initialization completed!")
    print(f"\nDatabase: {INFLUXDB_DB}")
    print(f"Measurements:")
    print("  - temperature_sht21")
    print("  - humidity_sht21")
    print("  - temperature_ds18b20")

if __name__ == '__main__':
    init_influxdb()
