#!/usr/bin/env python3
"""
Simple script to upload firmware to RP2040
Simplified version using pyserial
"""

import subprocess
import sys
import os
import time
import glob
import serial
import json

def check_dependencies():
    """Check if required tools are installed"""
    try:
        subprocess.run(["ampy", "--version"], capture_output=True, check=True)
        return True
    except:
        print("Installing adafruit-ampy...")
        subprocess.run([sys.executable, "-m", "pip", "install", "adafruit-ampy"], check=True)
        return True

def find_rp2040_port():
    """Find RP2040 serial port"""
    patterns = [
        "/dev/serial/by-id/*RP2040*",
        "/dev/serial/by-id/*Raspberry_Pi*",
        "/dev/ttyACM*",
        "/dev/ttyUSB*",
    ]

    for pattern in patterns:
        matches = sorted(glob.glob(pattern))
        if matches:
            return matches[0]
    return None

def upload_firmware(port, rp2040_dir):
    """Upload firmware to RP2040"""
    print(f"Uploading to {port}...")
    
    try:
        # Upload boot.py
        print("1. Uploading boot.py...")
        subprocess.run(
            ["ampy", "--port", port, "--baud", "115200", "put", 
             os.path.join(rp2040_dir, "boot.py")],
            check=True
        )
        
        # Upload main.py
        print("2. Uploading main.py...")
        subprocess.run(
            ["ampy", "--port", port, "--baud", "115200", "put",
             os.path.join(rp2040_dir, "main.py")],
            check=True
        )
        
        print("✓ Firmware uploaded successfully")
        return True
    except Exception as e:
        print(f"✗ Upload failed: {e}")
        return False

def verify_firmware(port):
    """Verify firmware is running"""
    print("\nVerifying firmware...")
    
    try:
        ser = serial.Serial(port, 115200, timeout=2)
        time.sleep(2)
        
        print("Waiting for sensor data...")
        timeout = time.time() + 15
        
        while time.time() < timeout:
            if ser.in_waiting:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    print(f"  {line}")
                    if line.startswith('{'):
                        try:
                            data = json.loads(line)
                            print("\n✓ Valid sensor data received!")
                            print(f"  Temperature (SHT21): {data.get('temp_sht21', 'N/A')}°C")
                            print(f"  Humidity (SHT21): {data.get('humid_sht21', 'N/A')}%")
                            print(f"  Temperature (DS18B20): {data.get('temp_ds18b20', 'N/A')}°C")
                            ser.close()
                            return True
                        except:
                            pass
            time.sleep(0.1)
        
        ser.close()
        print("⚠ No valid data received (check sensor connections)")
        return False
        
    except Exception as e:
        print(f"✗ Verification failed: {e}")
        return False

def main():
    print("╔════════════════════════════════════════════════════════════╗")
    print("║       RP2040 Sensor Hub Firmware Upload                    ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    
    # Check dependencies
    print("Checking dependencies...")
    check_dependencies()
    print("✓ Dependencies OK\n")
    
    # Find port
    port = find_rp2040_port()
    if not port:
        print("❌ RP2040 not found!")
        print("Available devices:")
        os.system("ls -la /dev/ttyACM* /dev/ttyUSB* 2>/dev/null || echo '  (none)'")
        sys.exit(1)
    
    print(f"✓ Found RP2040 at {port}\n")
    
    # Get project directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    rp2040_dir = os.path.join(script_dir, "rp2040")
    
    # Upload
    if not upload_firmware(port, rp2040_dir):
        sys.exit(1)
    
    # Verify
    time.sleep(2)
    verify_firmware(port)
    
    print("\n╔════════════════════════════════════════════════════════════╗")
    print("║              Upload Complete!                              ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    print("Next: Connect RP2040 to Orange Pi via USB")

if __name__ == "__main__":
    main()
