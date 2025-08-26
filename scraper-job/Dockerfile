FROM python:3.9-slim

WORKDIR /app

# Instala dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia solo core y scraper-job
COPY core/ ./core/
COPY scraper-job/ ./scraper-job/

WORKDIR /app/scraper-job

# Comando para ejecutar el job
CMD ["python", "get_messages.py"]
