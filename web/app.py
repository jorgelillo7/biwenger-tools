# app.py
from flask import Flask, render_template, request
import csv
import requests
import io
import os
import json
from collections import defaultdict

# Importaciones para Google Cloud
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

app = Flask(__name__)

# --- CONFIGURACIÓN ---
COMUNICADOS_CSV_URL = os.getenv('COMUNICADOS_CSV_URL')
PARTICIPACION_CSV_URL = os.getenv('PARTICIPACION_CSV_URL')
PALMARES_CSV_URL = os.getenv('PALMARES_CSV_URL')
LIGAS_ESPECIALES_SHEET_ID = os.getenv('LIGAS_ESPECIALES_SHEET_ID')

MESSAGES_PER_PAGE = 5
# Nuevos permisos: Drive (existente) + Sheets (solo lectura)
SCOPES = ['https://www.googleapis.com/auth/drive.readonly', 'https://www.googleapis.com/auth/spreadsheets.readonly']
# -------------------

def get_google_service(service_name, version):
    """Función genérica para autenticar y crear un servicio de Google (Drive o Sheets)."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secrets.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
            
    return build(service_name, version, credentials=creds)

def download_csv_data(csv_url):
    """Descarga y parsea un CSV desde una URL."""
    if not csv_url: raise ValueError("La URL del CSV no está configurada.")
    response = requests.get(csv_url)
    response.raise_for_status()
    return list(csv.DictReader(io.StringIO(response.text)))

def get_sheets_data(service, spreadsheet_id):
    """Lee y procesa los datos de todas las hojas de un Google Sheet."""
    sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheets = sheet_metadata.get('sheets', '')
    
    all_leagues = []

    for sheet in sheets:
        sheet_title = sheet.get("properties", {}).get("title", "Sin Título")
        print(f"▶️  Leyendo hoja: {sheet_title}")
        
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

# --- RUTAS DE LA APLICACIÓN ---

@app.route('/')
def comunicados():
    error = None
    paginated_messages = []
    page = 1
    total_pages = 1
    comunicados_only = []
    try:
        all_messages = download_csv_data(COMUNICADOS_CSV_URL)
        comunicados_only = [m for m in all_messages if m.get('categoria') == 'comunicado']
        
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * MESSAGES_PER_PAGE
        end = start + MESSAGES_PER_PAGE
        
        paginated_messages = comunicados_only[start:end]
        total_pages = (len(comunicados_only) + MESSAGES_PER_PAGE - 1) // MESSAGES_PER_PAGE

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
        all_messages = download_csv_data(COMUNICADOS_CSV_URL)
        datos_curiosos = [m for m in all_messages if m.get('categoria') == 'dato']
        cesiones = [m for m in all_messages if m.get('categoria') == 'cesion']
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
        participation_data = download_csv_data(PARTICIPACION_CSV_URL)
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
        palmares_data = download_csv_data(PALMARES_CSV_URL)
        for row in palmares_data:
            season = row.get('temporada', '').strip()
            category = row.get('categoria', '').strip()
            value = row.get('valor', '').strip()
            
            if not season or not category:
                continue

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
    """Página que lee y muestra los datos de Google Sheets."""
    error = None
    leagues = []
    try:
        if not LIGAS_ESPECIALES_SHEET_ID:
            raise ValueError("El ID de la hoja de cálculo de Ligas Especiales no está configurado.")
        sheets_service = get_google_service('sheets', 'v4')
        leagues = get_sheets_data(sheets_service, LIGAS_ESPECIALES_SHEET_ID)
    except Exception as e:
        error = f"Ocurrió un error al cargar las ligas especiales: {e}"
        print(error)
        
    return render_template('ligas_especiales.html', leagues=leagues, error=error, active_page='ligas-especiales')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=True, host='0.0.0.0', port=port)
