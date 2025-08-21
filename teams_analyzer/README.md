# ⚽ Analizador de Equipos Biwenger

Este proyecto contiene un script de Python (`teams_analyzer.py`) diseñado para extraer y analizar datos de tu liga de Biwenger. Utiliza `requests` para interactuar con la API de Biwenger y `Selenium` para hacer scraping de datos avanzados de webs de análisis fantasy como "Analítica Fantasy" y "Jornada Perfecta".

El objetivo es obtener un CSV con datos de la competencia para la toma de decisiones importantes. El resultado final es un archivo (`analisis_biwenger.csv`) con un resumen completo de todos los jugadores de tu liga (y del mercado), enriquecido con datos externos.

## 🏠 Puesta en Marcha Local

Sigue estos pasos para configurar y ejecutar el analizador en tu máquina.

### 1. Requisitos Previos

- **Python 3**: Asegúrate de tener Python 3 instalado en tu sistema.
- **Google Chrome**: El script utiliza Selenium con ChromeDriver, por lo que necesitas tener Google Chrome instalado.

### 2. Instalación de Dependencias

Se recomienda encarecidamente trabajar dentro de un entorno virtual (venv) para evitar conflictos de librerías.

```bash
# Crea un entorno virtual (solo la primera vez)
python3 -m venv venv

# Activa el entorno (en macOS/Linux)
source venv/bin/activate

# En Windows usa: venv\Scripts\activate
```

Una vez activado el entorno, puedes instalar todas las dependencias con el archivo `requirements.txt`

```bash
# Instala todas las dependencias del archivo
pip3 install -r requirements.txt
```

### 3. Archivo de Configuración

Antes de ejecutar el script, necesitas configurar tus datos personales.

1. Crea un archivo llamado `.env` en la misma carpeta que `teams_analyzer.py`.
2. Copia y pega el siguiente contenido en el archivo, rellenando tus datos.

**config.py**
```bash
BIWENGER_EMAIL = "YOUR_EMAIL"
BIWENGER_PASSWORD = "YOUR_PASS"
```

### 4. Ejecución del Script

Ya puedes ejecutar el analizador.

```bash
python3 teams_analyzer.py
```

El script comenzará a mostrar su progreso en la terminal. Selenium podría abrir una ventana de Chrome para realizar el scraping (dependiendo de si el modo headless está activado).

## 📂 Archivos Generados

Al finalizar la ejecución, encontrarás dos nuevos archivos CSV en tu carpeta:

- **`squads_export.csv`**: El informe principal. Contiene la lista de todos los jugadores de la liga y del mercado, con su valor, cláusula y los datos de análisis extraídos.

- **`analitica_fantasy_data.csv`**: Un archivo de respaldo con los datos en crudo obtenidos de "Analítica Fantasy". Es útil para verificar que el scraping ha funcionado correctamente.

## 🔧 Personalización y Mantenimiento

### Mapa de Nombres de Jugadores

A veces, el nombre de un jugador en Biwenger no coincide exactamente con el de las webs de análisis. Para solucionar esto, puedes añadir excepciones en el diccionario `PLAYER_NAME_MAPPINGS` al principio del script.

**Ejemplo:**
```python
PLAYER_NAME_MAPPINGS = {
    'odysseas': 'vlachodimos',
    'carlos vicente': 'c. vicente',
}
```

## ⚠️ Notas Importantes

- **Modo Headless**: Para que el script se ejecute más rápido y sin abrir una ventana de navegador, puedes activar el modo headless en la función `fetch_analitica_fantasy_coeffs` del script, quitando el `#` de la línea `# chrome_options.add_argument("--headless")`.

---

## 📊 Flujo de Datos

1. **Autenticación** → Login en Biwenger con tus credenciales
2. **Extracción de datos** → Obtiene información de jugadores, mercado y liga
3. **Scraping externo** → Enriquece los datos con información de webs de análisis
4. **Procesamiento** → Combina y procesa toda la información
5. **Exportación** → Genera el CSV final con el análisis completo