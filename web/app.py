# app.py
from flask import Flask, render_template, request, session, redirect, url_for, flash
import csv
import requests
import io
import os
import json
from collections import defaultdict
from datetime import datetime, timedelta
from dateutil import parser
import pytz

# Importamos la configuración
import config

# Importaciones para Google Cloud
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY

# --- FUNCIONES ---

def get_google_service(service_name, version):
    """Función genérica para autenticar y crear un servicio de Google (Drive o Sheets)."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', config.SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secrets.json', config.SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build(service_name, version, credentials=creds)

def find_file_id_by_name(service, folder_id, filename):
    """Busca un archivo por nombre en Drive y devuelve su ID."""
    query = f"name = '{filename}' and '{folder_id}' in parents and trashed=false"
    response = service.files().list(q=query, spaces='drive', fields='files(id)').execute()
    files = response.get('files', [])
    return files[0]['id'] if files else None

def download_csv_data_by_id(service, file_id):
    """Descarga el contenido de un CSV a partir de su ID de archivo."""
    if not file_id:
        raise FileNotFoundError("El archivo CSV no fue encontrado en Google Drive.")
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    return list(csv.DictReader(io.StringIO(fh.getvalue().decode('utf-8'))))


def get_sheets_data(service, spreadsheet_id):
    """Lee y procesa los datos de todas las hojas de un Google Sheet."""
    sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheets = sheet_metadata.get('sheets', '')
    
    all_leagues = []
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
        all_leagues.append(league_info)
    return all_leagues

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

# --- RUTAS DE LA APLICACIÓN ---

@app.route('/')
def home():
    # Redirige a la temporada actual por defecto
    return redirect(url_for('comunicados', season=config.TEMPORADA_ACTUAL))

@app.route('/<season>/')
def comunicados(season):
    session['current_season'] = season # Guardamos la temporada en la sesión
    error = None
    paginated_messages = []
    page = 1
    total_pages = 1
    comunicados_only = []
    try:
        drive_service = get_google_service('drive', 'v3')
        filename = f"{config.COMUNICADOS_FILENAME_BASE}_{season}.csv"
        file_id = find_file_id_by_name(drive_service, config.GDRIVE_FOLDER_ID, filename)
        all_messages = download_csv_data_by_id(drive_service, file_id)

        comunicados_only = [m for m in all_messages if m.get('categoria', '').strip() == 'comunicado']
        
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * config.MESSAGES_PER_PAGE
        end = start + config.MESSAGES_PER_PAGE
        
        paginated_messages = comunicados_only[start:end]
        total_pages = (len(comunicados_only) + config.MESSAGES_PER_PAGE - 1) // config.MESSAGES_PER_PAGE
    except Exception as e:
        error = f"Ocurrió un error al cargar los comunicados de la temporada {season}: {e}"
        print(error)

    return render_template('index.html', 
                           messages=paginated_messages, 
                           all_comunicados=comunicados_only,
                           error=error, 
                           active_page='comunicados',
                           current_page=page,
                           total_pages=total_pages,
                           season=season,
                           temporada_actual=config.TEMPORADA_ACTUAL,
                           temporadas_disponibles=config.TEMPORADAS_DISPONIBLES)

@app.route('/<season>/salseo')
def salseo(season):
    session['current_season'] = season
    error = None
    datos_curiosos = []
    cesiones = []
    cronicas = []
    try:
        drive_service = get_google_service('drive', 'v3')
        filename = f"{config.COMUNICADOS_FILENAME_BASE}_{season}.csv"
        file_id = find_file_id_by_name(drive_service, config.GDRIVE_FOLDER_ID, filename)
        all_messages = download_csv_data_by_id(drive_service, file_id)

        datos_curiosos = [m for m in all_messages if m.get('categoria', '').strip() == 'dato']
        cesiones = [m for m in all_messages if m.get('categoria', '').strip() == 'cesion']
        cronicas = [m for m in all_messages if m.get('categoria', '').strip() == 'cronica']
    except Exception as e:
        error = f"Ocurrió un error al cargar los datos de la temporada {season}: {e}"
        print(error)

    return render_template('salseo.html', 
                           datos=datos_curiosos, 
                           cesiones=cesiones,
                           cronicas=cronicas,
                           error=error, 
                           active_page='salseo',
                           season=season,
                           temporada_actual=config.TEMPORADA_ACTUAL,
                           temporadas_disponibles=config.TEMPORADAS_DISPONIBLES)

@app.route('/<season>/participacion')
def participacion(season):
    session['current_season'] = season
    error = None
    stats = []
    try:
        drive_service = get_google_service('drive', 'v3')
        filename = f"{config.PARTICIPACION_FILENAME_BASE}_{season}.csv"
        file_id = find_file_id_by_name(drive_service, config.GDRIVE_FOLDER_ID, filename)
        participation_data = download_csv_data_by_id(drive_service, file_id)

        for row in participation_data:
            comunicados_count = len(row.get('comunicados', '').split(';')) if row.get('comunicados') else 0
            datos_count = len(row.get('datos', '').split(';')) if row.get('datos') else 0
            cesiones_count = len(row.get('cesiones', '').split(';')) if row.get('cesiones') else 0
            cronicas_count = len(row.get('cronicas', '').split(';')) if row.get('cronicas') else 0
            
            stats.append({
                'autor': row['autor'],
                'comunicados': comunicados_count,
                'datos': datos_count,
                'cesiones': cesiones_count,
                'cronicas': cronicas_count,
                'total': comunicados_count + datos_count + cesiones_count + cronicas_count
            })
        stats.sort(key=lambda item: item['total'], reverse=True)
    except Exception as e:
        error = f"Ocurrió un error al calcular las estadísticas de la temporada {season}: {e}"
        print(error)
        
    return render_template('participacion.html', 
                           stats=stats, 
                           error=error, 
                           active_page='participacion',
                           season=season,
                           temporada_actual=config.TEMPORADA_ACTUAL,
                           temporadas_disponibles=config.TEMPORADAS_DISPONIBLES)

@app.route('/<season>/ligas-especiales')
def ligas_especiales(season):
    session['current_season'] = season
    error = None
    leagues = []
    try:
        sheet_id = config.LIGAS_ESPECIALES_SHEETS.get(season)
        if not sheet_id:
            raise ValueError(f"No hay una hoja de Ligas Especiales configurada para la temporada {season}.")
        
        sheets_service = get_google_service('sheets', 'v4')
        leagues = get_sheets_data(sheets_service, sheet_id)
    except Exception as e:
        error = f"Ocurrió un error al cargar las ligas especiales: {e}"
        print(error)
        
    return render_template('ligas_especiales.html', 
                           leagues=leagues, 
                           error=error, 
                           active_page='ligas-especiales',
                           season=season,
                           temporada_actual=config.TEMPORADA_ACTUAL,
                           temporadas_disponibles=config.TEMPORADAS_DISPONIBLES)


# --- RUTAS FIJAS (NO DEPENDEN DE LA TEMPORADA) ---

@app.route('/palmares')
def palmares():
    seasons = defaultdict(lambda: defaultdict(list))
    error = None
    try:
        drive_service = get_google_service('drive', 'v3')
        file_id = find_file_id_by_name(drive_service, config.GDRIVE_FOLDER_ID, config.PALMARES_FILENAME)
        palmares_data = download_csv_data_by_id(drive_service, file_id)

        for row in palmares_data:
            season_data = row.get('temporada', '').strip()
            category = row.get('categoria', '').strip()
            value = row.get('valor', '').strip()
            
            if not season_data or not category: continue
            if category in ['multa', 'sancion', 'farolillo']:
                 seasons[season_data]['otros'].append({'tipo': category, 'valor': value})
            else:
                 seasons[season_data][category] = value
        sorted_seasons = sorted(seasons.items(), key=lambda item: item[0], reverse=True)
    except Exception as e:
        error = f"Ocurrió un error al cargar el palmarés: {e}"
        print(error)
        sorted_seasons = []
        
    return render_template('palmares.html', 
                           seasons=sorted_seasons, 
                           error=error, 
                           active_page='palmares',
                           season=session.get('current_season', config.TEMPORADA_ACTUAL),
                           temporada_actual=config.TEMPORADA_ACTUAL,
                           temporadas_disponibles=config.TEMPORADAS_DISPONIBLES)

@app.route('/reglamento')
def reglamento():
    error = None
    leagues = []
    try:
        # Usamos la temporada guardada en la sesión para cargar los datos correctos del índice
        sheet_id = config.LIGAS_ESPECIALES_SHEETS.get(session.get('current_season', config.TEMPORADA_ACTUAL))
        if sheet_id:
            sheets_service = get_google_service('sheets', 'v4')
            leagues = get_sheets_data(sheets_service, sheet_id)
    except Exception as e:
        error = f"Ocurrió un error al cargar los datos para el índice: {e}"
        print(error)

    return render_template('reglamento.html', 
                           leagues=leagues,
                           error=error,
                           active_page='reglamento',
                           season=session.get('current_season', config.TEMPORADA_ACTUAL),
                           temporada_actual=config.TEMPORADA_ACTUAL,
                           temporadas_disponibles=config.TEMPORADAS_DISPONIBLES)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    season = session.get('current_season', config.TEMPORADA_ACTUAL)
    if 'admin_logged_in' in session:
        file_statuses = []
        error = None
        try:
            drive_service = get_google_service('drive', 'v3')
            
            comunicados_actual = f"{config.COMUNICADOS_FILENAME_BASE}_{season}.csv"
            participacion_actual = f"{config.PARTICIPACION_FILENAME_BASE}_{season}.csv"
            dynamic_files = [comunicados_actual, participacion_actual]

            sheet_id = config.LIGAS_ESPECIALES_SHEETS.get(season)
            if sheet_id:
                dynamic_files.append(sheet_id) # También comprobamos el Sheet

            filenames_to_check = [comunicados_actual, participacion_actual, config.PALMARES_FILENAME]
            file_statuses = get_file_metadata(drive_service, config.GDRIVE_FOLDER_ID, filenames_to_check, dynamic_files)

            if sheet_id:
                sheet_metadata = drive_service.files().get(fileId=sheet_id, fields='name, modifiedTime').execute()
                dt_utc = parser.isoparse(sheet_metadata['modifiedTime'])
                dt_madrid = dt_utc.astimezone(pytz.timezone('Europe/Madrid'))
                formatted_date = dt_madrid.strftime('%d-%m-%Y a las %H:%M:%S')
                
                is_stale = (datetime.now(pytz.timezone('Europe/Madrid')) - dt_madrid) > timedelta(days=7)

                file_statuses.append({
                    'name': f"{sheet_metadata['name']} (Sheet)",
                    'status': 'Encontrado',
                    'last_updated': formatted_date,
                    'is_stale': is_stale
                })

        except Exception as e:
            error = f"No se pudo conectar con Google Drive para obtener el estado de los archivos: {e}"
        
        log_url = f"https://console.cloud.google.com/run/jobs/details/{config.CLOUD_RUN_REGION}/{config.CLOUD_RUN_JOB_NAME}/logs?project={config.GCP_PROJECT_ID}"

        return render_template('admin_panel.html', 
                               active_page='admin', 
                               file_statuses=file_statuses, 
                               log_url=log_url,
                               error=error,
                               season=season,
                               temporada_actual=config.TEMPORADA_ACTUAL,
                               temporadas_disponibles=config.TEMPORADAS_DISPONIBLES)

    if request.method == 'POST':
        if request.form.get('password') == config.ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin'))
        else:
            flash('Contraseña incorrecta. Inténtalo de nuevo.', 'error')
    
    return render_template('admin_login.html', 
                           active_page='admin',
                           season=session.get('current_season', config.TEMPORADA_ACTUAL),
                           temporada_actual=config.TEMPORADA_ACTUAL,
                           temporadas_disponibles=config.TEMPORADAS_DISPONIBLES)

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    flash('Has cerrado la sesión correctamente.', 'info')
    return redirect(url_for('home'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=True, host='0.0.0.0', port=port)
