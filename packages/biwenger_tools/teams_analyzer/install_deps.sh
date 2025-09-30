#!/bin/bash
set -e

apt-get update
apt-get install -y --no-install-recommends \
    python3 python3-pip chromium chromium-driver fonts-liberation \
    libnss3 libasound2 libatk-bridge2.0-0 libcups2 libdrm2 libgbm1 \
    libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libxtst6 \
    libatk1.0-0 libgtk-3-0 libx11-xcb1
rm -rf /var/lib/apt/lists/*
pip3 install --no-cache-dir -r /app/requirements_lock.txt