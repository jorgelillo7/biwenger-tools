# app.py
from flask import Flask, render_template, request, session, redirect, url_for, flash
import csv
import requests
import io
import os
import json
from collections import defaultdict
from datetime import datetime
from dateutil import parser
import pytz

# Importamos la configuración
import config

# Importaciones para Google Cloud
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

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

def download_csv_data(csv_url):
    """Descarga y parsea un CSV desde una URL."""
    if not csv_url: raise ValueError("La URL del CSV no está configurada.")
    cache_buster_url = f"{csv_url}&timestamp={datetime.now().timestamp()}"
    response = requests.get(cache_buster_url)
    response.raise_for_status()
    return list(csv.DictReader(io.StringIO(response.text)))

def get_file_metadata(service, folder_id, filenames):
    """Obtiene la metadata de una lista de archivos CSV en Google Drive."""
    statuses = []
    for name in filenames:
        query = f"name = '{name}' and '{folder_id}' in parents and trashed=false"
        response = service.files().list(q=query, spaces='drive', fields='files(id, name, modifiedTime)').execute()
        file = response.get('files', [])[0] if response.get('files') else None
        
        if file:
            dt_utc = parser.isoparse(file['modifiedTime'])
            dt_madrid = dt_utc.astimezone(pytz.timezone('Europe/Madrid'))
            formatted_date = dt_madrid.strftime('%d-%m-%Y a las %H:%M:%S')
            statuses.append({'name': name, 'status': 'Encontrado', 'last_updated': formatted_date})
        else:
            statuses.append({'name': name, 'status': 'No Encontrado', 'last_updated': 'N/A'})
    return statuses

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

# --- RUTAS ---

@app.route('/')
def comunicados():
    error = None
    paginated_messages = []
    page = 1
    total_pages = 1
    comunicados_only = []
    try:
        all_messages = download_csv_data(config.COMUNICADOS_CSV_URL)
        comunicados_only = [m for m in all_messages if m.get('categoria', '').strip() == 'comunicado']
        
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * config.MESSAGES_PER_PAGE
        end = start + config.MESSAGES_PER_PAGE
        
        paginated_messages = comunicados_only[start:end]
        total_pages = (len(comunicados_only) + config.MESSAGES_PER_PAGE - 1) // config.MESSAGES_PER_PAGE
    except Exception as e:
        error = f"Ocurrió un error al cargar los comunicados: {e}"
        print(error)

    return render_template('index.html', 
                           messages=paginated_messages, 
                           all_comunicados=comunicados_only,
                           error=error, 
                           active_page='comunicados',
                           current_page=page,
                           total_pages=total_pages)

@app.route('/salseo')
def salseo():
    error = None
    datos_curiosos = []
    cesiones = []
    try:
        all_messages = download_csv_data(config.COMUNICADOS_CSV_URL)
        datos_curiosos = [m for m in all_messages if m.get('categoria', '').strip() == 'dato']
        cesiones = [m for m in all_messages if m.get('categoria', '').strip() == 'cesion']
    except Exception as e:
        error = f"Ocurrió un error al cargar los datos: {e}"
        print(error)

    return render_template('salseo.html', 
                           datos=datos_curiosos, 
                           cesiones=cesiones, 
                           error=error, 
                           active_page='salseo')

@app.route('/participacion')
def participacion():
    error = None
    stats = []
    try:
        participation_data = download_csv_data(config.PARTICIPACION_CSV_URL)
        for row in participation_data:
            comunicados_count = len(row['comunicados'].split(';')) if row['comunicados'] else 0
            datos_count = len(row['datos'].split(';')) if row['datos'] else 0
            cesiones_count = len(row['cesiones'].split(';')) if row['cesiones'] else 0
            
            stats.append({
                'autor': row['autor'],
                'comunicados': comunicados_count,
                'datos': datos_count,
                'cesiones': cesiones_count,
                'total': comunicados_count + datos_count + cesiones_count
            })
        stats.sort(key=lambda item: item['total'], reverse=True)
    except Exception as e:
        error = f"Ocurrió un error al calcular las estadísticas: {e}"
        print(error)
        
    return render_template('participacion.html', stats=stats, error=error, active_page='participacion')

