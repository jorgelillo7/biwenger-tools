# Release Notes del Proyecto Biwenger

Aquí se documenta la increíble y a veces caótica evolución de nuestro pequeño gran proyecto para inmortalizar el salseo de la liga.

---

### **v3.1 - La Sincronización Definitiva (3 de Septiembre, 2025)**

Una actualización que consolida la arquitectura del proyecto y simplifica el flujo de trabajo de desarrollo, eliminando los errores de configuración más comunes y preparando la base para futuras expansiones.

* **⚙️ Entorno de Desarrollo Unificado**: Se centraliza el entorno virtual de Python en un único `venv` en la raíz del proyecto. Este cambio crucial resuelve conflictos de dependencias entre módulos y asegura que el linter, el formateador y el intérprete funcionen de manera consistente.
* **📦 Gestión Simplificada de Dependencias**: Al consolidar el `venv`, los comandos de instalación se simplifican, eliminando la necesidad de activar y desactivar múltiples entornos. Todas las dependencias ahora se instalan en un solo lugar, mejorando la coherencia.
* **✅ Integración Continua Local y en la Nube**: Se han verificado y optimizado los procesos de ejecución, construcción de imágenes y despliegue para todos los módulos (`web`, `scraper-job`, `teams_analyzer`), garantizando que funcionen sin problemas tanto en entornos locales (con Docker) como en Google Cloud Platform. (menos teams_analyzer)
* **🔗 Importaciones y Estilo de Código Uniforme**: Se ha validado la importación de módulos del `core` y la aplicación de reglas de estilo de código con **Flake8** y **Black**, asegurando que el proyecto mantenga su calidad y cohesión a lo largo de las nuevas funcionalidades.

---

### **v3.0 - El Espía Táctico y el Arquitecto (22 de Agosto, 2025)**

Una actualización mayor que no solo introduce una nueva herramienta de análisis, sino que también reconstruye los cimientos del proyecto para hacerlo más robusto y escalable.

* **🚀 Nuevo Módulo `teams-analyzer`**: Se introduce una nueva herramienta independiente para el análisis táctico profundo de la liga, diseñada para ser ejecutada localmente.
* **🕵️ Scraping Avanzado con Selenium**: El analizador extrae datos de rendimiento y coeficientes de webs especializadas como "Analítica Fantasy" y "Jornada Perfecta".
* **📊 Análisis 360º**: El script evalúa todas las plantillas de la liga y los jugadores libres en el mercado, ofreciendo una visión completa de la competencia.
* **📬 Notificaciones por Telegram**: Al finalizar, el script envía automáticamente el informe `analisis_biwenger.csv` a un chat de Telegram configurado.
* **🏗️ Gran Refactor Arquitectónico**: ¡Un hito clave! Se realiza una reestructuración profunda del código para crear módulos reutilizables en los directorios `core` (para clientes de APIs como Biwenger y Google) y `logic` (para el procesamiento de datos). Este cambio reduce drásticamente la duplicación de código, mejora la mantenibilidad y sienta las bases para futuras expansiones del proyecto.

---

### **v2.5 - El Viajero del Tiempo (18 de Agosto, 2025)**

Una actualización fundamental que convierte la web en un archivo histórico, permitiendo navegar entre diferentes temporadas de forma fluida e intuitiva.

* **✈️ Navegación Multi-Temporada:** ¡La funcionalidad estrella! Se añade un menú desplegable en la cabecera que permite seleccionar y visualizar los datos (`Comunicados`, `Salseo`, `Participación`, `Ligas Especiales`) de cualquier temporada pasada.
* **💾 Scraper Multi-Temporada:** El script `get_messages.py` ahora es consciente de la temporada activa. Genera y actualiza los archivos CSV con un sufijo de temporada (ej. `comunicados_25-26.csv`), manteniendo los datos de cada año perfectamente aislados y preservados.
* **⚖️ Nueva Sección "Fair Play":** Se crea una página de reglamento completa, con un índice navegable, contenido dinámico (como la lista de Ligas Especiales) y un diseño mejorado para la lectura de las normas.
* **🖥️ Panel de Admin Mejorado:** La sección "VAR (Admin)" ahora muestra el estado de los archivos correspondientes a la temporada que se está visualizando y avisa si alguno de los ficheros dinámicos lleva más de 7 días sin actualizarse.
* **📱 Mejoras de UI/UX:** Se corrige la visualización del menú de navegación en dispositivos móviles para evitar que los textos se corten o solapen, y se solucionan problemas de posicionamiento en los menús desplegables.


### **v2.0 - El Portal Definitivo (12 de Agosto, 2025)**

Una re-arquitectura clave para hacer el proyecto más robusto, seguro y fácil de mantener, sentando las bases para el futuro.

* **🚀 (Beta) Nueva Sección "Ligas Especiales":** Se añade la funcionalidad más esperada. La web ahora puede leer y mostrar datos de competiciones especiales directamente desde un **Google Sheet**, permitiendo una gestión y actualización manual extremadamente sencilla.
* **⚙️ Externalización de la Configuración:** Tanto el scraper como la aplicación web ahora utilizan un archivo `config.py` para gestionar sus parámetros. Las credenciales y datos sensibles se cargan de forma segura desde un archivo `.env` en local o desde Secret Manager / variables de entorno en la nube.
* **🐛 Correcciones de Estabilidad:** Se solucionan bugs relacionados con la categorización de mensajes y la ordenación de fechas, asegurando que los datos se procesan y muestran siempre de forma correcta.

