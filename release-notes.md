# Release Notes del Proyecto Biwenger

Aquí se documenta la increíble y a veces caótica evolución de nuestro pequeño gran proyecto para inmortalizar el salseo de la liga.

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