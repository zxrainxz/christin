#!/usr/bin/env python3
"""
Orange Pi Sensor Reader
Читает данные с RP2040 через USB UART и отправляет в InfluxDB
"""

import os
import glob
import json
import serial
import time
import sys
from datetime import datetime

try:
    from influxdb import InfluxDBClient
    HAS_INFLUXDB = True
except ImportError:
    HAS_INFLUXDB = False
    print("Warning: influxdb module not installed. Data will be saved to CSV only.")

# Конфигурация
SERIAL_PORT = os.environ.get("SERIAL_PORT", "").strip()
SERIAL_BAUDRATE = int(os.environ.get("SERIAL_BAUDRATE", "115200"))
SERIAL_PORT_PATTERNS = [
    "/dev/serial/by-id/*MicroPython*",
    "/dev/serial/by-id/*RP2040*",
    "/dev/serial/by-id/*Raspberry_Pi*",
    "/dev/ttyACM*",
    "/dev/ttyUSB*",
]
INFLUXDB_HOST = os.environ.get("INFLUXDB_HOST", "localhost")
INFLUXDB_PORT = int(os.environ.get("INFLUXDB_PORT", "8086"))
INFLUXDB_DB = os.environ.get("INFLUXDB_DB", "sensors")
INFLUXDB_USER = os.environ.get("INFLUXDB_USER", "")
INFLUXDB_PASSWORD = os.environ.get("INFLUXDB_PASSWORD", "")

CSV_FILE = "/var/log/sensor_data.csv"
LOG_FILE = "/var/log/sensor_reader.log"
MIN_VALID_UNIX_TS = 1700000000

