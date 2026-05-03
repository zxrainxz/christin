"""
Waveshare RP2040-Zero boot script
Минимальная диагностика перед запуском main.py
"""

import gc
import machine
import os

# Версия прошивки
FIRMWARE_VERSION = "1.0.0"
BUILD_DATE = "2026-05-03"
BOARD_NAME = "Waveshare RP2040-Zero"
ONBOARD_WS2812_PIN = 16

print(f"\n=== RP2040 Sensor Hub v{FIRMWARE_VERSION} ===")
print(f"Build: {BUILD_DATE}")
print(f"Board: {BOARD_NAME}")

try:
    uname = os.uname()
    print(f"Platform: {uname.sysname} {uname.release}")
except Exception:
    print("Platform: MicroPython rp2")

print(f"CPU frequency: {machine.freq()} Hz")
print(f"Onboard WS2812 data pin: GP{ONBOARD_WS2812_PIN}\n")

# Проверка доступной памяти
gc.collect()
print(f"Free memory: {gc.mem_free()} bytes\n")

# Важно: у RP2040-Zero нет обычного LED на GPIO25.
# На плате есть адресный WS2812 на GPIO16, поэтому этот GPIO не используем под датчики.
print("Reserved board GPIO: GP16 (onboard WS2812 RGB LED)")

print("Boot completed, starting main...\n")