### **v1.5 - El Portal Inteligente (12 de Agosto, 2025)**

Una actualización masiva centrada en la inteligencia de datos y la expansión de funcionalidades, haciendo la web más rápida y completa.

* **✨ Nueva Categorización de Mensajes:** El script ahora analiza los títulos de los comunicados y los clasifica automáticamente como `comunicado`, `dato` o `cesion`, añadiendo una nueva columna al CSV.
* **⚡️ Optimización de la Participación:** Se crea un nuevo archivo, `participacion.csv`, que es generado automáticamente por el scraper. La web ahora lee este archivo pre-procesado, haciendo que la pestaña de "Participación" cargue de forma instantánea.
* **🌶️ Nueva Sección "Salseo":** Se crea una nueva página dedicada a los "Datos Curiosos" (Mr. Lucen) y a las "Cesiones", con filtros para alternar entre ambas categorías.
* **📊 Tabla de Participación Mejorada:** La sección de participación se rediseña por completo para mostrar un desglose detallado del número de comunicados, datos y cesiones de cada jugador.
* **📄 Paginación en la Página Principal:** Se implementa un sistema de paginación en la sección de "Comunicados" para manejar un gran volumen de mensajes de forma ordenada.
* **🔍 Búsqueda Global:** El buscador de la página principal y de "Salseo" ahora busca en la totalidad de los mensajes, no solo en los visibles en la página actual.

### **v1.0 - El Autómata (07 de Agosto, 2025)**

¡La versión definitiva (por ahora)! El proyecto alcanza la madurez con una automatización completa y una arquitectura profesional.

* **✨ ¡Automatización Total!** El script que recoge los datos ahora es un **Cloud Run Job**, programado para ejecutarse automáticamente cada semana con **Cloud Scheduler**. ¡Se acabaron las ejecuciones manuales!
* **🔒 Seguridad Máxima:** Todas las credenciales sensibles (Biwenger, Google Drive) se han movido a **Google Secret Manager**. El código está limpio de secretos.
* **🏗️ Arquitectura Desacoplada:** El proyecto se divide oficialmente en dos partes: el **scraper automatizado** (el job) y la **aplicación web**, cada uno con su propio ciclo de vida.
* **🐛 Corrección de Errores:** Se solucionan errores de permisos y configuración de `gcloud` para un despliegue robusto.

### **v0.5 - El Portal (06 de Agosto, 2025)**

La aplicación web evoluciona de una simple página a un portal completo para la liga.

* **🎨 Nuevo Diseño:** Se implementa un tema visual más limpio y elegante, mejorando la legibilidad en todos los dispositivos.
* **📊 Nueva Sección "Participación":** Se añade una página que muestra un ranking de los comunicados publicados por cada participante, con una tabla ordenable.
* **🏆 Nueva Sección "Palmarés":** Se crea una sección para mostrar el historial de ganadores, podios y otros datos curiosos de temporadas pasadas, leídos desde un segundo archivo CSV.
* **🐛 Correcciones de Datos:** Se mejora la lógica para identificar correctamente a los autores de los comunicados y se solucionan problemas de formato en la sección de Palmarés.

### **v0.4 - Conexión a la Nube (05 de Agosto, 2025)**

Un paso crucial: separamos los datos de la aplicación para hacer el sistema más flexible y escalable.

* **☁️ Integración con Google Drive:** El script de Python se modifica para subir el archivo `biwenger_comunicados.csv` a una carpeta de Google Drive.
* **🌐 Lectura desde la Nube:** La aplicación Flask ahora lee los datos directamente desde una URL pública del CSV en Google Drive, en lugar de un archivo local.
* **🚀 Preparación para el Despliegue:** Se containeriza la aplicación web con **Docker** y se prepara para su despliegue en **Cloud Run**.

### **v0.3 - El Museo (04 de Agosto, 2025)**

Nace la primera interfaz visual para leer los comunicados de una forma más amigable que un simple CSV.

* **🐍 Nace la Web:** Se crea una aplicación web básica con **Flask**.
* **🎨 Primera Interfaz:** Se diseña una plantilla HTML con **Tailwind CSS** para mostrar los comunicados en tarjetas.
* **🔍 Funcionalidad de Búsqueda:** Se añade una barra de búsqueda con JavaScript para filtrar los comunicados en tiempo real.

### **v0.2 - El Recolector (03 de Agosto, 2025)**

El script evoluciona para convertirse en una herramienta de backup funcional.

* **💾 Guardado en CSV:** El script ahora guarda todos los datos extraídos (fecha, título, autor, contenido) en un archivo `biwenger_comunicados.csv`.
* **🔄 Lógica de Actualización:** El script se vuelve inteligente: lee el CSV existente y añade solo los comunicados nuevos, manteniendo el archivo siempre al día y ordenado.
* **🆔 ID Único:** Se implementa un sistema de hash para asignar un ID único a cada comunicado, evitando duplicados.

### **v0.1 - La Chispa (02 de Agosto, 2025)**

El origen de todo. Un único script de Python con un objetivo claro.

* **🔑 Inicio de Sesión:** El script es capaz de autenticarse en Biwenger usando credenciales locales.
* **📊 Extracción Básica:** Se conecta a la API interna de Biwenger para obtener datos básicos de la liga, como el nombre y el número de participantes.
* **💻 Salida por Consola:** Toda la información se muestra directamente en la terminal.