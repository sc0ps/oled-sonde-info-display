# ============================================================
# OLED Sonde Info Display - Raspberry Pi Build
# Maintainer: Sc0ps / ScopsOwlDesigns
# ============================================================

FROM python:3.11-slim

LABEL maintainer="ScopsOwlDesigns <ScopsOwlDesigns@gmail.com>"
LABEL description="OLED Sonde Info Display - Optimized for Raspberry Pi (ARM64/ARMv7)"

# ------------------------------------------------------------
# Install dependencies for Pillow & luma.oled
# ------------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7-dev \
    libtiff5-dev \
    libwebp-dev \
    tcl-dev tk-dev python3-tk \
    libxcb1-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ------------------------------------------------------------
# Install Python dependencies
# ------------------------------------------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ------------------------------------------------------------
# Copy application files
# ------------------------------------------------------------
COPY . .

# ------------------------------------------------------------
# Set environment defaults (can be overridden)
# ------------------------------------------------------------
ENV CALLSIGN=CHANGE_ME
ENV HORUS_UDP_PORT=55673
ENV I2C_ADDR=0x3C
ENV OLED_CONTRAST=160
ENV PAGE_INTERVAL_S=3.0
ENV REFRESH_HZ=2.0

# ------------------------------------------------------------
# Run the main app
# ------------------------------------------------------------
CMD ["python", "oled_display.py"]
