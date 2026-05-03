#!/bin/bash
# Upload firmware to RP2040
# Автоматическая загрузка прошивки на RP2040-Zero

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RP2040_DIR="$PROJECT_DIR/rp2040"

# Параметры
SERIAL_PORT="${1:-/dev/ttyACM0}"
BAUDRATE="115200"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║       RP2040 Firmware Upload                               ║"
echo "╚════════════════════════════════════════════════════════════╝"

# Проверить серийный порт
if [ ! -e "$SERIAL_PORT" ]; then
    echo "❌ Error: Serial port $SERIAL_PORT not found!"
    echo ""
    echo "Available serial ports:"
    ls -la /dev/ttyACM* /dev/ttyUSB* 2>/dev/null || echo "  (none found)"
    echo ""
    echo "Usage: $0 [PORT]"
    echo "Example: $0 /dev/ttyACM0"
    exit 1
fi

echo "✓ Found serial port: $SERIAL_PORT"

# Проверить ampy
if ! command -v ampy &> /dev/null; then
    echo ""
    echo "❌ ampy not installed. Installing..."
    pip install adafruit-ampy
fi

echo ""
echo "📝 Uploading files..."
echo ""

# Загрузить boot.py
echo "1. Uploading boot.py..."
ampy --port "$SERIAL_PORT" --baud "$BAUDRATE" put "$RP2040_DIR/boot.py"
echo "   ✓ boot.py uploaded"

# Загрузить main.py
echo "2. Uploading main.py..."
ampy --port "$SERIAL_PORT" --baud "$BAUDRATE" put "$RP2040_DIR/main.py"
echo "   ✓ main.py uploaded"

# Перезагрузить устройство
echo ""
echo "🔄 Rebooting RP2040..."
python3 << EOF
import serial
import time
import sys

try:
    ser = serial.Serial('$SERIAL_PORT', 115200, timeout=1)
    time.sleep(1)
    
    # Отправить CTRL-D для мягкой перезагрузки
    ser.write(b'\x04')
    time.sleep(2)
    
    ser.close()
    print("   ✓ Reboot complete")
except Exception as e:
    print(f"   Warning: {e}")
EOF

echo ""
echo "✅ Firmware upload completed!"
echo ""
echo "📊 Checking connection..."
sleep 2

python3 << EOF
import serial
import json
import time

try:
    ser = serial.Serial('$SERIAL_PORT', 115200, timeout=2)
    time.sleep(2)
    
    print("Waiting for data from RP2040...")
    
    timeout = time.time() + 10
    while time.time() < timeout:
        if ser.in_waiting:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                print(f"  {line}")
                if line.startswith('{'):
                    try:
                        data = json.loads(line)
                        print("  ✓ Valid JSON data received!")
                    except:
                        pass
        time.sleep(0.1)
    
    ser.close()
except Exception as e:
    print(f"Error: {e}")
EOF

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Next step: Connect RP2040 to Orange Pi via USB            ║"
echo "║  Then run: bash deploy_orangepi.sh                         ║"
echo "╚════════════════════════════════════════════════════════════╝"
