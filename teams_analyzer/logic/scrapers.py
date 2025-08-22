import time
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# Importaciones necesarias para que la función sea autocontenida
from .. import config
from .player_matching import normalize_name

def fetch_jp_player_tips(url):
    # Asumo que esta función ya la tienes definida en otra parte, la incluyo como placeholder
    print(f"▶️  (Placeholder) Descargando consejos de Jornada Perfecta desde {url}...")
    return {}

def fetch_analitica_fantasy_coeffs():
    """
    Versión restaurada y funcional del scraper de Analítica Fantasy.
    Utiliza la lógica que proporcionaste y que funciona correctamente.
    """
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
        # La URL se obtiene directamente desde el archivo de configuración
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
