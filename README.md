# Biwenger Tools

## 🔥 ¿El salseo de tu liga Biwenger merece ser eterno? 🔥

¿Te molan los comunicados graciosos entre colegas para calentar vuestras ligas? ¿Os da rabia que se pierdan entre la publicidad o al reiniciar la temporada?

¡Aquí tienes la solución! Este proyecto es un sistema de **backup + web** para que vuestros mensajes más épicos, presentaciones de equipo y piques legendarios queden guardados para siempre. Y sí, está hecho con un poco de ayuda de la IA ;)

---

## 📜 Descripción del Proyecto

Este proyecto se divide en dos componentes principales que trabajan juntos para archivar y visualizar los comunicados del tablón de anuncios de una liga de Biwenger.

1.  **Scraper de Datos (`get_messages.py`):** Un script de Python que se ejecuta de forma automatizada. Se conecta a Biwenger, extrae todos los comunicados de los participantes, los procesa y los guarda en un archivo CSV en Google Drive. Está diseñado para ejecutarse periódicamente (por ejemplo, una vez a la semana) para mantener el archivo siempre actualizado.

2.  **Aplicación Web (`app.py`):** Una aplicación web ligera construida con Flask. Lee los datos directamente desde el archivo CSV público en Google Drive y los presenta en una interfaz limpia, elegante y totalmente responsive.

---

## ✨ Características Principales

### Scraper (El Recolector)

* **Autenticación Segura:** Inicia sesión en Biwenger de forma segura.
* **Extracción Completa:** Descarga todos los comunicados del tablón, incluyendo autor, título, fecha y contenido HTML original.
* **Almacenamiento en la Nube:** Guarda y actualiza un archivo CSV centralizado en Google Drive.
* **Automatización Total:** Diseñado para ser ejecutado como un **Cloud Run Job** y programado con **Cloud Scheduler** para una ejecución desatendida.
* **Gestión de Secretos:** Todas las credenciales (Biwenger, Google) se gestionan de forma segura a través de **Google Secret Manager**.

### Aplicación Web (El Museo)

* **Interfaz Limpia:** Un diseño elegante y minimalista, con un tema claro y toques de color para una legibilidad perfecta en cualquier dispositivo.
* **Tres Secciones:**
    * **Comunicados:** Visualiza todos los mensajes con su formato original, ordenados por fecha. Incluye un buscador en tiempo real.
    * **Participación:** Un ranking que muestra qué participante ha publicado más comunicados, con una tabla ordenable.
    * **Palmarés:** Un resumen histórico de los ganadores, podios y otros datos curiosos de temporadas pasadas.
* **Desplegado en la Nube:** Alojado en **Cloud Run** para un rendimiento escalable y eficiente.
* **Independiente:** La web solo lee el CSV, por lo que sigue funcionando aunque el scraper no se ejecute.

---

## 💻 Tecnologías Utilizadas

* **Backend (Scraper):** Python, Requests, BeautifulSoup, Google Cloud SDK.
* **Backend (Web):** Python, Flask.
* **Frontend:** HTML, Tailwind CSS, JavaScript.
* **Cloud y Despliegue:** Google Cloud Run (Jobs y Services), Cloud Scheduler, Secret Manager, Google Drive API, Docker.