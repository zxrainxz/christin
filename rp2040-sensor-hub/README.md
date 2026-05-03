# RP2040 Sensor Hub

Полнофункциональная система мониторинга датчиков температуры и влажности с визуализацией в Grafana.

## 📋 Компоненты

- **RP2040-Zero** - микроконтроллер для сбора данных с датчиков
- **SHT21/HTU21** - датчик температуры и влажности (I2C)
- **DS18B20** - датчик температуры (OneWire)
- **Orange Pi 4 LTS** - сервер для сбора, хранения и визуализации данных
- **InfluxDB** - временной ряд БД
- **Grafana** - визуализация данных

## 🔌 Подключение

### Распиновка RP2040-Zero

```
Питание:
- 3V3 (P1-21) → питание датчиков 3.3V
- GND (P1-22 или P3-5) → земля
- VSYS (P1-23) → вход питания платы, если не питать её по USB

SHT21/HTU21 (I2C):
- SDA → GP4 (P1-5)
- SCL → GP5 (P1-6)
- VDD → 3V3
- GND → GND

DS18B20 (OneWire):
- DQ → GP6 (P1-7) + Pull-up 4.7kOm к 3V3
- VDD → 3V3
- GND → GND

USB к Orange Pi:
- Подключить RP2040-Zero к Orange Pi обычным USB-кабелем
- Данные идут через штатный USB CDC (`/dev/ttyACM*`)
- GPIO `GP0/GP1` для связи с Orange Pi не используются
- GPIO `GP16` занят встроенным WS2812 RGB LED платы
```

Подробная распиновка в [docs/РАСПИНОВКА.md](docs/РАСПИНОВКА.md)

## 🚀 Быстрый старт

### На PC (загрузка RP2040)

```bash
# 1. Установить инструменты
pip install adafruit-ampy

# 2. RP2040-Zero подключить к PC в режиме загрузчика (кнопка BOOT + RESET)
# Или просто подключить USB, если уже установлена MicroPython

# 3. Загрузить прошивку
ampy --port /dev/ttyACM0 put rp2040/boot.py
ampy --port /dev/ttyACM0 put rp2040/main.py

# 4. Перезагрузить RP2040 (RESET)
```

### На Orange Pi

```bash
# 1. Подключиться по SSH
ssh root@192.168.0.202

# 2. Загрузить проект
cd /opt
git clone <repository> sensor_hub
# или скопировать файлы напрямую

# 3. Запустить установку
sudo bash /opt/sensor_hub/orangepi/setup.sh

# 4. Инициализировать сервисы
sudo /opt/sensor_hub/venv/bin/python3 /opt/sensor_hub/orangepi/init_influxdb.py
sudo /opt/sensor_hub/venv/bin/python3 /opt/sensor_hub/orangepi/init_grafana.py

# 5. Запустить сервис
sudo systemctl start sensor-reader
```

### Проверка

```bash
# Проверить статус сервиса
sudo systemctl status sensor-reader

# Смотреть логи в реальном времени
sudo journalctl -u sensor-reader -f

# Проверить CSV файл
tail -f /var/log/sensor_data.csv
```

## 📊 Доступ к Grafana

- **URL:** http://192.168.0.202:3000
- **Username:** admin
- **Password:** admin (измените при первом логине!)

## 🔧 Конфигурация

### RP2040 (rp2040/main.py)

```python
BOARD_NAME = "Waveshare RP2040-Zero"
I2C_FREQUENCY = 400000        # Частота I2C
SENSOR_READ_INTERVAL = 5      # Интервал чтения (сек)
```

### Orange Pi (orangepi/sensor_reader.py)

```python
SERIAL_PORT = ""              # Пусто = автоопределение USB порта RP2040
INFLUXDB_HOST = "localhost"
INFLUXDB_DB = "sensors"
```

## 📈 Данные

Система отправляет JSON строки в формате:

```json
{
  "timestamp": 1704067200,
  "temp_sht21": 22.5,
  "humid_sht21": 45.2,
  "temp_ds18b20": 23.1,
  "status": 0
}
```

Данные сохраняются в:
- **InfluxDB:** база `sensors` с измерениями `temperature_*` и `humidity_*`
- **CSV:** `/var/log/sensor_data.csv`

## 🐛 Устранение неполадок

### RP2040 не подключается

```bash
# Проверить наличие устройства
ls -la /dev/ttyACM* /dev/serial/by-id/*

# Проверить права доступа
sudo usermod -a -G dialout $USER

# Проверить логи
dmesg | tail -20
```

### Нет данных в Grafana

1. Проверить работу сенсора:
   ```bash
   python3 -c "import glob, serial; port = sorted(glob.glob('/dev/ttyACM*'))[0]; s = serial.Serial(port, 115200, timeout=2); print(s.readline())"
   ```

2. Проверить InfluxDB:
   ```bash
   influx -execute "SELECT * FROM temperature_sht21 LIMIT 5"
   ```

3. Проверить логи sensor-reader:
   ```bash
   sudo journalctl -u sensor-reader -n 100
   ```

## 📚 Структура проекта

```
rp2040-sensor-hub/
├── rp2040/                    # Прошивка RP2040
│   ├── boot.py               # Boot скрипт
│   ├── main.py               # Основная прошивка
│   └── requirements.txt       # Зависимости MicroPython
│
├── orangepi/                  # Скрипты Orange Pi
│   ├── sensor_reader.py       # Основной сервис
│   ├── setup.sh              # Скрипт установки
│   ├── sensor-reader.service # Systemd сервис
│   ├── init_influxdb.py      # Инициализация InfluxDB
│   ├── init_grafana.py       # Инициализация Grafana
│   └── quickstart.py         # Быстрый старт
│
├── docs/                      # Документация
│   └── РАСПИНОВКА.md         # Подробная распиновка
│
└── README.md                  # Этот файл
```

## ⚙️ Системные требования

**RP2040-Zero:**
- MicroPython ≥ 1.19
- Память: ≥ 150KB Flash, ≥ 256KB RAM
- Встроенный WS2812 RGB LED на GP16

**Orange Pi 4 LTS:**
- ОС: Ubuntu 20.04+
- Python 3.8+
- InfluxDB 1.8+
- Grafana 8.0+

## 🔐 Безопасность

Перед использованием в боевой среде:

1. **Изменить пароли:**
   - Grafana admin
   - InfluxDB credentials (в sensor_reader.py)

2. **Настроить HTTPS:**
   - Сертификаты SSL для Grafana
   - Шифрование данных

3. **Ограничить доступ:**
   - UFW firewall
   - Только локальная сеть для InfluxDB

## 📝 Лицензия

MIT License

## 🤝 Поддержка

Для вопросов и проблем открывайте Issues в репозитории.