@app.route('/palmares')
def palmares():
    seasons = defaultdict(lambda: defaultdict(list))
    error = None
    try:
        palmares_data = download_csv_data(config.PALMARES_CSV_URL)
        for row in palmares_data:
            season = row.get('temporada', '').strip()
            category = row.get('categoria', '').strip()
            value = row.get('valor', '').strip()
            
            if not season or not category: continue
            if category in ['multa', 'sancion', 'farolillo']:
                 seasons[season]['otros'].append({'tipo': category, 'valor': value})
            else:
                 seasons[season][category] = value
        sorted_seasons = sorted(seasons.items(), key=lambda item: item[0], reverse=True)
    except Exception as e:
        error = f"Ocurrió un error al cargar el palmarés: {e}"
        print(error)
        sorted_seasons = []
        
    return render_template('palmares.html', seasons=sorted_seasons, error=error, active_page='palmares')

@app.route('/ligas-especiales')
def ligas_especiales():
    error = None
    leagues = []
    try:
        if not config.LIGAS_ESPECIALES_SHEET_ID:
            raise ValueError("El ID de la hoja de cálculo de Ligas Especiales no está configurado.")
        sheets_service = get_google_service('sheets', 'v4')
        leagues = get_sheets_data(sheets_service, config.LIGAS_ESPECIALES_SHEET_ID)
    except Exception as e:
        error = f"Ocurrió un error al cargar las ligas especiales: {e}"
        print(error)
        
    return render_template('ligas_especiales.html', leagues=leagues, error=error, active_page='ligas-especiales')


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    """Gestiona el login y el acceso al panel de administración."""
    if 'admin_logged_in' in session:
        file_statuses = []
        error = None
        try:
            drive_service = get_google_service('drive', 'v3')
            # Comprueba los archivos CSV
            filenames_to_check = [
                config.COMUNICADOS_FILENAME, 
                config.PARTICIPACION_FILENAME, 
                config.PALMARES_FILENAME
            ]
            file_statuses = get_file_metadata(drive_service, config.GDRIVE_FOLDER_ID, filenames_to_check)

            # AÑADIDO: Comprueba el Google Sheet de Ligas Especiales
            if config.LIGAS_ESPECIALES_SHEET_ID:
                sheet_metadata = drive_service.files().get(
                    fileId=config.LIGAS_ESPECIALES_SHEET_ID,
                    fields='name, modifiedTime'
                ).execute()
                
                dt_utc = parser.isoparse(sheet_metadata['modifiedTime'])
                dt_madrid = dt_utc.astimezone(pytz.timezone('Europe/Madrid'))
                formatted_date = dt_madrid.strftime('%d-%m-%Y a las %H:%M:%S')
                file_statuses.append({
                    'name': f"{sheet_metadata['name']} (Sheet)",
                    'status': 'Encontrado',
                    'last_updated': formatted_date
                })

        except Exception as e:
            error = f"No se pudo conectar con Google Drive para obtener el estado de los archivos: {e}"
        
        # CORRECCIÓN: URL actualizada para apuntar a la vista de logs correcta.
        log_url = f"https://console.cloud.google.com/run/jobs/details/{config.CLOUD_RUN_REGION}/{config.CLOUD_RUN_JOB_NAME}/logs?project={config.GCP_PROJECT_ID}"

        return render_template('admin_panel.html', 
                               active_page='admin', 
                               file_statuses=file_statuses, 
                               log_url=log_url,
                               error=error)

    if request.method == 'POST':
        if request.form.get('password') == config.ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash('¡Bienvenido al VAR!', 'success')
            return redirect(url_for('admin'))
        else:
            flash('Contraseña incorrecta. Inténtalo de nuevo.', 'error')
    
    return render_template('admin_login.html', active_page='admin')

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    flash('Has cerrado la sesión correctamente.', 'info')
    return redirect(url_for('comunicados'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=True, host='0.0.0.0', port=port)
