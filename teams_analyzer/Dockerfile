# Usa Debian Bookworm slim
FROM debian:bookworm-slim

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/usr/bin:${PATH}"

WORKDIR /app

# Instala Python, dependencias y Chromium nativo ARM64
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    unzip \
    ca-certificates \
    wget \
    gnupg \
    chromium \
    chromium-driver \
    fonts-liberation \
    libnss3 \
    libxss1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libgbm1 \
    libnspr4 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libxtst6 \
    libxcursor1 \
    libatk1.0-0 \
    libgtk-3-0 \
    libx11-xcb1 \
    libxcb1 \
    libxi6 \
    && rm -rf /var/lib/apt/lists/*

# Copia requisitos y crea entorno virtual
COPY teams_analyzer/requirements.txt .
RUN python3 -m venv venv
RUN venv/bin/pip install --no-cache-dir -r requirements.txt

# Copia el resto del código
COPY core/ ./core/
COPY teams_analyzer/ ./teams_analyzer/

# Comando por defecto
CMD ["/app/venv/bin/python3", "-u", "-m", "teams_analyzer.teams_analyzer"]
