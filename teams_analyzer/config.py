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

# --- URLs DE LAS APIS ---
BASE_URL_BIWENGER = "https://biwenger.as.com/api/v2"
CF_BASE_URL_BIWENGER = "https://cf.biwenger.com/api/v2"
LOGIN_URL = f"{BASE_URL_BIWENGER}/auth/login"
ACCOUNT_URL = f"{BASE_URL_BIWENGER}/account"
LEAGUE_DATA_URL = f"{BASE_URL_BIWENGER}/league/{LEAGUE_ID}?fields=standings"
USER_SQUAD_URL = f"{BASE_URL_BIWENGER}/user/{{manager_id}}?fields=players(id,owner)"
ALL_PLAYERS_DATA_URL = f"{CF_BASE_URL_BIWENGER}/competitions/la-liga/data?lang=es&score=100"
MARKET_URL = f"{BASE_URL_BIWENGER}/market"

# NUEVO: URL de Jornada Perfecta para obtener las recomendaciones de la IA
JORNADA_PERFECTA_MERCADO_URL = "https://www.jornadaperfecta.com/mercado/"
ANALITICA_FANTASY_URL = "https://www.analiticafantasy.com/oraculo-fantasy"