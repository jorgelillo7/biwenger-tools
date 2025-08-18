# export_squads.py
import requests
import os
import time
import json
import re
import csv
from collections import defaultdict

# Importamos toda la configuración desde nuestro archivo config.py
import config

def authenticate_and_get_session(email, password):
    """Inicia sesión en Biwenger y devuelve una sesión autenticada."""
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
    session = requests.Session()
    login_headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'X-Lang': 'es', 'X-Version': '628'
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
    for league in account_data.get('data', {}).get('leagues', []):
        if str(league.get('id')) == config.LEAGUE_ID:
            user_id = league.get('user', {}).get('id')
            break
    if not user_id: raise Exception("Error: No se pudo encontrar el ID de usuario para la liga.")
    print(f"✅ ID de usuario ({user_id}) para la liga {config.LEAGUE_ID} obtenido.")
    session.headers.update({'X-League': str(config.LEAGUE_ID), 'X-User': str(user_id)})
    session.verify = False
    return session

def fetch_all_players_data_map():
    """Obtiene todos los jugadores de la competición y crea un mapa de datos."""
    print("▶️  Descargando la base de datos de jugadores...")
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'}
    response = requests.get(config.ALL_PLAYERS_DATA_URL, headers=headers, verify=False)
    response.raise_for_status()
    try:
        data = response.json()
    except json.JSONDecodeError:
        jsonp_text = response.text
        json_str = re.search(r'^\s*jsonp_\d+\((.*)\)\s*$', jsonp_text, re.DOTALL).group(1)
        data = json.loads(json_str)
    
    players_dict = data.get('data', {}).get('players', {})
    players_map = {player_info['id']: player_info for player_id, player_info in players_dict.items()}
    
    print(f"✅ Base de datos con {len(players_map)} jugadores creada.")
    return players_map

def fetch_league_managers(session):
    """Obtiene la lista de mánagers de la liga."""
    print(f"▶️  Obteniendo lista de mánagers...")
    response = session.get(config.LEAGUE_DATA_URL)
    response.raise_for_status()
    standings = response.json().get('data', {}).get('standings')
    if not standings: raise Exception("No se encontraron participantes en la liga.")
    print("✅ Lista de mánagers obtenida.")
    return standings

def fetch_manager_squad(session, manager_id):
    """Obtiene la lista de jugadores (con ID y owner) de la plantilla de un mánager."""
    url = config.USER_SQUAD_URL.format(manager_id=manager_id)
    response = session.get(url)
    response.raise_for_status()
    return response.json().get('data', {}).get('players', [])

def map_position(pos_id):
    """Traduce el ID de la posición a un texto legible."""
    positions = {1: "Portero", 2: "Defensa", 3: "Centrocampista", 4: "Delantero"}
    return positions.get(pos_id, "N/A")

def main():
    """Función principal que orquesta el proceso."""
    if not config.BIWENGER_EMAIL or not config.BIWENGER_PASSWORD:
        print("⚠️ ¡Atención! Debes configurar BIWENGER_EMAIL y BIWENGER_PASSWORD en tu archivo .env")
        return
        
    try:
        session = authenticate_and_get_session(config.BIWENGER_EMAIL, config.BIWENGER_PASSWORD)
        players_map = fetch_all_players_data_map()
        managers = fetch_league_managers(session)

        all_players_export_list = []
        print("\n--- Analizando plantillas (squads) de la liga ---\n")
        
        for manager in managers:
            manager_name = manager.get('name', 'Desconocido')
            manager_id = manager.get('id')
            
            print(f"🔎 Analizando a: {manager_name}")
            time.sleep(0.5) 
            
            squad_data = fetch_manager_squad(session, manager_id)
            
            if squad_data:
                for player_data in squad_data:
                    player_id = player_data.get('id')
                    player_info = players_map.get(player_id)

                    # Excluimos jugadores que no estén en la base de datos principal
                    if not player_info:
                        print(f"    - Omitiendo jugador con ID {player_id} (no encontrado en la base de datos).")
                        continue

                    clause = player_data.get('owner', {}).get('clause', 0)
                    multiposicion = "Sí" if player_info.get('altPositions') else "No"
                    
                    all_players_export_list.append({
                        'Mánager': manager_name,
                        'Jugador': player_info.get('name', 'N/A'),
                        'Posición': map_position(player_info.get('position')),
                        'Multiposición': multiposicion,
                        'Valor Actual': player_info.get('price', 0),
                        'Cláusula': clause,
                        'Nota IA': '' # Columna placeholder
                    })

        # Escribir los datos en un archivo CSV
        if all_players_export_list:
            print(f"\n▶️  Escribiendo {len(all_players_export_list)} jugadores en '{config.OUTPUT_FILENAME}'...")
            with open(config.OUTPUT_FILENAME, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Mánager', 'Jugador', 'Posición', 'Multiposición', 'Valor Actual', 'Cláusula', 'Nota IA']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(all_players_export_list)
            print("✅ ¡Exportación completada con éxito!")
        else:
            print("ℹ️ No se encontraron jugadores para exportar.")

    except Exception as e:
        print(f"❌ Ocurrió un error inesperado: {e}")

if __name__ == '__main__':
    main()
