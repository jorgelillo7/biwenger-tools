import csv
import io
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload

# --- AUTENTICACIÓN Y SERVICIOS ---

def get_google_service(service_name, version, token_path, client_secrets_path, scopes):
    """
    Función genérica para autenticar y crear un servicio de Google.
    Maneja la creación y actualización automática del token.
    """
    creds = None
    token_file = token_path if os.path.exists(token_path) else 'token.json'

    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, scopes)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("ℹ️  El token de acceso ha caducado. Refrescando automáticamente...")
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"❌ Error al refrescar el token: {e}. Se requiere nueva autenticación.")
                if os.path.exists(token_file): os.remove(token_file)
                creds = None

        if not creds or not creds.valid:
            print("▶️  Iniciando flujo de autenticación (puede necesitar intervención manual).")
            if not os.path.exists(client_secrets_path):
                raise FileNotFoundError(f"El archivo de secretos de cliente '{client_secrets_path}' es necesario.")
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_path, scopes)
            creds = flow.run_local_server(port=0)

        try:
            if not os.path.exists(token_path): # No sobreescribir si es un secreto montado
                with open(token_file, 'w') as token:
                    token.write(creds.to_json())
                print(f"✅ Nuevo token guardado en '{token_file}'.")
        except Exception as e:
            print(f"⚠️  No se pudo reescribir el archivo del token (normal en Cloud Run): {e}")

    return build(service_name, version, credentials=creds)

# --- OPERACIONES CON GOOGLE DRIVE ---

def find_file_on_drive(service, name, folder_id):
    """Busca un archivo por nombre en una carpeta de Drive y devuelve su metadata."""
    query = f"name = '{name}' and '{folder_id}' in parents and trashed=false"
    response = service.files().list(q=query, spaces='drive', fields='files(id, name, modifiedTime)').execute()
    return response.get('files', [])[0] if response.get('files') else None

def download_csv_from_drive(service, file_id):
    """Descarga el contenido de un archivo CSV de Drive y lo devuelve como string."""
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    return fh.getvalue().decode('utf-8')

def download_csv_as_dict(service, file_id):
    """Descarga un CSV de Drive y lo devuelve como una lista de diccionarios."""
    if not file_id:
        raise FileNotFoundError("El ID del archivo CSV no fue proporcionado.")
    csv_content = download_csv_from_drive(service, file_id)
    return list(csv.DictReader(io.StringIO(csv_content)))

def upload_csv_to_drive(service, folder_id, filename, csv_content_string, existing_file_id):
    """Sube (o actualiza) un string con contenido CSV a una carpeta de Drive."""
    media = MediaIoBaseUpload(io.BytesIO(csv_content_string.encode('utf-8')), mimetype='text/csv', resumable=True)
    if existing_file_id:
        service.files().update(fileId=existing_file_id, media_body=media).execute()
        print(f"✅ Archivo '{filename}' actualizado en Drive.")
    else:
        file_metadata = {'name': filename, 'parents': [folder_id]}
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        permission = {'type': 'anyone', 'role': 'reader'}
        service.permissions().create(fileId=file.get('id'), body=permission).execute()
        print(f"✅ Archivo '{filename}' creado y compartido públicamente en Drive.")

# --- OPERACIONES CON GOOGLE SHEETS ---

def get_sheets_data(service, spreadsheet_id):
    """Lee y procesa los datos de todas las hojas de un Google Sheet."""
    sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheets = sheet_metadata.get('sheets', '')

    all_leagues_data = []
    for sheet in sheets:
        sheet_title = sheet.get("properties", {}).get("title", "Sin Título")
        result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=sheet_title).execute()
        values = result.get('values', [])

        if not values or len(values) < 6: continue

        league_info = {
            'nombre': values[0][1] if len(values[0]) > 1 else 'N/A',
            'descripcion': values[1][1] if len(values[1]) > 1 else 'N/A',
            'premio': values[2][1] if len(values[2]) > 1 else 'N/A',
            'headers': values[4],
            'rows': values[5:]
        }
        all_leagues_data.append(league_info)
    return all_leagues_data

