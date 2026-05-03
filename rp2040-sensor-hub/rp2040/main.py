"""
RP2040 Sensor Hub Firmware
Подключение: SHT21/HTU21 (I2C) + DS18B20 (OneWire)
Плата: Waveshare RP2040-Zero
Отправка данных через штатный USB CDC в JSON формате
"""

import json
import sys
import time
import machine
from machine import I2C, Pin
import onewire
import ds18x20

# Конфигурация
BOARD_NAME = "Waveshare RP2040-Zero"
I2C_FREQUENCY = 400000
SENSOR_READ_INTERVAL = 5  # секунды

# GPIO pins for Waveshare RP2040-Zero
# GP16 занят встроенным WS2812 RGB LED, поэтому под датчики его не используем.
I2C_SDA_PIN = 4
I2C_SCL_PIN = 5
ONEWIRE_PIN = 6
ONBOARD_WS2812_PIN = 16

# I2C адреса датчиков
SHT21_ADDR = 0x40

# Коды команд SHT21
SHT21_TEMP_CMD = b'\xE3'
SHT21_HUMID_CMD = b'\xE5'
SHT21_RESET_CMD = b'\xFE'

# Флаги состояния
STATUS_OK = 0x00
STATUS_SHT21_ERROR = 0x01
STATUS_DS18B20_ERROR = 0x02
STATUS_I2C_ERROR = 0x04
STATUS_SERIAL_ERROR = 0x08

class SHT21Sensor:
    """Драйвер датчика SHT21/HTU21"""
    
    def __init__(self, i2c, addr=SHT21_ADDR):
        self.i2c = i2c
        self.addr = addr
        self.temp = 0.0
        self.humid = 0.0
        self.crc_check = True
        
    def write_cmd(self, cmd):
        """Отправить команду"""
        try:
            self.i2c.writeto(self.addr, cmd)
            return True
        except:
            return False
    
    def read_measurement(self, num_bytes=2):
        """Прочитать значение датчика"""
        try:
            data = self.i2c.readfrom(self.addr, num_bytes)
            return data
        except:
            return None
    
    def _crc_check(self, msb, lsb, crc):
        """Проверка контрольной суммы"""
        polynomial = 0x131  # CRC8 polynomial
        crc_val = 0
        
        for byte in [msb, lsb]:
            crc_val ^= byte
            for _ in range(8):
                if crc_val & 0x80:
                    crc_val = (crc_val << 1) ^ polynomial
                else:
                    crc_val = crc_val << 1
                crc_val &= 0xFF
        
        return crc_val == crc
    
    def read_temperature(self):
        """Прочитать температуру в градусах Цельсия"""
        try:
            self.write_cmd(SHT21_TEMP_CMD)
            time.sleep(0.1)  # Время на измерение
            data = self.read_measurement(3)
            
            if data is None or len(data) < 3:
                return None
            
            msb, lsb, crc = data[0], data[1], data[2]
            
            # Проверка CRC (опционально)
            if self.crc_check and not self._crc_check(msb, lsb, crc):
                print("SHT21: CRC error for temperature")
                return None
            
            # Удалить 2 младших бита (флаги)
            raw = (msb << 8) | (lsb & 0xFC)
            
            # Расчёт температуры: T = -46.85 + 175.72 * (raw / 65536)
            temp = -46.85 + 175.72 * (raw / 65536.0)
            self.temp = temp
            return temp
            
        except Exception as e:
            print(f"SHT21 read_temperature error: {e}")
            return None
    
    def read_humidity(self):
        """Прочитать относительную влажность в процентах"""
        try:
            self.write_cmd(SHT21_HUMID_CMD)
            time.sleep(0.1)  # Время на измерение
            data = self.read_measurement(3)
            
            if data is None or len(data) < 3:
                return None
            
            msb, lsb, crc = data[0], data[1], data[2]
            
            # Проверка CRC (опционально)
            if self.crc_check and not self._crc_check(msb, lsb, crc):
                print("SHT21: CRC error for humidity")
                return None
            
            # Удалить 2 младших бита (флаги)
            raw = (msb << 8) | (lsb & 0xFC)
            
            # Расчёт влажности: RH = -6 + 125 * (raw / 65536)
            humid = -6 + 125 * (raw / 65536.0)
            
            # Ограничить значение 0-100%
            humid = max(0, min(100, humid))
            self.humid = humid
            return humid
            
        except Exception as e:
            print(f"SHT21 read_humidity error: {e}")
            return None
    
    def read_all(self):
        """Прочитать оба значения"""
        temp = self.read_temperature()
        time.sleep(0.05)
        humid = self.read_humidity()
        return temp, humid

