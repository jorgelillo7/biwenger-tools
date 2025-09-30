# ⚽ Analizador de Equipos Biwenger

Este proyecto es un conjunto de herramientas en Python que extraen, analizan y notifican datos de tu liga de Biwenger. Utiliza la API de Biwenger y el scraping de webs como "Analítica Fantasy" y "Jornada Perfecta" para enriquecer los datos.

El objetivo es doble:
1. Generar un archivo **CSV** con un análisis completo de tu liga.
2. Enviar automáticamente ese análisis a tu **chat de Telegram**.

## 🚀 Funcionalidades Clave

* **Análisis Completo**:
- **`squads_export.csv`**: El informe principal con la lista de todos los jugadores, su valor, cláusula y los datos de análisis extraídos.

- **`analitica_fantasy_data_backup.csv`**: Un archivo de respaldo con los datos en crudo obtenidos de "Analítica Fantasy". Es útil para verificar que el scraping ha funcionado correctamente.

* **Notificación por Telegram**: Envía automáticamente el archivo generado a un chat de Telegram. (si se configuran las variables de entorno)

## ⚙️ Configuración y Uso

Para ejecutar y configurar este proyecto, consulta las instrucciones detalladas en el documento principal de operaciones.

* **Instalación y dependencias**: Revisa la sección **`1.3 Teams Analyzer`** en `operations.md`.
* **Configuración de credenciales**: Las variables para Biwenger y Telegram se establecen en el archivo `.env`.
* **Ejecución**: El comando para la ejecución local se encuentra en `operations.md`.

---

### **Cómo obtener los datos de Telegram**

Si quieres recibir notificaciones, necesitas un **bot token** y el **chat ID**.

1. **Crea un Bot**: Habla con `@BotFather` en Telegram. Usa el comando `/newbot`, dale un nombre y te proporcionará el `TELEGRAM_BOT_TOKEN`.
2. **Obtén tu Chat ID**: Usa el bot token en la siguiente URL (quitando los corchetes) para obtener tu chat ID.

    `https://api.telegram.org/bot[TELEGRAM_BOT_TOKEN]/getUpdates`

    El resultado te mostrará el ID de tu chat en el JSON de respuesta.

---

### **🔧 Personalización y Mantenimiento**

#### **Mapa de Nombres de Jugadores**

A veces, el nombre de un jugador en Biwenger no coincide exactamente con el de las webs de análisis. Para solucionar esto, puedes añadir excepciones en el diccionario `PLAYER_NAME_MAPPINGS` al principio del script.

**Ejemplo:**
```python
PLAYER_NAME_MAPPINGS = {
    'odysseas': 'vlachodimos',
    'carlos vicente': 'c. vicente',
}

## ⚠️ Notas Importantes

- **Modo Headless**: Para que el script se ejecute más rápido y sin abrir una ventana de navegador, puedes activar el modo headless en la función `fetch_analitica_fantasy_coeffs` del script, quitando el `#` de la línea `# chrome_options.add_argument("--headless")`.