import os
import pytz
from datetime import datetime, timedelta
from dateutil import parser

def read_secret_from_file(secret_path, fallback=None):
    """
    Lee un secreto montado como un archivo (típico en Cloud Run/Secrets Manager).
    Si la ruta no existe, devuelve un valor por defecto.
    """
    if secret_path and os.path.exists(secret_path):
        with open(secret_path, 'r') as f:
            return f.read().strip()
    return fallback

def get_file_metadata(service, folder_id, filenames, dynamic_files):
    """Obtiene la metadata de una lista de archivos y comprueba si están desactualizados."""
    statuses = []
    now_madrid = datetime.now(pytz.timezone('Europe/Madrid'))

    for name in filenames:
        query = f"name = '{name}' and '{folder_id}' in parents and trashed=false"
        response = service.files().list(q=query, spaces='drive', fields='files(id, name, modifiedTime)').execute()
        file = response.get('files', [])[0] if response.get('files') else None

        if file:
            dt_utc = parser.isoparse(file['modifiedTime'])
            dt_madrid = dt_utc.astimezone(pytz.timezone('Europe/Madrid'))
            formatted_date = dt_madrid.strftime('%d-%m-%Y a las %H:%M:%S')

            is_stale = False
            # Comprueba si el archivo debe ser revisado y si tiene más de 7 días
            if name in dynamic_files and (now_madrid - dt_madrid) > timedelta(days=7):
                is_stale = True

            statuses.append({'name': name, 'status': 'Encontrado', 'last_updated': formatted_date, 'is_stale': is_stale})
        else:
            statuses.append({'name': name, 'status': 'No Encontrado', 'last_updated': 'N/A', 'is_stale': False})
    return statuses