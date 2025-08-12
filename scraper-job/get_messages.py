# get_messages.py
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import csv
import hashlib
import os
import io
import json
import unidecode
from collections import defaultdict

# Importamos toda la configuración desde nuestro archivo config.py
import config

# Importaciones para Google Cloud
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# --- FUNCIONES AUXILIARES ---

def read_secret_from_file(secret_path):
    """Lee un secreto montado como un archivo por Cloud Run."""
    if os.path.exists(secret_path):
        with open(secret_path, 'r') as f:
            return f.read().strip()
    return None

# --- FUNCIONES DE GOOGLE DRIVE ---

def get_gdrive_service_oauth():
    """Autentica con Google Drive usando la configuración de config.py."""
    creds = None
    token_file = config.TOKEN_PATH if os.path.exists(config.TOKEN_PATH) else 'token.json'
    client_secrets_file = config.CLIENT_SECRETS_PATH if os.path.exists(config.CLIENT_SECRETS_PATH) else 'client_secrets.json'

    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, config.SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(client_secrets_file):
                raise FileNotFoundError(f"El archivo '{client_secrets_file}' es necesario.")
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, config.SCOPES)
            creds = flow.run_local_server(port=0)
        try:
            with open(token_file, 'w') as token:
                token.write(creds.to_json())
        except Exception as e:
            print(f"⚠️  No se pudo reescribir el token.json: {e}")

    service = build('drive', 'v3', credentials=creds)
    return service

def find_file_on_drive(service, name, folder_id):
    query = f"name = '{name}' and '{folder_id}' in parents and trashed=false"
    response = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    return response.get('files', [])[0] if response.get('files') else None

def download_csv_from_drive(service, file_id):
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    return fh.getvalue().decode('utf-8')

def upload_csv_to_drive(service, folder_id, filename, csv_content_string, existing_file):
    media = MediaIoBaseUpload(io.BytesIO(csv_content_string.encode('utf-8')), mimetype='text/csv', resumable=True)
    if existing_file:
        service.files().update(fileId=existing_file['id'], media_body=media).execute()
        print(f"✅ Archivo '{filename}' actualizado.")
    else:
        file_metadata = {'name': filename, 'parents': [folder_id]}
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        permission = {'type': 'anyone', 'role': 'reader'}
        service.permissions().create(fileId=file.get('id'), body=permission).execute()
        print(f"✅ Archivo '{filename}' creado y compartido públicamente.")

# --- FUNCIONES DE PROCESAMIENTO ---

def categorize_title(title):
    clean_title = title.strip().upper()
    if clean_title.startswith("DATO -") or clean_title.startswith("DATOS -"):
        return "dato"
    if unidecode.unidecode(clean_title).startswith("CESION -"):
        return "cesion"
    return "comunicado"

def process_participation(all_messages, user_map):
    """Procesa la lista de todos los mensajes y genera los datos de participación, incluyendo a todos los usuarios de la liga."""
    # Inicializa la participación con todos los usuarios de la liga.
    participation = {
        name: {"comunicado": [], "dato": [], "cesion": []}
        for name in user_map.values()
    }

    # Rellena con los mensajes existentes
    for msg in all_messages:
        author = msg.get('autor')
        category = msg.get('categoria')
        msg_id = msg.get('id_hash')
        # Nos aseguramos de que el autor está en nuestro diccionario de participación
        if author and category and msg_id and author in participation:
            if msg_id not in participation[author][category]:
                participation[author][category].append(msg_id)

    # Convertimos a formato de salida para el CSV
    output_data = []
    for author, categories in participation.items():
        output_data.append({
            'autor': author,
            'comunicados': ";".join(categories['comunicado']),
            'datos': ";".join(categories['dato']),
            'cesiones': ";".join(categories['cesion']),
        })
    return output_data

# --- FUNCIONES DE BIWENGER ---

def authenticate_and_get_session(email, password):
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
    session = requests.Session()
    login_headers = {
        'Accept': 'application/json, text/plain, */*',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'X-Lang': 'es',
        'X-Version': '628'
    }
    login_payload = {'email': email, 'password': password}

    print("▶️  Iniciando sesión en Biwenger...")
    login_response = session.post(config.LOGIN_URL, data=login_payload, headers=login_headers, verify=False)
    login_response.raise_for_status()
    token = login_response.json().get('token')
    if not token: raise Exception("Error en el login: No se recibió el token.")
    print("✅ Token de sesión obtenido.")

    session.headers.update(login_headers)
    session.headers.update({'Authorization': f'Bearer {token}'})

    print("▶️  Obteniendo datos de la cuenta...")
    account_response = session.get(config.ACCOUNT_URL, verify=False)
    account_response.raise_for_status()
    account_data = account_response.json()
    
    user_id = None
    leagues = account_data.get('data', {}).get('leagues', [])
    for league in leagues:
        if str(league.get('id')) == config.LEAGUE_ID:
            user_id = league.get('user', {}).get('id')
            break
    if not user_id: raise Exception("Error: No se pudo encontrar el ID de usuario para la liga especificada.")
    print(f"✅ ID de usuario ({user_id}) para la liga {config.LEAGUE_ID} obtenido correctamente.")

    session.headers.update({'X-League': str(config.LEAGUE_ID), 'X-User': str(user_id)})
    session.verify = False
    return session

