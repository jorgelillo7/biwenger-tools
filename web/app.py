# app.py
from flask import Flask, render_template, request
import csv
import requests
import io
import os
from collections import defaultdict

app = Flask(__name__)

# Leemos las URLs de los dos archivos CSV desde variables de entorno
COMUNICADOS_CSV_URL = os.getenv('COMUNICADOS_CSV_URL')
PALMARES_CSV_URL = os.getenv('PALMARES_CSV_URL')
PARTICIPACION_CSV_URL = os.getenv('PARTICIPACION_CSV_URL')
MESSAGES_PER_PAGE = 5 # Número de mensajes a mostrar por página

def download_csv_data(csv_url):
    """Función auxiliar para descargar y parsear un CSV desde una URL."""
    if not csv_url:
        raise ValueError("La URL del CSV no está configurada.")
    response = requests.get(csv_url)
    response.raise_for_status()
    csv_file = io.StringIO(response.text)
    return list(csv.DictReader(csv_file))

@app.route('/')
def comunicados():
    """Página principal que muestra los comunicados con paginación."""
    error = None
    paginated_messages = []
    page = 1
    total_pages = 1
    comunicados_only = []
    try:
        all_messages = download_csv_data(COMUNICADOS_CSV_URL)
        # Filtramos para mostrar solo la categoría 'comunicado'
        comunicados_only = [m for m in all_messages if m.get('categoria') == 'comunicado']
        
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * MESSAGES_PER_PAGE
        end = start + MESSAGES_PER_PAGE
        
        paginated_messages = comunicados_only[start:end]
        total_pages = (len(comunicados_only) + MESSAGES_PER_PAGE - 1) // MESSAGES_PER_PAGE

    except Exception as e:
        error = f"Ocurrió un error al cargar los comunicados: {e}"
        print(error)
        paginated_messages = []
        page = 1
        total_pages = 1

    return render_template('index.html', 
                           messages=paginated_messages, 
                           all_comunicados=comunicados_only, # <--- CAMBIO: Pasamos la lista completa
                           error=error, 
                           active_page='comunicados',
                           current_page=page,
                           total_pages=total_pages)

@app.route('/salseo')
def salseo():
    """Nueva página para mostrar Datos Curiosos y Cesiones."""
    error = None
    datos_curiosos = []
    cesiones = []
    try:
        all_messages = download_csv_data(COMUNICADOS_CSV_URL)
        datos_curiosos = [m for m in all_messages if m.get('categoria') == 'dato']
        cesiones = [m for m in all_messages if m.get('categoria') == 'cesion']
    except Exception as e:
        error = f"Ocurrió un error al cargar los datos: {e}"

    return render_template('salseo.html', 
                           datos=datos_curiosos, cesiones=cesiones, 
                           error=error, active_page='salseo')

@app.route('/participacion')
def participacion():
    """Página de participación que lee el nuevo CSV y cuenta las publicaciones."""
    error = None
    stats = []
    try:
        participation_data = download_csv_data(PARTICIPACION_CSV_URL)
        for row in participation_data:
            # Contamos cuántos hashes hay en cada categoría, separando por ';'
            # Si la celda está vacía, el resultado es 0.
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
        # Ordenamos por el total de publicaciones (de mayor a menor)
        stats.sort(key=lambda item: item['total'], reverse=True)
    except Exception as e:
        error = f"Ocurrió un error al calcular las estadísticas: {e}"
        print(error)
        stats = []
    return render_template('participacion.html', stats=stats, error=error, active_page='participacion')

@app.route('/palmares')
def palmares():
    """Página que muestra el palmarés de la liga."""
    seasons = defaultdict(lambda: defaultdict(list))
    error = None
    try:
        palmares_data = download_csv_data(PALMARES_CSV_URL)
        for row in palmares_data:
            # Usamos .get() y .strip() para hacer el código más robusto a errores en el CSV
            season = row.get('temporada', '').strip()
            category = row.get('categoria', '').strip()
            value = row.get('valor', '').strip()
            
            if not season or not category:
                continue # Saltamos filas vacías o malformadas

            if category in ['multa', 'sancion', 'farolillo']:
                 seasons[season]['otros'].append({'tipo': category, 'valor': value})
            else:
                 seasons[season][category] = value

        # Ordenamos las temporadas de más reciente a más antigua
        sorted_seasons = sorted(seasons.items(), key=lambda item: item[0], reverse=True)

    except Exception as e:
        error = f"Ocurrió un error al cargar el palmarés: {e}"
        print(error)
        sorted_seasons = []
        
    return render_template('palmares.html', seasons=sorted_seasons, error=error, active_page='palmares')

@app.route('/ligas-especiales')
def ligas_especiales():
    """Página de placeholder para Ligas Especiales."""
    return render_template('ligas_especiales.html', active_page='ligas-especiales')


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=True, host='0.0.0.0', port=port)
