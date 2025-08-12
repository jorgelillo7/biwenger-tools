# Biwenger Tools

## 🔥 ¿El salseo de tu liga Biwenger merece ser eterno? 🔥

¿Te molan los comunicados graciosos entre colegas para calentar vuestras ligas? ¿Os da rabia que se pierdan entre la publicidad o al reiniciar la temporada?

¡Aquí tienes la solución! Este proyecto es un sistema de **backup + web** para que vuestros mensajes más épicos, presentaciones de equipo y piques legendarios queden guardados para siempre. Y sí, está hecho con un poco(mucho) de ayuda de la IA ;)

---

## 📜 Descripción del Proyecto

Este proyecto se divide en dos componentes principales que trabajan juntos para archivar y visualizar los comunicados del tablón de anuncios de una liga de Biwenger.

1.  **Scraper de Datos (`get_messages.py`):** Un script de Python que se ejecuta de forma automatizada. Se conecta a Biwenger, extrae todos los comunicados, los **categoriza** (`comunicado`, `dato`, `cesion`) y pre-procesa los datos de participación. Finalmente, guarda toda la información en dos archivos CSV en Google Drive.

2.  **Aplicación Web (`app.py`):** Una aplicación web ligera construida con Flask. Lee los datos directamente desde los archivos CSV públicos en Google Drive y los presenta en una interfaz limpia, elegante y totalmente responsive con múltiples secciones.

---

## ✨ Características Principales

### Scraper (El Recolector Inteligente)

* **Autenticación Segura:** Inicia sesión en Biwenger de forma segura.
* **Categorización Inteligente:** Analiza los títulos de los mensajes y los clasifica automáticamente como `comunicado`, `dato` o `cesion`.
* **Pre-procesamiento de Datos:** Genera un archivo `participacion.csv` optimizado para que la web cargue las estadísticas de forma instantánea.
* **Almacenamiento en la Nube:** Guarda y actualiza los archivos CSV en Google Drive.
* **Automatización Total:** Diseñado para ser ejecutado como un **Cloud Run Job** y programado con **Cloud Scheduler** para una ejecución desatendida.
* **Gestión de Secretos:** Todas las credenciales se gestionan de forma segura a través de **Google Secret Manager**.

### Aplicación Web (El Portal de la Liga)

* **Interfaz Limpia:** Un diseño elegante y minimalista, con un tema claro y toques de color para una legibilidad perfecta en cualquier dispositivo.
* **Múltiples Secciones:**
    * **Comunicados:** Visualiza los mensajes oficiales con **paginación** para una navegación cómoda.
    * **Salseo:** Una nueva sección para los "Datos Curiosos" (Mr. Lucen) y las "Cesiones", con filtros para alternar entre ambas.
    * **Participación:** Un ranking mejorado que muestra un desglose del número de comunicados, datos y cesiones de cada jugador.
    * **Palmarés:** Un resumen histórico de los ganadores y datos curiosos de temporadas pasadas.
    * **Ligas Especiales:** Una sección preparada para futuras ampliaciones.
* **Búsqueda Global:** El buscador ahora funciona en la totalidad de los mensajes, no solo en la página actual.
* **Desplegado en la Nube:** Alojado en **Cloud Run** para un rendimiento escalable y eficiente.

---

## 💻 Tecnologías Utilizadas

* **Backend (Scraper):** Python, Requests, BeautifulSoup, Unidecode, Google Cloud SDK.
* **Backend (Web):** Python, Flask.
* **Frontend:** HTML, Tailwind CSS, JavaScript.
* **Cloud y Despliegue:** Google Cloud Run (Jobs y Services), Cloud Scheduler, Secret Manager, Google Drive API, Docker.