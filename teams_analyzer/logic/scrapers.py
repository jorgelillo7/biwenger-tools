import csv
import json
import os
import re
import requests
import time
import shutil
import tempfile
import traceback
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
#from webdriver_manager.chrome import ChromeDriverManager

from .. import config
from .player_matching import normalize_name

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

def create_chrome_driver():
    """
    Inicializa Chromium headless con opciones robustas para Docker ARM64.
    """
    driver = None
    max_retries = 3
    retry_delay = 5
    temp_dir = None

    for attempt in range(max_retries):
        try:
            temp_dir = tempfile.mkdtemp()
            chrome_options = Options()
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument(f"--user-data-dir={temp_dir}")
            chrome_options.add_argument("--remote-allow-origins=*")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.binary_location = "/usr/bin/chromium"

            driver = webdriver.Chrome(
                service=Service("/usr/bin/chromedriver"),
                options=chrome_options
            )
            driver.get("about:blank")
            return driver

        except Exception as e:
            print(f"❌ Intento {attempt+1} fallido al iniciar Chromium: {e}")
            if driver:
                driver.quit()
            time.sleep(retry_delay)
        finally:
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

    raise Exception("No se pudo iniciar Chromium tras varios intentos")


def fetch_analitica_fantasy_coeffs():
    """
    Descarga los coeficientes de Analítica Fantasy, ignorando problemas de dropdown.
    """
    print("▶️ Descargando coeficientes de Analítica Fantasy (usando Selenium)...")
    driver = None
    coeffs_map = {}
    temp_dir = None

    try:
        driver = create_chrome_driver()
        driver.get(config.ANALITICA_FANTASY_URL)
        wait = WebDriverWait(driver, 60)

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
        if driver:
            driver.quit()
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    # Guardar CSV de respaldo
    if coeffs_map:
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', config.BACKUP_COEFFS_CSV)
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['nombre_normalizado', 'coeficiente', 'puntuacion_esperada'])
                for name, data in coeffs_map.items():
                    writer.writerow([name, data['coeficiente'], data['puntuacion_esperada']])
            print(f"✅ Datos guardados en '{output_path}'")
        except Exception as e:
            print(f"❌ No se pudo guardar el archivo: {e}")

    print(f"✅ Base de datos de Analítica Fantasy con {len(coeffs_map)} coeficientes creada.")
    return coeffs_map
