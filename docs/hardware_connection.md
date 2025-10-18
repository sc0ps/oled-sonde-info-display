
# OLED Hardware Connection Guide

This document describes how to connect a 0.91" or 1.3" SSD1306 I²C OLED display to your Raspberry Pi for use with the **OLED Sonde Info Display** project.

---

## Required Hardware

- Raspberry Pi (any model with I²C support, e.g. Pi 3, 4, or Zero)
- SSD1306 OLED display (128×32 or 128×64 resolution)
- 4 jumper wires (female-to-female)

---

## Pin Connections

| OLED Pin | Raspberry Pi Pin | Description |
|-----------|------------------|--------------|
| VCC | Pin 1 (3.3V) | Power supply |
| GND | Pin 6 (GND) | Ground |
| SDA | Pin 3 (GPIO 2 / SDA1) | I²C Data |
| SCL | Pin 5 (GPIO 3 / SCL1) | I²C Clock |

Ensure I²C is enabled on your Pi:

```bash
sudo raspi-config
# → Interface Options → I2C → Enable
```

Then reboot your Pi and check that the display is detected:

```bash
sudo apt install -y i2c-tools
sudo i2cdetect -y 1
```

You should see a device address such as 0x3C (the default used by the display).

---

### Notes

- If your OLED uses address 0x3D, update the environment variable in docker-compose.yml:
```yml
- I2C_ADDR=0x3D
```
- 3.3V power is recommended, but most SSD1306 modules also support 5V.
- Cable length should be short (≤ 20 cm) for best I²C stability.

---

Once the wiring and Docker container are configured, the display will automatically show telemetry data from Radiosonde Auto-RX.

---

© 2025 Scops Owl Designs (Sc0ps)  
Licensed under the [GNU General Public License v3.0](./LICENSE).
You are free to use, modify, and distribute this software under the same license.  
For details, see the full license text in the repository.