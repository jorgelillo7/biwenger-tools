FROM python:3.9-slim

WORKDIR /app

COPY web/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY core/ ./core/
COPY web/ ./web/

WORKDIR /app/web

ENV PYTHONPATH=/app

EXPOSE 8080

# Gunicorn arranca usando el paquete web
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "web.app:app"]
