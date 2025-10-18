#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# OLED Sonde Info Display
# Copyright (C) 2025 Scops Owl Designs (Sc0ps)
# Email: ScopsOwlDesigns@gmail.com
# Repository: https://github.com/ScopsOwlDesigns/oled-sonde-info-display
#
# This file is part of the OLED Sonde Info Display project.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------
# Description:
#   Displays live radiosonde telemetry from Auto-RX or Horus UDP
#   on a 0.91" or 1.3" SSD1306 OLED via I²C (Raspberry Pi).
# ---------------------------------------------------------------

import os
import time
import json
import socket
import threading
import re
from PIL import Image, ImageDraw, ImageFont
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306

# --------------------------------------------------------------
# Configuration (Environment Variables)
# --------------------------------------------------------------
CALLSIGN = os.getenv("CALLSIGN", "CHANGE_ME")
I2C_ADDR = int(os.getenv("I2C_ADDR", "0x3C"), 16)
HORUS_UDP_PORT = int(os.getenv("HORUS_UDP_PORT", "55673"))
OLED_CONTRAST = int(os.getenv("OLED_CONTRAST", "160"))
PAGE_INTERVAL_S = float(os.getenv("PAGE_INTERVAL_S", "3.0"))
ACTIVE_GAP_S = int(os.getenv("ACTIVE_GAP_S", "10"))
HOLD_LAST_S = int(os.getenv("HOLD_LAST_S", str(6 * 60)))
REFRESH_HZ = float(os.getenv("REFRESH_HZ", "2"))
ALT_UNIT_MODE = os.getenv("ALT_UNIT_MODE", "KM").upper()

# --------------------------------------------------------------
# OLED Setup
# --------------------------------------------------------------
serial = i2c(port=1, address=I2C_ADDR)
device = ssd1306(serial, width=128, height=32)
try:
    device.contrast(OLED_CONTRAST)
except Exception:
    pass

# --------------------------------------------------------------
# Font Setup
# --------------------------------------------------------------
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_SMALL = ImageFont.truetype(FONT_PATH, 10)
FONT_MED = ImageFont.truetype(FONT_PATH, 12)
FONT_LARGE = ImageFont.truetype(FONT_PATH, 16)

# --------------------------------------------------------------
# Telemetry Data Model
# --------------------------------------------------------------
class Telemetry:
    def __init__(self):
        self.model = "—"
        self.callsign = "—"
        self.freq_hz = 403_000_000
        self.altitude = 0
        self.speed = 0.0
        self.vel_v = 0.0
        self.batt = 0.0
        self.snr = 0.0

DATA = Telemetry()
LAST_RX = 0.0

# --------------------------------------------------------------
# Helper Functions
# --------------------------------------------------------------
def draw_centered(draw, text, y, font):
    """Draw centered text on OLED."""
    w, _ = draw.textsize(text, font=font)
    draw.text(((128 - w) // 2, y), text, font=font, fill=255)

def parse_freq(v):
    """Parse frequency in Hz or MHz."""
    try:
        if isinstance(v, str):
            m = re.search(r'([\d.]+)', v)
            if m:
                val = float(m.group(1))
                return int(val * 1e6) if val < 1e5 else int(val)
        return int(float(v))
    except Exception:
        return 403_000_000

def rx_state(now=None):
    """Return state of telemetry reception."""
    now = now or time.time()
    age = now - LAST_RX
    if age <= ACTIVE_GAP_S:
        return "ACTIVE", age
    if age <= HOLD_LAST_S:
        return "RECENT", age
    return "IDLE", age

# --------------------------------------------------------------
# OLED Page Renderers
# --------------------------------------------------------------
def page_model(draw): draw_centered(draw, f"{DATA.model}", 10, FONT_MED)
def page_callsign(draw): draw_centered(draw, f"{DATA.callsign}", 10, FONT_MED)
def page_freq(draw): draw_centered(draw, f"{DATA.freq_hz/1e6:.3f} MHz", 10, FONT_MED)

def page_alt(draw):
    """Altitude page: show km above 1 km, else meters."""
    if DATA.altitude < 1000:
        txt = f"{int(DATA.altitude)} m"
    else:
        txt = f"{DATA.altitude/1000:.1f} km"
    draw_centered(draw, txt, 10, FONT_MED)

def page_speed(draw): draw_centered(draw, f"{DATA.speed:.1f} km/h", 10, FONT_MED)

def page_vspeed(draw):
    """Vertical speed page: uses arrow symbol."""
    symbol = "▲" if DATA.vel_v > 0 else "▼" if DATA.vel_v < 0 else "•"
    draw_centered(draw, f"{symbol} {abs(DATA.vel_v):.1f} m/s", 10, FONT_MED)

def page_batt(draw): draw_centered(draw, f"{DATA.batt:.2f} V", 10, FONT_MED)
def page_snr(draw): draw_centered(draw, f"SNR {DATA.snr:.1f} dB", 10, FONT_MED)

# Display sequence
PAGES = [page_model, page_callsign, page_freq, page_alt, page_speed, page_vspeed, page_batt, page_snr]

# --------------------------------------------------------------
# Display Rendering Logic
# --------------------------------------------------------------
def render_idle():
    img = Image.new("1", (128, 32))
    d = ImageDraw.Draw(img)
    draw_centered(d, CALLSIGN, 8, FONT_LARGE)
    device.display(img)

def render_recent(age):
    img = Image.new("1", (128, 32))
    d = ImageDraw.Draw(img)
    draw_centered(d, f"Last RX {int(age)}s", 10, FONT_MED)
    device.display(img)

def render_active(i):
    img = Image.new("1", (128, 32))
    d = ImageDraw.Draw(img)
    PAGES[i](d)
    device.display(img)

# --------------------------------------------------------------
# UDP Listener (Horus / Auto-RX)
# --------------------------------------------------------------
def listener():
    """Listen for incoming UDP telemetry packets."""
    global LAST_RX
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.bind(("", HORUS_UDP_PORT))

    while True:
        try:
            data, _ = s.recvfrom(65535)
            pkt = json.loads(data.decode("utf-8", "ignore"))

            if isinstance(pkt, dict) and pkt.get("type") == "PAYLOAD_SUMMARY":
                DATA.model = pkt.get("model", DATA.model)
                DATA.callsign = pkt.get("callsign", DATA.callsign)
                DATA.freq_hz = parse_freq(pkt.get("freq", DATA.freq_hz))
                DATA.altitude = float(pkt.get("altitude", DATA.altitude))
                DATA.speed = float(pkt.get("vel_h", DATA.speed))
                DATA.vel_v = float(pkt.get("vel_v", DATA.vel_v))
                DATA.batt = float(pkt.get("batt", DATA.batt))
                DATA.snr = float(pkt.get("snr", DATA.snr))
                LAST_RX = time.time()
        except Exception:
            time.sleep(0.1)

# --------------------------------------------------------------
# Main Loop
# --------------------------------------------------------------
def main():
    threading.Thread(target=listener, daemon=True).start()
    page = 0
    next_page = time.time() + PAGE_INTERVAL_S

    while True:
        state, age = rx_state()
        if state == "ACTIVE":
            if time.time() >= next_page:
                page = (page + 1) % len(PAGES)
                next_page = time.time() + PAGE_INTERVAL_S
            render_active(page)
        elif state == "RECENT":
            render_recent(age)
        else:
            render_idle()
        time.sleep(1.0 / REFRESH_HZ)

# --------------------------------------------------------------
# Entry Point
# --------------------------------------------------------------
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        device.clear()
        print("\nOLED Sonde Info Display stopped.")
