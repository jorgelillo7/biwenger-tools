# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import csv
import hashlib
import os
import io
import json
from dotenv import load_dotenv

# Importaciones para Google Cloud
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# --- CONFIGURACIÓN ---
LEAGUE_ID = "340703"

# --- CONFIGURACIÓN DE GOOGLE DRIVE ---
GDRIVE_FOLDER_ID = '1DEY5pzf0iyZi3uxAFsjnE0tgVf8YiYI7'
CSV_FILENAME = 'biwenger_comunicados.csv'
SCOPES = ['https://www.googleapis.com/auth/drive']

# --- CONFIGURACIÓN DE SECRETOS ---
# CAMBIO: Rutas únicas para cada secreto para evitar conflictos de montaje
BIWENGER_EMAIL_PATH = "/biwenger_email/biwenger-email" 
BIWENGER_PASSWORD_PATH = "/biwenger_password/biwenger-password"
CLIENT_SECRETS_PATH = "/gdrive_client/client_secrets.json"
TOKEN_PATH = "/gdrive_token/token.json"
# -------------------

# --- FUNCIONES AUXILIARES ---

def read_secret_from_file(secret_path):
    """Lee un secreto montado como un archivo por Cloud Run."""
    if os.path.exists(secret_path):
        with open(secret_path, 'r') as f:
            return f.read().strip()
    return None

# --- FUNCIONES DE GOOGLE DRIVE ---

def get_gdrive_service_oauth():
    """
    Autentica con Google Drive. Usa secretos en Cloud Run o archivos locales en desarrollo.
    """
    creds = None
    
    # Determina la ruta de los archivos de credenciales (Cloud Run vs Local)
    token_file = TOKEN_PATH if os.path.exists(TOKEN_PATH) else 'token.json'
    client_secrets_file = CLIENT_SECRETS_PATH if os.path.exists(CLIENT_SECRETS_PATH) else 'client_secrets.json'

    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("▶️  Refrescando token de acceso de Drive...")
            creds.refresh(Request())
        else:
            print("▶️  Se necesita autorización. Abriendo navegador para iniciar sesión (solo en local)...")
            if not os.path.exists(client_secrets_file):
                raise FileNotFoundError("El archivo 'client_secrets.json' es necesario para la autenticación local.")
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Guarda las credenciales actualizadas para la próxima ejecución
        try:
            with open(token_file, 'w') as token:
                token.write(creds.to_json())
        except Exception as e:
            print(f"⚠️  No se pudo reescribir el token.json (esto es normal en Cloud Run): {e}")

    if not creds:
        raise Exception("No se pudieron obtener las credenciales de Google Drive.")

    print("✅ Autenticación con Google Drive correcta.")
    service = build('drive', 'v3', credentials=creds)
    return service

def find_file_on_drive(service, name, folder_id):
    """Busca un archivo por nombre en una carpeta específica de Drive."""
    query = f"name = '{name}' and '{folder_id}' in parents and trashed=false"
    response = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    return response.get('files', [])[0] if response.get('files') else None

def load_messages_from_drive(service, file_id):
    """Descarga el CSV desde Drive y lo carga en memoria."""
    print(f"▶️  Descargando CSV existente desde Google Drive (ID: {file_id})...")
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    csv_content = fh.getvalue().decode('utf-8')
    csv_file = io.StringIO(csv_content)
    
    existing_ids = set()
    messages = []
    reader = csv.DictReader(csv_file)
    for row in reader:
        existing_ids.add(row['id_hash'])
        try:
            dt_object = datetime.strptime(row['fecha'], '%d-%m-%Y %H:%M:%S')
            row['timestamp'] = int(dt_object.timestamp())
        except (ValueError, TypeError):
            row['timestamp'] = 0
        messages.append(row)
    print(f"✅ Se han cargado {len(messages)} mensajes existentes desde Google Drive.")
    return existing_ids, messages

