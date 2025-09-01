import csv
import io
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload

# --- AUTENTICACIÓN Y SERVICIOS ---

def get_google_service(api_name, api_version, service_account_file, scopes):
    """
    Devuelve un cliente autenticado usando Service Account.
    """
    credentials = service_account.Credentials.from_service_account_file(
        service_account_file,
        scopes=scopes
    )
    service = build(api_name, api_version, credentials=credentials)
    return service

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

