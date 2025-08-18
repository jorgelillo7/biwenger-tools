# config.py
import os
from dotenv import load_dotenv

# Carga las variables del archivo .env para el desarrollo local
load_dotenv()

# --- CONFIGURACIÓN CRÍTICA (leída desde el entorno) ---
BIWENGER_EMAIL = os.getenv("BIWENGER_EMAIL")
BIWENGER_PASSWORD = os.getenv("BIWENGER_PASSWORD")

# --- CONFIGURACIÓN NO CRÍTICA (valores fijos) ---
LEAGUE_ID = "340703"
OUTPUT_FILENAME = "squads_export.csv"

# --- URLs DE LA API DE BIWENGER ---
BASE_URL = "https://biwenger.as.com/api/v2"
CF_BASE_URL = "https://cf.biwenger.com/api/v2"
LOGIN_URL = f"{BASE_URL}/auth/login"
ACCOUNT_URL = f"{BASE_URL}/account"
LEAGUE_DATA_URL = f"{BASE_URL}/league/{LEAGUE_ID}?fields=standings"
# CORRECCIÓN: Se pide explícitamente el campo 'owner' para obtener la cláusula
USER_SQUAD_URL = f"{BASE_URL}/user/{{manager_id}}?fields=players(id,owner)"
# URL para obtener la base de datos completa de jugadores
ALL_PLAYERS_DATA_URL = f"{CF_BASE_URL}/competitions/la-liga/data?lang=es&score=100"
