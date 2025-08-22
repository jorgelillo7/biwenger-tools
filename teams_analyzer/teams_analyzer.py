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
import traceback

# Importaciones para Selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

import config

# Mapea nombres o partes de nombres de Biwenger a como aparecen en Analítica Fantasy.
# La clave es el nombre/apodo en Biwenger (en minúsculas y sin acentos).
# El valor es el nombre/apodo a buscar en Analítica Fantasy.
PLAYER_NAME_MAPPINGS = {
    # Mapeos completos (si el nombre entero es distinto)
    'odysseas': 'vlachodimos',
    'sancet': 'oihan sancet',
    'carlos vicente': 'c. vicente',
    'javier rueda': 'javi rueda',

    # Reemplazos de partes del nombre (para apodos o variaciones)
    'javi': 'javier',
    'brugue': 'brugui',
    'nacho': 'ignacio',
    'alhassane': 'rahim',
}

def normalize_name(name):
    """Función centralizada para limpiar y normalizar nombres."""
    return unidecode(name.lower().strip())

def find_player_match(biwenger_name, analitica_map):
    """Sistema de búsqueda de jugadores mejorado con el mapa unificado."""
    norm_b_name = normalize_name(biwenger_name)

    # 1. Búsqueda por mapeo directo (ej: 'odysseas' -> 'vlachodimos')
    if norm_b_name in PLAYER_NAME_MAPPINGS:
        mapped_name = PLAYER_NAME_MAPPINGS[norm_b_name]
        if mapped_name in analitica_map:
            return analitica_map[mapped_name]

    # 2. Búsqueda reemplazando partes del nombre (ej: 'javi hernandez' -> 'javier hernandez')
    modified_name = norm_b_name
    for biwenger_part, fa_part in PLAYER_NAME_MAPPINGS.items():
        if biwenger_part in modified_name:
            modified_name = modified_name.replace(biwenger_part, fa_part)

    if modified_name in analitica_map:
        return analitica_map[modified_name]

    # 3. Búsqueda por nombre original normalizado
    if norm_b_name in analitica_map:
        return analitica_map[norm_b_name]

    # 4. Búsqueda por subconjunto de palabras (si las palabras del nombre de Biwenger están en el de AF)
    b_name_parts = set(norm_b_name.split())
    for a_name, data in analitica_map.items():
        a_name_parts = set(a_name.split())
        if b_name_parts.issubset(a_name_parts):
            return data

    # 5. Búsqueda por si un nombre contiene al otro
    for a_name, data in analitica_map.items():
        if norm_b_name in a_name or a_name in norm_b_name:
            return data

    return {'coeficiente': 'N/A', 'puntuacion_esperada': 'N/A'}

def send_telegram_notification(bot_token, chat_id, caption, filepath):
    """Envía el archivo CSV a un chat de Telegram."""
    print("\n▶️  Enviando notificación a Telegram...")
    url = config.TELEGRAM_API_URL.format(token=bot_token)
    try:
        with open(filepath, 'rb') as f:
            files = {'document': (os.path.basename(filepath), f)}
            data = {'chat_id': chat_id, 'caption': caption}
            response = requests.post(url, data=data, files=files)
            response.raise_for_status()
        print("✅ Notificación enviada a Telegram con éxito.")
    except Exception as e:
        print(f"❌ Error al enviar la notificación a Telegram: {e}")

def authenticate_and_get_session(email, password):
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
    session = requests.Session()
    login_headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36', 'X-Lang': 'es', 'X-Version': '628'}
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
            user_id = league.get('user', {}).get('id'); break
    if not user_id: raise Exception("Error: No se pudo encontrar el ID de usuario para la liga.")
    print(f"✅ ID de usuario ({user_id}) para la liga {config.LEAGUE_ID} obtenido.")
    session.headers.update({'X-League': str(config.LEAGUE_ID), 'X-User': str(user_id)})
    session.verify = False
    return session

