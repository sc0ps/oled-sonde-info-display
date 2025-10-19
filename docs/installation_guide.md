# Installation and Hardware Guide

This document describes how to install and run **OLED Sonde Info Display** on a Raspberry Pi, including both Docker and manual Python setups.

---

## 1. Hardware Connection

### Required Hardware

- Raspberry Pi (any model with I²C support: Pi 3, 4, or Zero)
- SSD1306 OLED display (128×32 or 128×64)
- 4 female-to-female jumper wires

### Wiring Table

| OLED Pin | Raspberry Pi Pin | Description |
|-----------|------------------|--------------|
| VCC | Pin 1 (3.3V) | Power supply |
| GND | Pin 6 (GND) | Ground |
| SDA | Pin 3 (GPIO 2 / SDA1) | I²C Data |
| SCL | Pin 5 (GPIO 3 / SCL1) | I²C Clock |

### Enable I²C on your Raspberry Pi

```bash
sudo raspi-config
# → Interface Options → I2C → Enable
sudo reboot
```
### After reboot, verify that the display is detected:

```bash
sudo apt install -y i2c-tools
sudo i2cdetect -y 1
```
You should see an address like 0x3C (default) or 0x3D.

If your display uses 0x3D, update it in your environment or docker-compose file:
```bash
- I2C_ADDR=0x3D
```
---


## 2. Docker Installation (Recommended)
### Clone the repository
```bash
git clone https://github.com/sc0ps/oled-sonde-info-display.git
cd oled-sonde-info-display
```

### Build and run the container
```bash
docker compose up -d --build
```

### Edit configuration

Before running, open and modify docker-compose.yml:
```bash
nano docker-compose.yml
```

Set your personal callsign and other options:

```bash
environment:
  - CALLSIGN=SC0PS
  - HORUS_UDP_PORT=55673
  - I2C_ADDR=0x3C
  - OLED_CONTRAST=160
  - PAGE_INTERVAL_S=3.0
  - REFRESH_HZ=2
```

Save and restart:
```bash
docker compose down
docker compose up -d --build
```

### Check logs
```bash
docker logs -f oled-sonde-info-display
```
---

## 3. Manual Python Installation (Alternative)

If you prefer to run the display script directly on your Pi without Docker:

### Install dependencies
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-pil python3-dev i2c-tools
pip install -r requirements.txt
```

### Set environment variables
```bash
export CALLSIGN=SC0PS
export HORUS_UDP_PORT=55673
export I2C_ADDR=0x3C
export OLED_CONTRAST=160
export PAGE_INTERVAL_S=3.0
export REFRESH_HZ=2
```

### Start the display
```bash
python3 oled_display.py
```

To stop it, press **CTRL+C**.

---

## 4. Removing or Rebuilding the Docker Container

To stop and remove the running container:
```bash
docker compose down
```

If you want to completely remove the container and image:
```bash
docker rm -f oled-sonde-info-display
docker image rm oled-sonde-info-display
```

To rebuild from scratch:
```bash
docker compose up -d --build
```

---

### 5. Troubleshooting

- **No display output:**
Check I²C wiring and confirm with sudo i2cdetect -y 1.
- **Wrong I²C address:**
Adjust I2C_ADDR in your compose file or environment.
- **Display too dim or too bright:**
Change OLED_CONTRAST (range 0–255).
- **No telemetry displayed:**
Ensure your Auto-RX or ChaseMapper is broadcasting to UDP port 55673.

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