class DS18B20Sensor:
    """Драйвер датчика DS18B20 (OneWire)"""
    
    def __init__(self, pin_num):
        self.pin = Pin(pin_num, Pin.IN, Pin.PULL_UP)
        self.ow = onewire.OneWire(self.pin)
        self.ds = ds18x20.DS18X20(self.ow)
        self.devices = []
        self.temp = 0.0
        self._scan_devices()
    
    def _scan_devices(self):
        """Сканировать подключённые датчики"""
        try:
            self.devices = self.ds.scan()
            print(f"DS18B20: Found {len(self.devices)} device(s)")
            for device in self.devices:
                print(f"  - {device}")
        except Exception as e:
            print(f"DS18B20 scan error: {e}")
            self.devices = []
    
    def read_temperature(self, device_index=0):
        """Прочитать температуру первого найденного датчика"""
        try:
            if not self.devices:
                return None
            
            if device_index >= len(self.devices):
                device_index = 0
            
            # Инициировать измерение
            self.ds.convert_temp()
            time.sleep(0.75)  # Время для измерения (750ms для 12-bit)
            
            # Прочитать результат
            device = self.devices[device_index]
            temp = self.ds.read_temp(device)
            self.temp = temp
            return temp
            
        except Exception as e:
            print(f"DS18B20 read error: {e}")
            return None

class SensorHub:
    """Главный класс управления датчиками"""
    
    def __init__(self):
        self.status = STATUS_OK
        print(f"Board detected: {BOARD_NAME}")
        print("Using GP4/GP5 for I2C, GP6 for OneWire, GP16 reserved for onboard WS2812")
        self.init_i2c()
        self.init_sensors()
    
    def init_i2c(self):
        """Инициализация I2C"""
        try:
            self.i2c = I2C(0, scl=Pin(I2C_SCL_PIN), 
                          sda=Pin(I2C_SDA_PIN), 
                          freq=I2C_FREQUENCY)
            print("I2C initialized at 400kHz")
        except Exception as e:
            print(f"I2C init error: {e}")
            self.status |= STATUS_I2C_ERROR
            self.i2c = None
    
    def init_sensors(self):
        """Инициализация датчиков"""
        self.sht21 = None
        self.ds18b20 = None
        
        try:
            if self.i2c:
                self.sht21 = SHT21Sensor(self.i2c)
                print("SHT21 sensor initialized")
        except Exception as e:
            print(f"SHT21 init error: {e}")
            self.status |= STATUS_SHT21_ERROR
        
        try:
            self.ds18b20 = DS18B20Sensor(ONEWIRE_PIN)
            print("DS18B20 sensor initialized")
        except Exception as e:
            print(f"DS18B20 init error: {e}")
            self.status |= STATUS_DS18B20_ERROR
    
    def read_sensors(self):
        """Прочитать все датчики"""
        data = {
            'timestamp': int(time.time()),
            'status': self.status
        }
        
        # SHT21
        if self.sht21:
            try:
                temp, humid = self.sht21.read_all()
                if temp is not None:
                    data['temp_sht21'] = round(temp, 2)
                if humid is not None:
                    data['humid_sht21'] = round(humid, 2)
            except Exception as e:
                print(f"SHT21 read error: {e}")
                self.status |= STATUS_SHT21_ERROR
        
        # DS18B20
        if self.ds18b20:
            try:
                temp = self.ds18b20.read_temperature()
                if temp is not None:
                    data['temp_ds18b20'] = round(temp, 2)
            except Exception as e:
                print(f"DS18B20 read error: {e}")
                self.status |= STATUS_DS18B20_ERROR
        
        return data
    
    def send_data(self, data):
        """Отправить данные через штатный USB serial"""
        try:
            json_str = json.dumps(data)
            sys.stdout.write(json_str + "\n")
            if hasattr(sys.stdout, "flush"):
                sys.stdout.flush()
            return True
        except Exception as e:
            print(f"USB serial send error: {e}")
            self.status |= STATUS_SERIAL_ERROR
            return False
    
    def run(self):
        """Главный цикл"""
        print("\n=== RP2040 Sensor Hub Started ===\n")
        
        while True:
            try:
                # Прочитать датчики
                data = self.read_sensors()
                
                # Отправить через USB CDC
                self.send_data(data)

                # Ждать перед следующим измерением
                time.sleep(SENSOR_READ_INTERVAL)
                
            except Exception as e:
                print(f"Main loop error: {e}")
                time.sleep(1)

# Точка входа
if __name__ == '__main__':
    hub = SensorHub()
    hub.run()
