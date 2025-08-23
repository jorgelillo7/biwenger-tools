# ⚽ Analizador de Equipos Biwenger

Este proyecto contiene un conjunto de herramientas de Python diseñadas para extraer, analizar y notificar datos de tu liga de Biwenger. Utiliza `requests` para interactuar con la API de Biwenger y `Selenium` para hacer scraping de datos avanzados de webs de análisis fantasy como "Analítica Fantasy" y "Jornada Perfecta".

El objetivo es obtener un CSV con datos de la competencia para la toma de decisiones, y ahora también, **recibir este análisis directamente en tu chat de Telegram**.

## 🚀 Funcionalidades Principales

1.  **Análisis Completo**: Genera un archivo (`analisis_biwenger.csv`) con un resumen de todos los jugadores de tu liga y del mercado, enriquecido con datos externos.
2.  **Notificación por Telegram**: Envía automáticamente el archivo CSV generado a un chat de Telegram para que puedas consultarlo desde cualquier lugar.

## 🏠 Puesta en Marcha Local

Sigue estos pasos para configurar y ejecutar el analizador en tu máquina.

### 1. Requisitos Previos

-   **Python 3**: Asegúrate de tener Python 3 instalado.
-   **Google Chrome**: El script utiliza Selenium con ChromeDriver, por lo que necesitas tener Google Chrome instalado.

### 2. Instalación de Dependencias

Se recomienda encarecidamente trabajar dentro de un entorno virtual (`venv`).

```bash
# 1. Crea y activa un entorno virtual
python3 -m venv venv
source venv/bin/activate
# En Windows: venv\Scripts\activate

# 2. Instala todas las dependencias
pip3 install -r requirements.txt

### 3. Archivo de Configuración

Antes de ejecutar el script, necesitas configurar tus datos personales.

1. Crea un archivo llamado `.env` en la misma carpeta que `teams_analyzer.py`.
2. Copia y pega el siguiente contenido en el archivo, rellenando tus datos.

**config.py**
```bash
BIWENGER_EMAIL = "YOUR_EMAIL"
BIWENGER_PASSWORD = "YOUR_PASS"
# --- Configuración de Telegram (Opcional) ---
# Si dejas estos campos vacíos, el script no intentará enviar la notificación.

# 1. El token de tu Bot (obtenido de BotFather)
TELEGRAM_BOT_TOKEN = "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"

# 2. El ID de tu chat (puedes obtenerlo de bots como @userinfobot)
TELEGRAM_CHAT_ID = "123456789"
```

¿Cómo obtener los datos de Telegram?
1. Crea un Bot: Habla con @BotFather en Telegram. Usa el comando /newbot, dale un nombre y te proporcionará el TELEGRAM_BOT_TOKEN.

2. Obtén tu Chat ID: usa tu bot_token con la siguiente URL:
https://api.telegram.org/bot[TELEGRAM_BOT_TOKEN]/getUpdates (quitar [])

te saldrá algo similar a si lo haces en un grupo, o si es a un chat privado también saldrá el id
```
"chat": {
    "id": -1111111111,
    "title": "Teams Analyzer",
    "type": "group",
    "all_members_are_administrators": true,
    "accepted_gift_types": {
    "unlimited_gifts": false,
    "limited_gifts": false,
    "unique_gifts": false,
    "premium_subscription": false
}
```

### 4. Ejecución del Script (desde raiz)

Una vez configurado, ejecuta el analizador desde la raíz de tu proyecto:

```bash
python3 -m teams_analyzer.teams_analyzer
```

El script mostrará su progreso en la terminal. Si la configuración de Telegram es correcta, al finalizar recibirás el archivo CSV en tu chat.

## 📂 Archivos Generados

Al finalizar la ejecución, encontrarás dos nuevos archivos CSV en tu carpeta:

- **`squads_export.csv`**: El informe principal con la lista de todos los jugadores, su valor, cláusula y los datos de análisis extraídos.

- **`analitica_fantasy_data_backup.csv`**: Un archivo de respaldo con los datos en crudo obtenidos de "Analítica Fantasy". Es útil para verificar que el scraping ha funcionado correctamente.

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