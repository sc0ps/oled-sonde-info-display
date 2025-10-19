FROM --platform=linux/arm64 python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    i2c-tools fonts-dejavu-core && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY oled_display.py /app/oled_display.py

ENV TZ=Europe/Amsterdam
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD i2cdetect -y 1 || exit 1

CMD ["python", "/app/oled_display.py"]
