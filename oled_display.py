#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# OLED Sonde Info Display
# -----------------------
# Displays real-time telemetry from Radiosonde Auto-RX or Horus UDP feeds
# on an SSD1306 I²C OLED display (Raspberry Pi compatible).
#
# Author: Scops Owl Designs (Sc0ps)
# Contact: ScopsOwlDesigns@gmail.com
# Repository: https://github.com/sc0ps/oled-sonde-info-display
#
# License:
# This file is part of OLED Sonde Info Display.
#
# OLED Sonde Info Display is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# © 2025 Scops Owl Designs (Sc0ps)

import os, time, json, socket, threading, re
from PIL import Image, ImageDraw, ImageFont
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306

# ==== ENV ====
CALLSIGN = os.getenv("CALLSIGN", "Foxy_NL")
I2C_ADDR = int(os.getenv("I2C_ADDR", "0x3C"), 16)
ACTIVE_GAP_S = int(os.getenv("ACTIVE_GAP_S", "10"))
HOLD_LAST_S = int(os.getenv("HOLD_LAST_S", str(6 * 60)))
PAGE_INTERVAL_S = float(os.getenv("PAGE_INTERVAL_S", "3.0"))
REFRESH_HZ = float(os.getenv("REFRESH_HZ", "2"))
UDP_PORT = int(os.getenv("HORUS_UDP_PORT", "55673"))
OLED_CONTRAST = int(os.getenv("OLED_CONTRAST", "160"))
DEBUG = int(os.getenv("DEBUG", "0"))

# ==== Fonts ====
SANSB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def ttf(path, size, fallback=None):
    try:
        return ImageFont.truetype(path, size)
    except:
        return fallback or ImageFont.load_default()
FONT_S = ImageFont.load_default()
F10 = ttf(SANSB, 10, FONT_S)
F12 = ttf(SANSB, 12, FONT_S)
F14 = ttf(SANSB, 14, F12)
F16 = ttf(SANSB, 16, F14)

# ==== Data ====
class D:
    sonde_type = "—"
    callsign = "—"
    freq_hz = 0.0
    alt_m = 0.0
    vel_h = 0.0
    vel_v = 0.0
    batt_v = None
    snr_db = None

LAST_RX_TS = 0.0
page_idx = 0

# ==== OLED ====
serial = i2c(port=1, address=I2C_ADDR)
device = ssd1306(serial, width=128, height=32)
try:
    device.contrast(OLED_CONTRAST)
except:
    pass
W, H = device.width, device.height

# ==== helpers ====
def text_size(d, t, f):
    x0, y0, x1, y1 = d.textbbox((0, 0), t, font=f)
    return x1 - x0, y1 - y0

