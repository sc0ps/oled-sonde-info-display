# ==============================================================
#  OLED Sonde Info Display
#  Lightweight Docker container to display Auto-RX telemetry
#  Maintained by Scops Owl Designs (Sc0ps)
# ==============================================================

FROM python:3.11-slim

LABEL maintainer="Scops Owl Designs <ScopsOwlDesigns@gmail.com>" \
      description="OLED Sonde Info Display — Auto-RX telemetry on SSD1306 OLED" \
      license="CC BY-NC 4.0"

# ---- Dependencies ----
RUN apt-get update && apt-get install -y --no-install-recommends \
    i2c-tools fonts-dejavu-core && \
    rm -rf /var/lib/apt/lists/*

# ---- Working directory ----
WORKDIR /app
COPY oled_display.py .

# ---- Python requirements ----
RUN pip install --no-cache-dir pillow luma.oled

# ---- Environment defaults ----
ENV CALLSIGN="CHANGE_ME" \
    HORUS_UDP_PORT=55673 \
    I2C_ADDR=0x3C \
    OLED_CONTRAST=160

# ---- Run the display script ----
CMD ["python", "oled_display.py"]
