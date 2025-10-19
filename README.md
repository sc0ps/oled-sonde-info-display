# OLED Sonde Info Display
[![Version](https://img.shields.io/badge/Version-1.2-green.svg)](#)
[![License](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Stable-success.svg)](#)
[![Python](https://img.shields.io/badge/Python-3.11%2B-yellow.svg)](#)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)](#)
[![Platform](https://img.shields.io/badge/Platform-Raspberry%20Pi-lightgrey.svg)](#)

A non-commercial open-source project by **Scops Owl Designs (Sc0ps)**  
© 2025 Scops Owl Designs — Licensed under the [GNU General Public License v3.0](LICENSE)

---

## Overview

**OLED Sonde Info Display** is a lightweight Python-based application that visualizes real-time telemetry from **Radiosonde Auto-RX** or **Horus UDP** feeds on an SSD1306 I²C OLED display (0.91" or 1.3").  

It automatically cycles through multiple data pages including:

| Page | Description | Example |
|------|--------------|----------|
| Model | Sonde model/type | RS41-SGP |
| Callsign | Payload callsign | X2712291 |
| Frequency | Downlink frequency | 403.900 MHz |
| Altitude | Current altitude (auto m/km) | 31.3 km |
| Speed | Horizontal velocity | 15 m/s |
| Vertical Speed | Ascent/descent rate | ▲ 6.2 m/s |
| Battery | Battery voltage | 3.3 V |
| SNR | Signal-to-noise ratio | 12.8 dB |

When no telemetry is received, the OLED displays your configured **CALLSIGN**.  
After telemetry stops, the last data remains visible for six minutes before returning to idle mode.

---

## Features

- Lightweight and minimal CPU usage  
- Automatic page cycling and real-time updates  
- Compatible with **Radiosonde Auto-RX** and **ChaseMapper** UDP feeds  
- Plug & play via I²C on Raspberry Pi  
- Fully configurable through environment variables  
- Can run in **Docker** or directly in **Python**

---
## OLED Display Workflow

Below is the typical behavior of the **OLED Sonde Info Display** during operation:

### 1. Startup / Idle mode
The display shows your callsign when no sonde is detected or at startup.

![Idle Screen](assets/idle.gif)

---

### 2. Active telemetry reception
When telemetry packets are received from a radiosonde, the display cycles through
live data pages such as model, callsign, frequency, altitude, speed, and signal strength.

![Active Telemetry Loop](assets/active.gif)

---

### 3. No signal
If the sonde stops transmitting, the display shows **"NO SIGNAL"** and a timer indicating
how long it has been since the last received packet (up to 6 minutes).

![No Signal](assets/no_signal.gif)

If the sonde starts transmitting again within this 6-minute period,
the display will automatically resume showing live telemetry information.
After the 6-minute timeout, if no new data is received, the display
returns to idle mode showing your callsign.

---

## Documentation

For installation, configuration, and hardware setup instructions, see:

[**docs/installation_guide.md**](docs/installation_guide.md)

---

## Requirements

- Raspberry Pi (or compatible SBC with I²C enabled)  
- SSD1306 OLED display (128×32 or 128×64)  
- Radiosonde Auto-RX or ChaseMapper UDP feed  
- Python 3.11+ or Docker with Docker Compose installed  

---

## Configuration Variables

| Variable | Description | Default |
|-----------|--------------|----------|
| `CALLSIGN` | Your personal callsign shown in idle mode | `CHANGE_ME` |
| `HORUS_UDP_PORT` | UDP port used by Auto-RX / ChaseMapper | `55673` |
| `I2C_ADDR` | OLED I²C address | `0x3C` |
| `OLED_CONTRAST` | Display brightness (0–255) | `160` |
| `PAGE_INTERVAL_S` | Seconds between page switches | `3.0` |
| `REFRESH_HZ` | Display refresh rate | `2` |

These values can be set in `docker-compose.yml` or as environment variables when running manually.

---

## Example Usage

### Run with Docker

```bash
git clone https://github.com/sc0ps/oled-sonde-info-display.git
cd oled-sonde-info-display
docker compose up -d --build
```
### Run without Docker

```bash
pip install -r requirements.txt
python3 oled_display.py
```

---

## License

This project is licensed under the **GNU General Public License v3.0 (GPLv3)**.

You are free to use, modify, and redistribute this software under the same terms.  
There is no warranty; use at your own risk.

Full license text: [GNU GPL v3](https://www.gnu.org/licenses/gpl-3.0.html)

---

## Author

**Scops Owl Designs (Sc0ps)**  
Email: [ScopsOwlDesigns@gmail.com](mailto:ScopsOwlDesigns@gmail.com)

© 2025 Scops Owl Designs  
Licensed under the GNU GPL v3.0
