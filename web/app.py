# app.py
from flask import Flask, render_template, jsonify
import csv
import requests
import io
import os
from collections import defaultdict

app = Flask(__name__)

# Leemos las URLs de los dos archivos CSV desde variables de entorno
COMUNICADOS_CSV_URL = os.getenv('COMUNICADOS_CSV_URL')
PALMARES_CSV_URL = os.getenv('PALMARES_CSV_URL')

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
    """Página principal que muestra los comunicados."""
    messages = []
    error = None
    try:
        messages = download_csv_data(COMUNICADOS_CSV_URL)
    except Exception as e:
        error = f"Ocurrió un error al cargar los comunicados: {e}"
        print(error)
    return render_template('index.html', messages=messages, error=error, active_page='comunicados')

@app.route('/participacion')
def participacion():
    """Página que muestra estadísticas de participación."""
    stats = defaultdict(int)
    error = None
    try:
        messages = download_csv_data(COMUNICADOS_CSV_URL)
        for msg in messages:
            autor = msg.get('autor', 'Autor Desconocido').strip()
            if autor != 'Autor Desconocido':
                stats[autor] += 1
        # Ordenamos por número de comunicados (de mayor a menor)
        sorted_stats = sorted(stats.items(), key=lambda item: item[1], reverse=True)
    except Exception as e:
        error = f"Ocurrió un error al calcular las estadísticas: {e}"
        print(error)
        sorted_stats = []
    return render_template('participacion.html', stats=sorted_stats, error=error, active_page='participacion')

@app.route('/palmares')
def palmares():
    """Página que muestra el palmarés de la liga."""
    seasons = defaultdict(lambda: defaultdict(list))
    error = None
    try:
        palmares_data = download_csv_data(PALMARES_CSV_URL)
        for row in palmares_data:
            # CAMBIO: Usamos .strip() para limpiar los datos del CSV
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

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=True, host='0.0.0.0', port=port)
