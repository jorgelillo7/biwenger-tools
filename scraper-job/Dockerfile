# Usa una imagen base oficial de Python
FROM python:3.9-slim

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Copia el archivo de requerimientos y los instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el script de Python
COPY get_messages.py .

# Comando para ejecutar el script cuando el job se inicie
CMD ["python", "get_messages.py"]