def fetch_all_players_data_map():
    print("▶️  Descargando la base de datos de jugadores de Biwenger...")
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'}
    response = requests.get(config.ALL_PLAYERS_DATA_URL, headers=headers, verify=False)
    response.raise_for_status()
    try: data = response.json()
    except json.JSONDecodeError:
        jsonp_text = response.text
        json_str = re.search(r'^\s*jsonp_\d+\((.*)\)\s*$', jsonp_text, re.DOTALL).group(1)
        data = json.loads(json_str)
    players_dict = data.get('data', {}).get('players', {})
    players_map = {player_info['id']: player_info for player_id, player_info in players_dict.items()}
    print(f"✅ Base de datos de Biwenger con {len(players_map)} jugadores creada.")
    return players_map

def fetch_jp_player_tips():
    print("▶️  Descargando recomendaciones de Jornada Perfecta...")
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'}
    response = requests.get(config.JORNADA_PERFECTA_MERCADO_URL, headers=headers, verify=False)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    script_tag = soup.find('script', string=re.compile(r'\s*const marketCaching=\['))
    if not script_tag: raise Exception("No se pudo encontrar el script 'marketCaching' en la página de Jornada Perfecta.")
    script_content = script_tag.string
    json_str = re.search(r'const marketCaching=(\[.*\]);', script_content, re.DOTALL).group(1)
    jp_data = json.loads(json_str)
    jp_tips_map = {normalize_name(player.get('name', '')): player.get('tip', 'N/A') for player in jp_data}
    print(f"✅ Base de datos de Jornada Perfecta con {len(jp_tips_map)} recomendaciones creada.")
    return jp_tips_map

def fetch_analitica_fantasy_coeffs():
    print("▶️  Descargando coeficientes de Analítica Fantasy (usando Selenium)...")
    chrome_options = Options()

    # Para ejecutar en segundo plano, quita el '#' de la siguiente línea
    chrome_options.add_argument("--headless")

    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:128.0) Gecko/20100101 Firefox/128.0")
    chrome_options.add_argument("--start-maximized")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    coeffs_map = {}
    try:
        driver.get(config.ANALITICA_FANTASY_URL)
        print("    ...esperando a que la página cargue...")
        wait = WebDriverWait(driver, 30)

        try:
            cookie_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'ACEPTO')]")))
            driver.execute_script("arguments[0].click();", cookie_button)
            print("✅ Pop-up de cookies aceptado.")
            time.sleep(2)
        except TimeoutException:
            print("⚠️  No se encontró el botón de cookies. Continuando...")

        print("    -> Sincronizando con la tabla de datos...")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "tr.MuiTableRow-root")))
        print("✅ Tabla de datos cargada.")

        try:
            print("    -> Intentando configurar vista de 50 jugadores por página...")
            pagination_container = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.MuiTableContainer-root + div")))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", pagination_container)
            time.sleep(1)

            page_size_dropdown_xpath = "//label[text()='Elementos por página']/following-sibling::div/div[@role='combobox']"
            page_size_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, page_size_dropdown_xpath)))

            actions = ActionChains(driver)
            actions.move_to_element(page_size_dropdown).click().perform()

            option_50_xpath = "//ul[@role='listbox']/li[@data-value='50']"
            option_50 = wait.until(EC.element_to_be_clickable((By.XPATH, option_50_xpath)))
            option_50.click()

            print("✅ Vista configurada a 50 jugadores.")
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(3)
        except Exception as e:
            print("⚠️  No se pudo cambiar la vista a 50. Se continúa con la paginación por defecto.")
            print(f"   --- Error Detallado: {str(e).splitlines()[0]} ---")

        page_number = 1
        while True:
            print(f"    ...analizando página {page_number}...")
            player_rows = driver.find_elements(By.CSS_SELECTOR, "tr.MuiTableRow-root")
            if not player_rows:
                print("    -> No se encontraron más filas de jugadores.")
                break

            for row in player_rows:
                try:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) > 6:
                        player_name = cells[1].find_element(By.CSS_SELECTOR, "p.MuiTypography-root").text.strip()
                        coefficient = cells[2].find_element(By.CSS_SELECTOR, "p.MuiTypography-root").text.strip()
                        expected_score = cells[6].text.strip().replace('\n', ' / ')

                        if player_name and coefficient:
                            normalized_name = normalize_name(player_name)
                            coeffs_map[normalized_name] = {'coeficiente': coefficient, 'puntuacion_esperada': expected_score}
                except (NoSuchElementException, IndexError):
                    continue

            try:
                next_button_xpath = "//button[contains(., 'Siguiente')]"
                next_button_element = driver.find_element(By.XPATH, next_button_xpath)
                if not next_button_element.is_enabled():
                    print("    -> El botón 'Siguiente' está desactivado. Fin del scraping.")
                    break

                driver.execute_script("arguments[0].scrollIntoView(true);", next_button_element)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", next_button_element)
                page_number += 1
                time.sleep(3)
            except NoSuchElementException:
                print("    -> No se encontró el botón 'Siguiente'. Fin del scraping.")
                break
    except Exception:
        traceback.print_exc()
    finally:
        if 'driver' in locals():
            driver.quit()
    print(f"✅ Base de datos de Analítica Fantasy con {len(coeffs_map)} coeficientes creada.")
    return coeffs_map

