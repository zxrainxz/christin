#!/usr/bin/env python3
"""
Quick start script to deploy and run sensor hub
"""

import subprocess
import sys
import os
import time

def run_command(cmd, description):
    """Run a shell command"""
    print(f"\n{'='*60}")
    print(f"  {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("  RP2040 Sensor Hub - Quick Start")
    print("="*60)
    
    # Check if running as root
    if os.getuid() != 0:
        print("\nERROR: This script must be run as root")
        sys.exit(1)
    
    # Run setup
    if not run_command("bash /opt/sensor_hub/setup.sh", "Running system setup"):
        sys.exit(1)
    
    # Initialize InfluxDB
    if not run_command("python3 /opt/sensor_hub/scripts/init_influxdb.py", "Initializing InfluxDB"):
        print("Warning: InfluxDB initialization failed, continuing...")
    
    # Wait for Grafana
    print("\nWaiting for Grafana to start...")
    time.sleep(5)
    
    # Initialize Grafana
    if not run_command("python3 /opt/sensor_hub/scripts/init_grafana.py", "Initializing Grafana"):
        print("Warning: Grafana initialization failed, continuing...")
    
    # Start sensor reader
    print("\n" + "="*60)
    print("  Starting Sensor Reader Service")
    print("="*60)
    
    run_command("systemctl start sensor-reader", "Starting sensor-reader service")
    time.sleep(2)
    
    # Check service status
    print("\nChecking service status...")
    os.system("systemctl status sensor-reader")
    
    print("\n" + "="*60)
    print("  Setup Completed!")
    print("="*60)
    print("\nYour sensor hub is now running!")
    print("\nNext steps:")
    print("1. Connect RP2040 to Orange Pi with a regular USB cable")
    print("2. Access Grafana: http://192.168.0.202:3000")
    print("3. Check logs: journalctl -u sensor-reader -f")
    print("\nTo stop: systemctl stop sensor-reader")
    print("To restart: systemctl restart sensor-reader")

if __name__ == '__main__':
    main()
