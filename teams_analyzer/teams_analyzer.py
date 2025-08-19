# teams_analyzer.py
import requests
import os
import time
import json
import re
import csv
from bs4 import BeautifulSoup
from datetime import datetime
from unidecode import unidecode
import traceback  # <-- Importante para logs detallados

# Importaciones para Selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Importamos toda la configuración
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
    """Obtiene todos los jugadores de Biwenger y crea un mapa de datos."""
    print("▶️  Descargando la base de datos de jugadores de Biwenger...")
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

    print(f"✅ Base de datos de Biwenger con {len(players_map)} jugadores creada.")
    return players_map

def fetch_jp_player_tips():
    """Obtiene las recomendaciones de Jornada Perfecta y crea un mapa."""
    print("▶️  Descargando recomendaciones de Jornada Perfecta...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
    }
    response = requests.get(config.JORNADA_PERFECTA_MERCADO_URL, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    script_tag = soup.find('script', string=re.compile(r'\s*const marketCaching=\['))

    if not script_tag:
        raise Exception("No se pudo encontrar el script 'marketCaching' en la página de Jornada Perfecta.")

    script_content = script_tag.string
    json_str = re.search(r'const marketCaching=(\[.*\]);', script_content, re.DOTALL).group(1)
    jp_data = json.loads(json_str)

    jp_tips_map = {
        unidecode(player.get('name', '').strip().lower()): player.get('tip', 'N/A')
        for player in jp_data
    }
    print(f"✅ Base de datos de Jornada Perfecta con {len(jp_tips_map)} recomendaciones creada.")
    return jp_tips_map

# Reemplaza la función antigua por esta en teams_analyzer.py

def fetch_analitica_fantasy_coeffs():
    """Usa Selenium para obtener los coeficientes de Analítica Fantasy, manejando cookies y paginación."""
    print("▶️  Descargando coeficientes de Analítica Fantasy (usando Selenium)...")

    chrome_options = Options()
    # Descomenta la siguiente línea para que el navegador NO se muestre (modo headless)
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    chrome_options.add_argument("--window-size=1920,1200")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    raw_scraped_data = []
    coeffs_map = {}

    try:
        driver.get(config.ANALITICA_FANTASY_URL)
        print("    ...esperando a que la página cargue...")

        wait = WebDriverWait(driver, 25)

        # 1. Aceptar cookies
        try:
            print("    -> Buscando el botón de cookies...")
            cookie_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'ACEPTO')]")))
            driver.execute_script("arguments[0].click();", cookie_button)
            print("✅ Pop-up de cookies aceptado.")
            time.sleep(2)
        except TimeoutException:
            print("⚠️  No se encontró el botón de cookies. Continuando...")

        page_number = 1
        # 2. Bucle de paginación
        while True:
            print(f"    ...analizando página {page_number}...")

            try:
                # SELECTOR CORREGIDO: Esperamos a que el cuerpo de la tabla (tbody) sea visible
                print("    -> Buscando el cuerpo de la tabla (tbody)...")
                wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "table.MuiTable-root > tbody.MuiTableBody-root")))
                print("    -> Cuerpo de la tabla visible.")
                time.sleep(1) 

                # SELECTOR CORREGIDO: Buscamos las filas (tr) dentro del tbody
                player_rows = driver.find_elements(By.CSS_SELECTOR, "tbody.MuiTableBody-root > tr.MuiTableRow-root")
                print(f"    -> Se encontraron {len(player_rows)} filas en esta página.")
                
                if not player_rows:
                    print("    -> No se encontraron filas, finalizando bucle.")
                    break

                for row in player_rows:
                    try:
                        # SELECTORES CORREGIDOS: Buscamos las celdas (td) y extraemos el texto
                        # Las celdas se identifican por su posición (índice)
                        cells = row.find_elements(By.TAG_NAME, "td")
                        
                        # Celda 1 para el nombre del jugador, Celda 2 para el coeficiente
                        if len(cells) > 2:
                            player_name = cells[1].find_element(By.TAG_NAME, "p").text.strip()
                            coefficient = cells[2].find_element(By.TAG_NAME, "p").text.strip()

                            if player_name and coefficient:
                                normalized_name = unidecode(player_name.lower())
                                if normalized_name not in coeffs_map:
                                    coeffs_map[normalized_name] = coefficient
                                    raw_scraped_data.append({'jugador': player_name, 'coeficiente': coefficient})
                    except (NoSuchElementException, IndexError):
                        # Si una fila no tiene la estructura esperada, la saltamos
                        continue

            except TimeoutException:
                 print("⚠️  Timeout: No se encontró la tabla en la página. Finalizando scraping.")
                 break

            # 3. Lógica de paginación
            try:
                # SELECTOR CORREGIDO: Buscamos el botón por el texto 'Siguiente'
                print("    -> Buscando botón 'Siguiente'...")
                next_button_xpath = "//button[contains(., 'Siguiente')]"
                wait.until(EC.presence_of_element_located((By.XPATH, next_button_xpath)))
                next_button = driver.find_element(By.XPATH, next_button_xpath)

                if not next_button.is_enabled():
                    print("✅ Fin de la paginación (botón 'Siguiente' deshabilitado).")
                    break

                print("    ...pasando a la siguiente página...")
                driver.execute_script("arguments[0].click();", next_button)
                page_number += 1
                time.sleep(3) # Espera crucial para que la tabla de la siguiente página cargue

            except (NoSuchElementException, TimeoutException):
                print("✅ Fin de la paginación (no se encontró más botón 'Siguiente').")
                break

    except Exception:
        print(f"❌ Ocurrió un error inesperado durante el scraping.")
        print("\n--- INICIO DEL TRACEBACK (LOG DETALLADO) ---")
        traceback.print_exc()
        print("--- FIN DEL TRACEBACK ---\n")
        screenshot_path = "debug_screenshot_analitica.png"
        driver.save_screenshot(screenshot_path)
        print(f"📸 Se ha guardado una captura de pantalla en '{screenshot_path}' para depuración.")
    finally:
        if 'driver' in locals():
            driver.quit()

    if raw_scraped_data:
        print(f"💾 Guardando {len(raw_scraped_data)} jugadores extraídos en 'analitica_fantasy_data.csv'...")
        with open('analitica_fantasy_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['jugador', 'coeficiente'])
            writer.writeheader()
            writer.writerows(raw_scraped_data)

    print(f"✅ Base de datos de Analítica Fantasy con {len(coeffs_map)} coeficientes creada.")
    return coeffs_map

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
    """Obtiene la plantilla de un mánager."""
    url = config.USER_SQUAD_URL.format(manager_id=manager_id)
    response = session.get(url)
    response.raise_for_status()
    return response.json().get('data', {}).get('players', [])

def fetch_market_players(session):
    """Obtiene los jugadores que están actualmente en el mercado."""
    print("▶️  Obteniendo jugadores del mercado...")
    response = session.get(config.MARKET_URL)
    response.raise_for_status()
    market_players = response.json().get('data', {}).get('sales', [])
    print(f"✅ Se han encontrado {len(market_players)} jugadores en el mercado.")
    return market_players

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
        jp_tips_map = fetch_jp_player_tips()
        analitica_coeffs_map = fetch_analitica_fantasy_coeffs()
        managers = fetch_league_managers(session)
        market_players = fetch_market_players(session)

        all_players_export_list = []
        print("\n--- Analizando datos de la liga ---\n")

        # Analizar equipos de los mánagers
        for manager in managers:
            manager_name = manager.get('name', 'Desconocido')
            manager_id = manager.get('id')

            squad_data = fetch_manager_squad(session, manager_id)
            squad_size = len(squad_data) if squad_data else 0
            print(f"🔎 Analizando a: {manager_name} ({squad_size} jugadores)")
            time.sleep(0.5)

            if squad_data:
                for player_data in squad_data:
                    player_id = player_data.get('id')
                    player_info = players_map.get(player_id)
                    if not player_info: continue

                    player_name = player_info.get('name', 'N/A')
                    player_name_lower = unidecode(player_name.strip().lower())
                    ia_tip = jp_tips_map.get(player_name_lower, 'Sin datos')
                    coeficiente = analitica_coeffs_map.get(player_name_lower, 'N/A')

                    all_players_export_list.append({
                        'Mánager': manager_name,
                        'Jugador': player_name,
                        'Posición': map_position(player_info.get('position')),
                        'Multiposición': "Sí" if player_info.get('altPositions') else "No",
                        'Valor Actual': player_info.get('price', 0),
                        'Cláusula': player_data.get('owner', {}).get('clause', 0),
                        'Nota IA': ia_tip,
                        'Coeficiente AF': coeficiente
                    })

        # Analizar jugadores del mercado
        free_agents = [sale for sale in market_players if sale.get('user') is None]
        market_team_name = f"Mercado_{datetime.now().strftime('%d%m%Y')}"
        print(f"\n🔎 Analizando a: {market_team_name} ({len(free_agents)} jugadores libres)")
        for sale in free_agents:
            player_id = sale.get('player', {}).get('id')
            player_info = players_map.get(player_id)
            if not player_info: continue

            player_name = player_info.get('name', 'N/A')
            player_name_lower = unidecode(player_name.strip().lower())
            ia_tip = jp_tips_map.get(player_name_lower, 'Sin datos')
            coeficiente = analitica_coeffs_map.get(player_name_lower, 'N/A')

            all_players_export_list.append({
                'Mánager': market_team_name,
                'Jugador': player_name,
                'Posición': map_position(player_info.get('position')),
                'Multiposición': "Sí" if player_info.get('altPositions') else "No",
                'Valor Actual': player_info.get('price', 0),
                'Cláusula': sale.get('price', 0),
                'Nota IA': ia_tip,
                'Coeficiente AF': coeficiente
            })

        # Lógica de ordenación personalizada
        order = { "muyRecomendable": 0, "recomendable": 1, "apuesta": 2, "fondoDeArmario": 3, "parche": 4, "noRecomendable": 5 }
        all_players_export_list.sort(key=lambda x: (x['Mánager'].startswith('Mercado_'), x['Mánager'], order.get(x['Nota IA'], 99)))

        # Escribir los datos en un archivo CSV
        if all_players_export_list:
            print(f"\n▶️  Escribiendo {len(all_players_export_list)} jugadores en '{config.OUTPUT_FILENAME}'...")
            with open(config.OUTPUT_FILENAME, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Mánager', 'Jugador', 'Posición', 'Multiposición', 'Valor Actual', 'Cláusula', 'Nota IA', 'Coeficiente AF']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(all_players_export_list)
            print("✅ ¡Exportación completada con éxito!")
        else:
            print("ℹ️ No se encontraron jugadores para exportar.")

    except Exception as e:
        print(f"❌ Ocurrió un error inesperado en la ejecución principal: {e}")

if __name__ == '__main__':
    main()