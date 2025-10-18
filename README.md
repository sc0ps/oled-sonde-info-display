# OLED Sonde Info Display  
[![Version](https://img.shields.io/badge/Version-1.1-green.svg)](#)
[![License](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Stable-success.svg)](#)
[![Python](https://img.shields.io/badge/Python-3.11%2B-yellow.svg)](#)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)](#)
[![Platform](https://img.shields.io/badge/Platform-Raspberry%20Pi-lightgrey.svg)](#)

A non-commercial open-source project by **Scops Owl Designs (Sc0ps)**  
© 2025 Scops Owl Designs — Licensed under the [GNU General Public License v3.0](LICENSE)


## Overview

**OLED Sonde Info Display** is a lightweight Python-based Docker container that displays real-time telemetry from **Radiosonde Auto-RX** or **Horus UDP** data streams on an SSD1306 I²C OLED screen (0.91" or 1.3").

It cycles automatically through telemetry pages including:

| Page | Description | Example |
|------|--------------|----------|
| Model | Sonde model/type | RS41-SGP |
| Callsign | Payload callsign | X2712291 |
| Frequency | Downlink frequency | 403.900 MHz |
| Altitude | Current altitude (auto switches between m/km) | 31.3 km |
| Speed | Horizontal speed | 15 km/h |
| Vertical Speed | Ascent/descent rate | ▲ 6.2 m/s |
| Battery | Battery voltage | 3.3 V |
| SNR | Signal-to-noise ratio | 12.8 dB |

When no signal is received, your **CALLSIGN** is displayed.  
After telemetry stops, the last received data remains visible for 6 minutes before returning to idle mode.

---

## Features

- Lightweight and minimal footprint  
- Automatic page cycling and refresh  
- Compatible with **Radiosonde Auto-RX** and **ChaseMapper** UDP feeds  
- Plug & play on Raspberry Pi via `/dev/i2c-1`  
- Fully configurable via environment variables  
- Distributed as a Docker container for easy deployment  

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/sc0ps/oled-sonde-info-display.git
cd oled-sonde-info-display
```

### 2. Build and start the container
```bash
docker compose up -d --build
```

### 3. Check logs
```bash
docker logs -f oled-sonde-info-display
```
---

### Configuration

You must set your own callsign before starting the container.

By default, the compose file uses:
```yml
CALLSIGN=CHANGE_ME
```

You need to edit the file docker-compose.yml located in the root of this project folder and replace CHANGE_ME with your personal callsign — for example: sc0ps.

You can edit it directly on your Raspberry Pi using:

```bash
nano docker-compose.yml
```

Then modify this section:
```yml
services:
  oled:
    build: .
    container_name: oled-sonde-info-display
    restart: always
    privileged: true
    devices:
      - /dev/i2c-1:/dev/i2c-1
    environment:
      - CALLSIGN=Foxy_NL          # REQUIRED: your callsign
      - HORUS_UDP_PORT=55673      # UDP port used by Auto-RX / ChaseMapper
      - I2C_ADDR=0x3C             # I²C address of your OLED
      - OLED_CONTRAST=160         # Display brightness (0–255)
      - PAGE_INTERVAL_S=3.0       # Seconds per page
      - REFRESH_HZ=2              # Screen refresh rate
```

After editing the file, rebuild and restart:

```bash
docker compose up -d --build
```

---

### Hardware Setup

Wiring details for connecting the OLED display to the Raspberry Pi can be found here: [hardware_connection](docs/hardware_connection.md)

---

### Requirements

- Raspberry Pi (or compatible SBC running Linux)
- Radiosonde Auto-RX and/or ChaseMapper UDP feed (port 55673)
- I²C OLED display (SSD1306 128×32 or 128×64)
- Docker and Docker Compose installed

---

### License

This project is licensed under the **GNU General Public License v3.0 (GPLv3)**.

You are free to:

- Use, copy, and modify this software  
- Distribute copies or modified versions  

**Under the following terms:**
- You must include the original license and copyright notice  
- Any modifications must also be released under GPLv3  
- There is no warranty; use at your own risk  

Full license text: [GNU GPL v3](https://www.gnu.org/licenses/gpl-3.0.html)

---

## Author

**Scops Owl Designs (Sc0ps)**    
Email: [ScopsOwlDesigns@gmail.com](mailto:ScopsOwlDesigns@gmail.com)

---

© 2025 Scops Owl Designs (Sc0ps)  
Licensed under the [GNU General Public License v3.0](./LICENSE).
You are free to use, modify, and distribute this software under the same license.  
For details, see the full license text in the repository.
