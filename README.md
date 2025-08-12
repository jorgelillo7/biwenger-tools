# Biwenger Tools

## 🔥 ¿El salseo de tu liga Biwenger merece ser eterno? 🔥

¿Te molan los comunicados graciosos entre colegas para calentar vuestras ligas? ¿Os da rabia que se pierdan entre la publicidad o al reiniciar la temporada?

¡Aquí tienes la solución! Este proyecto es un sistema de **backup + web** para que vuestros mensajes más épicos, presentaciones de equipo y piques legendarios queden guardados para siempre. Y sí, está hecho con un poco (mucho) de ayuda de la IA ;)

---

## 📜 Descripción del Proyecto

Este proyecto se divide en dos componentes principales que trabajan juntos para archivar y visualizar los comunicados y datos de una liga de Biwenger.

1.  **Scraper (`scraper-job`):** Un script de Python automatizado que se conecta a Biwenger, extrae todos los comunicados, los categoriza (`comunicado`, `dato`, `cesion`), pre-procesa los datos de participación y guarda todo en archivos CSV en Google Drive.

2.  **Aplicación Web (`web-app`):** Una aplicación web ligera con Flask que lee los datos desde los archivos CSV y un Google Sheet para presentarlos en una interfaz limpia, elegante y totalmente responsive.

---

## ✨ Características Principales

### Scraper (El Recolector Inteligente)

* **Autenticación Segura:** Inicia sesión en Biwenger de forma segura.
* **Categorización Inteligente:** Analiza los títulos de los mensajes y los clasifica automáticamente.
* **Pre-procesamiento de Datos:** Genera un archivo `participacion.csv` optimizado para que la web cargue las estadísticas al instante.
* **Almacenamiento en la Nube:** Guarda y actualiza los archivos CSV en Google Drive.
* **Automatización Total:** Diseñado para ser ejecutado como un **Cloud Run Job** y programado con **Cloud Scheduler**.
* **Gestión de Secretos:** Todas las credenciales se gestionan de forma segura a través de **Google Secret Manager** y archivos `.env` para el desarrollo local.

### Aplicación Web (El Portal de la Liga)

* **Interfaz Limpia:** Un diseño elegante y minimalista, con un tema claro para una legibilidad perfecta en cualquier dispositivo.
* **Múltiples Secciones:**
    * **Comunicados:** Visualiza los mensajes oficiales con paginación y búsqueda global.
    * **Salseo:** Una nueva sección para los "Datos Curiosos" y las "Cesiones".
    * **Participación:** Un ranking mejorado que muestra un desglose de la participación de cada jugador.
    * **Palmarés:** Un resumen histórico de las temporadas pasadas.
    * **Ligas Especiales (Beta):** Lee y muestra datos de torneos especiales directamente desde un **Google Sheet**.
* **Configuración Centralizada:** Utiliza un archivo `config.py` y un `.env` para una gestión sencilla de las URLs y parámetros.
* **Desplegado en la Nube:** Alojado en **Cloud Run** para un rendimiento escalable y eficiente.

---
## 💻 Tecnologías Utilizadas

* **Backend (Scraper):** Python, Requests, BeautifulSoup, Unidecode, Google Cloud SDK.
* **Backend (Web):** Python, Flask.
* **Frontend:** HTML, Tailwind CSS, JavaScript.
* **Cloud y Despliegue:** Google Cloud Run (Jobs y Services), Cloud Scheduler, Secret Manager, Google Drive API, Google Sheets API, Docker.