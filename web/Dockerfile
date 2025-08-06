# Usa una imagen base oficial de Python
FROM python:3.9-slim

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Copia el archivo de requerimientos y los instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de los archivos de la aplicación
COPY . .

# Expone el puerto en el que Gunicorn se ejecutará
EXPOSE 8080

# Comando para ejecutar la aplicación usando Gunicorn
# Gunicorn es un servidor de producción más robusto que el de desarrollo de Flask
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
