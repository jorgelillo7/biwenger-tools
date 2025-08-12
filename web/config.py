# config.py
import os
from dotenv import load_dotenv

# Carga las variables del archivo .env si existe (para desarrollo local)
load_dotenv()

# --- CONFIGURACIÓN (leída desde el entorno) ---
# En local, se leen del .env. En Cloud Run, se leen de las variables de entorno del servicio.
COMUNICADOS_CSV_URL = os.getenv('COMUNICADOS_CSV_URL')
PARTICIPACION_CSV_URL = os.getenv('PARTICIPACION_CSV_URL')
PALMARES_CSV_URL = os.getenv('PALMARES_CSV_URL')
LIGAS_ESPECIALES_SHEET_ID = os.getenv('LIGAS_ESPECIALES_SHEET_ID')

# --- CONFIGURACIÓN NO CRÍTICA (valores fijos) ---
MESSAGES_PER_PAGE = 7
SCOPES = ['https://www.googleapis.com/auth/drive.readonly', 'https://www.googleapis.com/auth/spreadsheets.readonly']