def fetch_league_users(session):
    print("▶️  Obteniendo lista de usuarios de la liga...")
    response = session.get(config.LEAGUE_USERS_URL)
    response.raise_for_status()
    standings = response.json().get('data', {}).get('standings', [])
    if not standings: return {}
    user_map = {int(user['id']): user['name'] for user in standings if user.get('id')}
    print(f"✅ Mapa de {len(user_map)} usuarios creado.")
    return user_map

def fetch_board_messages(session):
    print(f"▶️  Obteniendo mensajes de jugadores del tablón...")
    board_response = session.get(config.BOARD_MESSAGES_URL)
    board_response.raise_for_status()
    return board_response.json()

# --- FUNCIÓN PRINCIPAL ---

def main():
    biwenger_email = read_secret_from_file(config.BIWENGER_EMAIL_PATH) or config.BIWENGER_EMAIL
    biwenger_password = read_secret_from_file(config.BIWENGER_PASSWORD_PATH) or config.BIWENGER_PASSWORD
    
    if not biwenger_email or not biwenger_password:
        print("⚠️ ¡Error! No se pudieron leer las credenciales de Biwenger.")
        return
        
    try:
        service = get_gdrive_service_oauth()
        comunicados_file = find_file_on_drive(service, config.COMUNICADOS_FILENAME, config.GDRIVE_FOLDER_ID)
        
        all_messages = []
        existing_ids = set()
        if comunicados_file:
            csv_content = download_csv_from_drive(service, comunicados_file['id'])
            reader = csv.DictReader(io.StringIO(csv_content))
            for row in reader:
                all_messages.append(row)
                existing_ids.add(row['id_hash'])
        
        session = authenticate_and_get_session(biwenger_email, biwenger_password)
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
                    date_str = datetime.fromtimestamp(timestamp).strftime('%d-%m-%Y %H:%M:%S') if timestamp else "N/A"
                    title = item.get('title', 'Sin título')
                    category = categorize_title(title)
                    author_name = item.get('author', {}).get('name')
                    author_id = item.get('author', {}).get('id')
                    if not author_name and author_id:
                        author_name = user_map.get(int(author_id))
                    if not author_name:
                        author_name = 'Autor Desconocido'
                    all_messages.append({
                        'id_hash': id_hash, 'fecha': date_str, 'autor': author_name,
                        'titulo': title, 'contenido': content_html, 'categoria': category
                    })
        
        if new_messages_found > 0:
            print(f"\n✅ Se han encontrado {new_messages_found} mensajes nuevos.")
            all_messages.sort(key=lambda x: datetime.strptime(x['fecha'], '%d-%m-%Y %H:%M:%S') if isinstance(x.get('fecha'), str) and x.get('fecha') != 'N/A' else datetime.min, reverse=True)
            
            output_comunicados = io.StringIO()
            writer_comunicados = csv.DictWriter(output_comunicados, fieldnames=['id_hash', 'fecha', 'autor', 'titulo', 'contenido', 'categoria'])
            writer_comunicados.writeheader()
            writer_comunicados.writerows(all_messages)
            upload_csv_to_drive(service, config.GDRIVE_FOLDER_ID, config.COMUNICADOS_FILENAME, output_comunicados.getvalue(), comunicados_file)

            # Se pasa el user_map para asegurar que todos los usuarios estén presentes
            participation_data = process_participation(all_messages, user_map)
            participation_file = find_file_on_drive(service, config.PARTICIPACION_FILENAME, config.GDRIVE_FOLDER_ID)
            output_part = io.StringIO()
            writer_part = csv.DictWriter(output_part, fieldnames=['autor', 'comunicados', 'datos', 'cesiones'])
            writer_part.writeheader()
            writer_part.writerows(participation_data)
            upload_csv_to_drive(service, config.GDRIVE_FOLDER_ID, config.PARTICIPACION_FILENAME, output_part.getvalue(), participation_file)
        else:
            print("\n✅ No hay mensajes nuevos.")

    except Exception as e:
        print(f"❌ Ocurrió un error inesperado: {e}")

if __name__ == '__main__':
    main()
