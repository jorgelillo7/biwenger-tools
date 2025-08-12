# config.py
import os
from dotenv import load_dotenv

# Carga las variables del archivo .env para el desarrollo local
load_dotenv()

# --- CONFIGURACIÓN CRÍTICA (leída desde el entorno) ---
# En local, se leen del .env. En Cloud Run, se leen de los secretos montados.
BIWENGER_EMAIL = os.getenv("BIWENGER_EMAIL")
BIWENGER_PASSWORD = os.getenv("BIWENGER_PASSWORD")
GDRIVE_FOLDER_ID = os.getenv("GDRIVE_FOLDER_ID")

# --- CONFIGURACIÓN NO CRÍTICA (valores fijos) ---
LEAGUE_ID = "340703"
COMUNICADOS_FILENAME = "biwenger_comunicados.csv"
PARTICIPACION_FILENAME = "biwenger_participacion.csv"
SCOPES = ['https://www.googleapis.com/auth/drive']

# --- URLs DE LA API DE BIWENGER ---
BASE_URL = "https://biwenger.as.com/api/v2"
LOGIN_URL = f"{BASE_URL}/auth/login"
ACCOUNT_URL = f"{BASE_URL}/account"
LEAGUE_USERS_URL = f"{BASE_URL}/league/{LEAGUE_ID}?fields=standings"
BOARD_MESSAGES_URL = f"{BASE_URL}/league/{LEAGUE_ID}/board?type=text&limit=200"

# Rutas donde Cloud Run montará los secretos como archivos
BIWENGER_EMAIL_PATH = "/biwenger_email/biwenger-email"
BIWENGER_PASSWORD_PATH = "/biwenger_password/biwenger-password"
CLIENT_SECRETS_PATH = "/gdrive_client/client_secrets.json"
TOKEN_PATH = "/gdrive_token/token.json"