def upload_or_update_drive_file(service, folder_id, filename, messages_data, existing_file):
    """Sube o actualiza el archivo CSV en Google Drive."""
    output = io.StringIO()
    fieldnames = ['id_hash', 'fecha', 'autor', 'titulo', 'contenido']
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for message in messages_data:
        row_to_write = message.copy()
        row_to_write.pop('timestamp', None)
        writer.writerow(row_to_write)
    
    csv_bytes = output.getvalue().encode('utf-8')
    media = MediaIoBaseUpload(io.BytesIO(csv_bytes), mimetype='text/csv', resumable=True)
    
    if existing_file:
        print(f"▶️  Actualizando archivo '{filename}' en Google Drive...")
        service.files().update(fileId=existing_file['id'], media_body=media).execute()
        print(f"✅ Archivo actualizado (ID: {existing_file['id']}).")
    else:
        print(f"▶️  Subiendo nuevo archivo '{filename}' a Google Drive...")
        file_metadata = {'name': filename, 'parents': [folder_id]}
        file = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
        print(f"✅ Archivo creado (ID: {file.get('id')}).")
        print("▶️  Haciendo el archivo público...")
        permission = {'type': 'anyone', 'role': 'reader'}
        service.permissions().create(fileId=file.get('id'), body=permission).execute()
        print(f"✅ ¡Archivo compartido públicamente! Enlace: {file.get('webViewLink')}")

# --- FUNCIONES DE BIWENGER ---

def authenticate_and_get_session(email, password):
    """Inicia sesión en Biwenger y devuelve una sesión autenticada."""
    login_url = "https://biwenger.as.com/api/v2/auth/login"
    account_url = "https://biwenger.as.com/api/v2/account"
    
    session = requests.Session()
    login_headers = {
        'Accept': 'application/json, text/plain, */*',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'X-Lang': 'es',
        'X-Version': '628'
    }
    login_payload = {'email': email, 'password': password}

    print("▶️  Iniciando sesión en Biwenger...")
    login_response = session.post(login_url, data=login_payload, headers=login_headers)
    login_response.raise_for_status()
    token = login_response.json().get('token')
    if not token: raise Exception("Error en el login: No se recibió el token.")
    print("✅ Token de sesión obtenido.")

    session.headers.update(login_headers)
    session.headers.update({'Authorization': f'Bearer {token}'})

    print("▶️  Obteniendo datos de la cuenta...")
    account_response = session.get(account_url)
    account_response.raise_for_status()
    account_data = account_response.json()
    
    user_id = None
    leagues = account_data.get('data', {}).get('leagues', [])
    for league in leagues:
        if str(league.get('id')) == LEAGUE_ID:
            user_id = league.get('user', {}).get('id')
            break
    if not user_id: raise Exception("Error: No se pudo encontrar el ID de usuario para la liga especificada.")
    print(f"✅ ID de usuario ({user_id}) para la liga {LEAGUE_ID} obtenido correctamente.")

    session.headers.update({'X-League': str(LEAGUE_ID), 'X-User': str(user_id)})
    return session

def fetch_league_users(session):
    """Obtiene todos los usuarios de la liga y crea un mapa de ID a nombre."""
    print("▶️  Obteniendo lista de usuarios de la liga...")
    league_url = f"https://biwenger.as.com/api/v2/league/{LEAGUE_ID}?fields=standings"
    response = session.get(league_url)
    response.raise_for_status()
    standings = response.json().get('data', {}).get('standings', [])
    if not standings:
        print("⚠️  No se encontraron usuarios en la liga. El mapa de autores estará vacío.")
        return {}
    
    user_map = {int(user['id']): user['name'] for user in standings if user.get('id')}
    print(f"✅ Mapa de {len(user_map)} usuarios creado.")
    return user_map

def fetch_board_messages(session):
    """Obtiene los mensajes del tablón de la liga."""
    board_url = f"https://biwenger.as.com/api/v2/league/{LEAGUE_ID}/board?type=text&limit=200"
    print(f"▶️  Obteniendo mensajes de jugadores del tablón...")
    board_response = session.get(board_url)
    board_response.raise_for_status()
    return board_response.json()