def fetch_league_managers(session):
    print(f"▶️  Obteniendo lista de mánagers...")
    response = session.get(config.LEAGUE_DATA_URL)
    response.raise_for_status()
    standings = response.json().get('data', {}).get('standings')
    if not standings: raise Exception("No se encontraron participantes en la liga.")
    print("✅ Lista de mánagers obtenida.")
    return standings

def fetch_manager_squad(session, manager_id):
    url = config.USER_SQUAD_URL.format(manager_id=manager_id)
    response = session.get(url)
    response.raise_for_status()
    return response.json().get('data', {}).get('players', [])

def fetch_market_players(session):
    print("▶️  Obteniendo jugadores del mercado...")
    response = session.get(config.MARKET_URL)
    response.raise_for_status()
    market_players = response.json().get('data', {}).get('sales', [])
    print(f"✅ Se han encontrado {len(market_players)} jugadores en el mercado.")
    return market_players

def map_position(pos_id):
    positions = {1: "Portero", 2: "Defensa", 3: "Centrocampista", 4: "Delantero"}
    return positions.get(pos_id, "N/A")

def main():
    start_time = time.time()
    print(f"🚀 Script iniciado a las {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    try:
        if not hasattr(config, 'BIWENGER_EMAIL') or not hasattr(config, 'BIWENGER_PASSWORD') or \
           not config.BIWENGER_EMAIL or not config.BIWENGER_PASSWORD:
            print("⚠️ ¡Atención! Debes configurar BIWENGER_EMAIL y BIWENGER_PASSWORD en tu archivo config.py")
            return

        session = authenticate_and_get_session(config.BIWENGER_EMAIL, config.BIWENGER_PASSWORD)
        players_map = fetch_all_players_data_map()
        jp_tips_map = fetch_jp_player_tips()
        analitica_coeffs_map = fetch_analitica_fantasy_coeffs()

        if not analitica_coeffs_map:
             print("\n❌ No se pudieron obtener los datos de Analítica Fantasy. Abortando el resto del proceso.")
             return

        fa_output_filename = 'analitica_fantasy_data.csv'
        print(f"\n▶️  Guardando datos de Analítica Fantasy en '{fa_output_filename}'...")
        fa_data_list = [{'Jugador': name, 'Coeficiente AF': data['coeficiente'], 'Puntuación Esperada AF': data['puntuacion_esperada']} for name, data in analitica_coeffs_map.items()]
        with open(fa_output_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Jugador', 'Coeficiente AF', 'Puntuación Esperada AF']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(fa_data_list)
        print(f"✅ Datos de Analítica Fantasy exportados con éxito.")

        managers = fetch_league_managers(session)
        market_players = fetch_market_players(session)
        all_players_export_list = []
        print("\n--- Analizando datos de la liga ---\n")
        for manager in managers:
            manager_name = manager.get('name', 'Desconocido')
            manager_id = manager.get('id')
            squad_data = fetch_manager_squad(session, manager_id)
            print(f"🔎 Analizando a: {manager_name} ({len(squad_data) if squad_data else 0} jugadores)")
            time.sleep(0.5)
            if squad_data:
                for player_data in squad_data:
                    player_info = players_map.get(player_data.get('id'))
                    if not player_info: continue
                    player_name = player_info.get('name', 'N/A')
                    ia_tip = jp_tips_map.get(normalize_name(player_name), 'Sin datos')
                    matched_data = find_player_match(player_name, analitica_coeffs_map)
                    all_players_export_list.append({
                        'Mánager': manager_name,
                        'Jugador': player_name,
                        'Posición': map_position(player_info.get('position')),
                        'Valor Actual': player_info.get('price', 0),
                        'Cláusula': player_data.get('owner', {}).get('clause', 0),
                        'Nota IA': ia_tip,
                        'Coeficiente AF': matched_data['coeficiente'],
                        'Puntuación Esperada AF': matched_data['puntuacion_esperada']
                    })

        free_agents = [sale for sale in market_players if sale.get('user') is None]
        market_team_name = f"Mercado_{datetime.now().strftime('%d%m%Y')}"
        print(f"\n🔎 Analizando a: {market_team_name} ({len(free_agents)} jugadores libres)")
        for sale in free_agents:
            player_info = players_map.get(sale.get('player', {}).get('id'))
            if not player_info: continue
            player_name = player_info.get('name', 'N/A')
            ia_tip = jp_tips_map.get(normalize_name(player_name), 'Sin datos')
            matched_data = find_player_match(player_name, analitica_coeffs_map)
            all_players_export_list.append({
                'Mánager': market_team_name,
                'Jugador': player_name,
                'Posición': map_position(player_info.get('position')),
                'Valor Actual': player_info.get('price', 0),
                'Cláusula': sale.get('price', 0),
                'Nota IA': ia_tip,
                'Coeficiente AF': matched_data['coeficiente'],
                'Puntuación Esperada AF': matched_data['puntuacion_esperada']
            })

        order = {"muyRecomendable": 0, "recomendable": 1, "apuesta": 2, "fondoDeArmario": 3, "parche": 4, "noRecomendable": 5}
        all_players_export_list.sort(key=lambda x: (x['Mánager'].startswith('Mercado_'), x['Mánager'], order.get(x['Nota IA'], 99)))

        if all_players_export_list:
            fieldnames = ['Mánager', 'Jugador', 'Posición', 'Valor Actual', 'Cláusula', 'Nota IA', 'Coeficiente AF', 'Puntuación Esperada AF']
            print(f"\n▶️  Escribiendo {len(all_players_export_list)} jugadores en '{config.OUTPUT_FILENAME}'...")
            with open(config.OUTPUT_FILENAME, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(all_players_export_list)
            print("✅ ¡Exportación completada con éxito!")

            # Enviar notificación a Telegram si está configurado
            telegram_bot_token = config.TELEGRAM_BOT_TOKEN
            telegram_chat_id = config.TELEGRAM_CHAT_ID
            if telegram_bot_token and telegram_chat_id:
                caption = f"📊 ¡Análisis de equipos completado!\n\n- Jugadores analizados: {len(all_players_export_list)}\n- Fecha: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
                send_telegram_notification(telegram_bot_token, telegram_chat_id, caption, config.OUTPUT_FILENAME)
            else:
                print("\nℹ️  No se ha configurado la notificación de Telegram (faltan TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID).")

    except Exception as e:
        print(f"❌ Ocurrió un error inesperado en la ejecución principal: {e}")
        traceback.print_exc()

    finally:
        end_time = time.time()
        duration = end_time - start_time
        minutes, seconds = divmod(duration, 60)
        print("\n" + "="*50)
        print(f"🏁 Script finalizado. Tiempo total de ejecución: {int(minutes)} minutos y {int(seconds)} segundos.")
        print("="*50)


if __name__ == '__main__':
    main()