import sys
import os
from gunicorn.app.wsgiapp import run

# Agregar el directorio padre (/app) al PYTHONPATH
# para que Python pueda encontrar el módulo 'web'
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

if __name__ == "__main__":
    sys.argv = [
        "gunicorn",
        "--bind",
        "0.0.0.0:8080",
        "web.app:app",  # Cambiar a web.app:app
    ]
    run()