def label(d, t):
    w, _ = text_size(d, t, F10)
    d.text(((W - w) // 2, 0), t, font=F10, fill=255)

def center_row_with_unit(d, big, unit):
    F = F16 if text_size(d, big, F16)[0] <= 110 else F14
    bw, bh = text_size(d, big, F)
    uw, uh = text_size(d, unit, F10) if unit else (0, 0)
    total = bw + (2 if unit else 0) + uw
    x = (W - total) // 2
    y = (H - bh) // 2 + 4
    d.text((x, y), big, font=F, fill=255)
    if unit:
        d.text((x + bw + 2, y + bh - uh), unit, font=F10, fill=255)

def rx_state(now=None):
    now = now or time.time()
    age = now - LAST_RX_TS
    if age <= ACTIVE_GAP_S:
        return "ACTIVE", age
    if age <= HOLD_LAST_S:
        return "RECENT", age
    return "IDLE", age

def _parse_freq(v):
    try:
        if isinstance(v, str):
            m = re.search(r'([\d.]+)', v)
            val = float(m.group(1))
            return val * 1e6 if "MHz" in v else val
        return float(v)
    except:
        return 0.0

# ==== Pages ====
def page_MODEL(d):
    label(d, "MODEL")
    t = D.sonde_type or "—"
    w, _ = text_size(d, t, F14)
    d.text(((W - w) // 2, 12), t, font=F14, fill=255)

def page_CALL(d):
    label(d, "CALLSIGN")
    t = D.callsign or "—"
    w, _ = text_size(d, t, F14)
    d.text(((W - w) // 2, 12), t, font=F14, fill=255)

def page_FREQ(d):
    label(d, "FREQ")
    val = f"{D.freq_hz / 1e6:.3f}" if D.freq_hz else "—"
    center_row_with_unit(d, val, "MHz")

def page_ALT(d):
    label(d, "ALT")
    if D.alt_m >= 1000:
        val = f"{D.alt_m / 1000:.1f}"
        unit = "km"
    else:
        val = f"{int(D.alt_m)}"
        unit = "m"
    center_row_with_unit(d, val, unit)

def page_VELH(d):
    label(d, "SPEED")
    val = f"{abs(D.vel_h):.1f}"
    center_row_with_unit(d, val, "m/s")

def page_VELV(d):
    label(d, "VEL")
    sign = "▲" if D.vel_v > 0 else ("▼" if D.vel_v < 0 else "•")
    txt = f"{sign} {abs(D.vel_v):.1f}"
    center_row_with_unit(d, txt, "m/s")

def page_BATT(d):
    label(d, "BATT")
    if D.batt_v is not None:
        val = f"{D.batt_v:.2f}"
    else:
        val = "—"
    center_row_with_unit(d, val, "V")

def page_SNR(d):
    label(d, "SNR")
    val = f"{int(D.snr_db)}" if D.snr_db is not None else "—"
    center_row_with_unit(d, val, "dB")

PAGES = [page_MODEL, page_CALL, page_FREQ, page_ALT, page_VELH, page_VELV, page_BATT, page_SNR]

# ==== UDP ====
def on_new_rx(p):
    global LAST_RX_TS
    try:
        if isinstance(p, dict) and str(p.get("type", "")).upper() == "PAYLOAD_SUMMARY":
            D.sonde_type = p.get("model") or D.sonde_type
            D.callsign = p.get("callsign") or D.callsign
            D.freq_hz = _parse_freq(p.get("freq") or p.get("f_centre") or p.get("freq_hz"))
            if "altitude" in p: D.alt_m = float(p["altitude"])
            if "vel_h" in p: D.vel_h = float(p["vel_h"])
            if "vel_v" in p: D.vel_v = float(p["vel_v"])
            if "batt" in p: D.batt_v = float(p["batt"])
            if "snr" in p: D.snr_db = float(p["snr"])
            LAST_RX_TS = time.time()
            if DEBUG: print(f"[DEBUG] RX: {p}")
    except Exception as e:
        if DEBUG: print("[ERROR] RX error:", e)

def start_udp_listener():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    except:
        pass
    # luisteren op alle interfaces (broadcast)
    s.bind(("", UDP_PORT))
    print(f"[INFO] Listening for UDP broadcasts on port {UDP_PORT}...")

    def loop():
        while True:
            try:
                data, _ = s.recvfrom(65535)
                on_new_rx(json.loads(data.decode("utf-8", "ignore")))
            except Exception:
                time.sleep(0.05)
    threading.Thread(target=loop, daemon=True).start()

# ==== Main loop ====
def main():
    global page_idx
    start_udp_listener()
    next_sw = time.time() + PAGE_INTERVAL_S

    while True:
        now = time.time()
        state, age = rx_state(now)
        img = Image.new("1", (W, H))
        d = ImageDraw.Draw(img)

        if state == "ACTIVE":
            if now >= next_sw:
                page_idx = (page_idx + 1) % len(PAGES)
                next_sw = now + PAGE_INTERVAL_S
            PAGES[page_idx](d)

        elif state == "RECENT":
            label(d, "LAATST")
            t = f"{int(age)}s"
            w, _ = text_size(d, t, F14)
            d.text(((W - w) // 2, 12), t, font=F14, fill=255)

        else:  # IDLE
            w, _ = text_size(d, CALLSIGN, F16)
            d.text(((W - w) // 2, 8), CALLSIGN, font=F16, fill=255)

        device.display(img)
        time.sleep(1.0 / REFRESH_HZ)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        device.clear()
        device.show()