class SensorReader:
    """Класс для чтения данных с RP2040"""
    
    def __init__(self, port=SERIAL_PORT, baudrate=SERIAL_BAUDRATE):
        self.port = port.strip() if port else ""
        self.baudrate = baudrate
        self.serial = None
        self.influxdb = None
        self.csv_initialized = False
        self.log_file = None
        
        self.init_logging()
        self.init_serial()
        self.init_influxdb()
        self.init_csv()
    
    def init_logging(self):
        """Инициализация логирования"""
        try:
            os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
            self.log_file = open(LOG_FILE, 'a')
        except Exception as e:
            print(f"Error opening log file: {e}")
    
    def log(self, message):
        """Логировать сообщение"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = f"[{timestamp}] {message}"
        print(msg)
        
        if self.log_file:
            try:
                self.log_file.write(msg + '\n')
                self.log_file.flush()
            except:
                pass

    def resolve_serial_port(self):
        """Найти RP2040 на штатном USB порту"""
        if self.port:
            if os.path.exists(self.port):
                return self.port
            self.log(f"Configured serial port {self.port} not found, falling back to auto-detect")
            self.port = ""

        for pattern in SERIAL_PORT_PATTERNS:
            matches = sorted(glob.glob(pattern))
            if matches:
                self.port = matches[0]
                return self.port

        return None
    
    def init_serial(self):
        """Инициализация USB serial"""
        retry_count = 0

        while True:
            try:
                port = self.resolve_serial_port()
                if not port:
                    raise FileNotFoundError("RP2040 USB serial port not found")

                self.serial = serial.Serial(port, self.baudrate, timeout=1)
                time.sleep(2)  # Дать RP2040 время на инициализацию
                self.serial.reset_input_buffer()
                self.log(f"Serial port {port} opened successfully at {self.baudrate} baud")
                return
            except Exception as e:
                retry_count += 1
                self.log(f"Failed to open serial port (attempt {retry_count}): {e}")
                time.sleep(5)
    
    def init_influxdb(self):
        """Инициализация InfluxDB"""
        if not HAS_INFLUXDB:
            self.log("InfluxDB support disabled (module not installed)")
            return
        
        try:
            client_kwargs = {
                'host': INFLUXDB_HOST,
                'port': INFLUXDB_PORT,
                'database': INFLUXDB_DB,
            }
            if INFLUXDB_USER:
                client_kwargs['username'] = INFLUXDB_USER
            if INFLUXDB_PASSWORD:
                client_kwargs['password'] = INFLUXDB_PASSWORD

            self.influxdb = InfluxDBClient(**client_kwargs)
            
            # Проверить соединение
            self.influxdb.ping()
            
            # Создать БД если не существует
            dbs = self.influxdb.get_list_database()
            if {'name': INFLUXDB_DB} not in dbs:
                self.influxdb.create_database(INFLUXDB_DB)
                self.log(f"Created InfluxDB database: {INFLUXDB_DB}")
            
            self.log("InfluxDB connection established")
        except Exception as e:
            self.log(f"InfluxDB connection failed: {e}")
            self.influxdb = None
    
    def init_csv(self):
        """Инициализация CSV файла"""
        try:
            os.makedirs(os.path.dirname(CSV_FILE), exist_ok=True)
            
            # Проверить существует ли файл
            csv_exists = os.path.exists(CSV_FILE)
            
            with open(CSV_FILE, 'a') as f:
                if not csv_exists:
                    f.write("timestamp,temp_sht21,humid_sht21,temp_ds18b20,status\n")
            
            self.csv_initialized = True
            self.log(f"CSV file initialized: {CSV_FILE}")
        except Exception as e:
            self.log(f"Error initializing CSV: {e}")

    def normalize_timestamp(self, data):
        """Привести timestamp к серверному времени, если у RP2040 нет RTC"""
        now = int(time.time())
        raw_ts = data.get('timestamp')

        if not isinstance(raw_ts, int):
            data['timestamp'] = now
            return

        if raw_ts < MIN_VALID_UNIX_TS or raw_ts > now + 86400:
            data['timestamp'] = now
    
    def write_csv(self, data):
        """Записать данные в CSV"""
        if not self.csv_initialized:
            return
        
        try:
            timestamp = datetime.fromtimestamp(data.get('timestamp', time.time())).isoformat()
            temp_sht21 = data.get('temp_sht21', '')
            humid_sht21 = data.get('humid_sht21', '')
            temp_ds18b20 = data.get('temp_ds18b20', '')
            status = data.get('status', 0)
            
            with open(CSV_FILE, 'a') as f:
                f.write(f"{timestamp},{temp_sht21},{humid_sht21},{temp_ds18b20},{status}\n")
        except Exception as e:
            self.log(f"CSV write error: {e}")
    
    def send_to_influxdb(self, data):
        """Отправить данные в InfluxDB"""
        if not self.influxdb or not HAS_INFLUXDB:
            return
        
        try:
            timestamp_ms = int(data.get('timestamp', time.time())) * 1000000000  # nanoseconds
            
            points = []
            
            # SHT21 data
            if 'temp_sht21' in data:
                points.append({
                    'measurement': 'temperature_sht21',
                    'tags': {'sensor': 'sht21'},
                    'time': timestamp_ms,
                    'fields': {'value': float(data['temp_sht21'])}
                })
            
            if 'humid_sht21' in data:
                points.append({
                    'measurement': 'humidity_sht21',
                    'tags': {'sensor': 'sht21'},
                    'time': timestamp_ms,
                    'fields': {'value': float(data['humid_sht21'])}
                })
            
            # DS18B20 data
            if 'temp_ds18b20' in data:
                points.append({
                    'measurement': 'temperature_ds18b20',
                    'tags': {'sensor': 'ds18b20'},
                    'time': timestamp_ms,
                    'fields': {'value': float(data['temp_ds18b20'])}
                })
            
            if points:
                self.influxdb.write_points(points)
        except Exception as e:
            self.log(f"InfluxDB write error: {e}")
    
    def read_loop(self):
        """Главный цикл чтения данных"""
        self.log("Starting sensor read loop...")
        
        error_count = 0
        max_errors = 10
        
        while True:
            try:
                line = self.serial.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    if line.startswith('{'):
                        if "'timestamp'" in line and '"timestamp"' not in line:
                            self.log(f"RP2040 console: {line}")
                            continue

                        try:
                            data = json.loads(line)
                            self.process_data(data)
                            error_count = 0
                        except json.JSONDecodeError as e:
                            self.log(f"JSON decode error: {e}: {line}")
                            error_count += 1
                    else:
                        self.log(f"RP2040 console: {line}")
                else:
                    time.sleep(0.1)
                
                # Проверка на избыток ошибок
                if error_count > max_errors:
                    self.log(f"Too many errors ({error_count}), reconnecting...")
                    self.reconnect()
                    error_count = 0
                
            except Exception as e:
                self.log(f"Read loop error: {e}")
                error_count += 1
                time.sleep(1)
    
    def process_data(self, data):
        """Обработать полученные данные"""
        self.normalize_timestamp(data)

        # Логировать
        self.log(f"Data received: {json.dumps(data)}")
        
        # Сохранить в CSV
        self.write_csv(data)
        
        # Отправить в InfluxDB
        self.send_to_influxdb(data)
    
    def reconnect(self):
        """Переподключиться"""
        if self.serial:
            try:
                self.serial.close()
            except:
                pass

        self.serial = None
        time.sleep(2)
        self.init_serial()
    
    def close(self):
        """Закрыть соединения"""
        if self.serial:
            self.serial.close()
        if self.log_file:
            self.log_file.close()

def main():
    """Главная функция"""
    reader = SensorReader()
    
    try:
        reader.read_loop()
    except KeyboardInterrupt:
        reader.log("Sensor reader stopped by user")
        reader.close()
        sys.exit(0)
    except Exception as e:
        reader.log(f"Fatal error: {e}")
        reader.close()
        sys.exit(1)

if __name__ == '__main__':
    main()