# --- FUNCIÓN PRINCIPAL ---

def main():
    """Función principal que orquesta todo el proceso."""
    # Lee las credenciales de Biwenger desde los archivos de secretos (Cloud Run)
    BIWENGER_EMAIL = read_secret_from_file(BIWENGER_EMAIL_PATH)
    BIWENGER_PASSWORD = read_secret_from_file(BIWENGER_PASSWORD_PATH)

    # Si no los encuentra (ej. en local), usa las variables de entorno
    if not BIWENGER_EMAIL:
        print("ℹ️  No se encontró el secreto de email, leyendo de variable de entorno...")
        load_dotenv()
        BIWENGER_EMAIL = os.getenv("BIWENGER_EMAIL")
    if not BIWENGER_PASSWORD:
        print("ℹ️  No se encontró el secreto de contraseña, leyendo de variable de entorno...")
        load_dotenv()
        BIWENGER_PASSWORD = os.getenv("BIWENGER_PASSWORD")
    
    if not BIWENGER_EMAIL or not BIWENGER_PASSWORD:
        print("⚠️ ¡Error! No se pudieron leer las credenciales de Biwenger.")
        return
        
    try:
        service = get_gdrive_service_oauth()
        # CORRECCIÓN: Los argumentos estaban intercambiados.
        existing_file = find_file_on_drive(service, CSV_FILENAME, GDRIVE_FOLDER_ID)
        
        existing_ids, all_messages = set(), []
        if existing_file:
            existing_ids, all_messages = load_messages_from_drive(service, existing_file['id'])
        else:
            print("ℹ️  No se encontró el archivo en Drive. Se creará uno nuevo.")

        session = authenticate_and_get_session(BIWENGER_EMAIL, BIWENGER_PASSWORD)
        user_map = fetch_league_users(session)
        board_data = fetch_board_messages(session)

        new_messages_found = 0
        if 'data' in board_data and board_data['data']:
            for item in board_data['data']:
                timestamp = item.get('date')
                content_html = item.get('content', '')
                
                soup = BeautifulSoup(content_html, 'html.parser')
                content_text_for_hash = soup.get_text(separator=' ', strip=True)
                unique_string = f"{timestamp}{content_text_for_hash}"
                id_hash = hashlib.sha256(unique_string.encode('utf-8')).hexdigest()

                if id_hash not in existing_ids:
                    new_messages_found += 1
                    existing_ids.add(id_hash)
                    
                    date_str = datetime.fromtimestamp(timestamp).strftime('%d-%m-%Y %H:%M:%S') if timestamp else "N/A"
                    title = item.get('title', 'Sin título')
                    
                    author_name = item.get('author', {}).get('name')
                    author_id = item.get('author', {}).get('id')
                    
                    if not author_name and author_id:
                        author_name = user_map.get(int(author_id))
                    
                    if not author_name:
                        author_name = 'Autor Desconocido'
                        if author_id:
                            print(f"⚠️  No se encontró el nombre para el autor con ID: {author_id}. (Título: '{title}')")
                    
                    all_messages.append({
                        'id_hash': id_hash, 'fecha': date_str, 'autor': author_name,
                        'titulo': title, 'contenido': content_html, 'timestamp': timestamp
                    })
        
        if new_messages_found > 0:
            print(f"\n✅ Se han encontrado {new_messages_found} mensajes nuevos.")
            all_messages.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
            upload_or_update_drive_file(service, GDRIVE_FOLDER_ID, CSV_FILENAME, all_messages, existing_file)
        else:
            print("\n✅ No hay mensajes nuevos. No se necesita actualizar el archivo en Drive.")

    except Exception as e:
        print(f"❌ Ocurrió un error inesperado: {e}")

if __name__ == '__main__':
    main()
