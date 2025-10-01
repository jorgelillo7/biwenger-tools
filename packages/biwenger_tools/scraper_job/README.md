# 🤖 Scraper de Mensajes de Biwenger

Este proyecto es un job de scraping automatizado que extrae los comunicados (mensajes) de tu liga de Biwenger y los guarda en archivos CSV. El objetivo principal es la creación de un historial de datos que luego puede ser utilizado por otras herramientas.

Los datos se guardan en un archivo CSV y se sincronizan directamente con una carpeta de Google Drive para facilitar su acceso.

## 🚀 Funcionalidades Clave

* **Extracción de datos**: Recopila automáticamente mensajes importantes del feed de tu liga de Biwenger.
* **Almacenamiento en CSV**: Organiza los datos extraídos en un formato estructurado.
* **Sincronización con Google Drive**: Sube los archivos CSV generados a una carpeta específica en tu Google Drive.

## ⚙️ Configuración y Uso

Para ejecutar y configurar este proyecto, consulta las instrucciones detalladas en el documento principal de operaciones.

* **Instalación y dependencias**: Revisa la sección **`1.2 Scraper Job`** en `operations.md`.
* **Configuración de Google API**: Sigue los pasos de configuración de credenciales de Google API.
* **Ejecución y despliegue**: Los comandos para la ejecución local y el despliegue en Google Cloud se encuentran en `operations.md` **`2.2 Scraper Job`**.

---

### **Configuración de Google API (Solo la primera vez, si usas OAuth)**

Si quisieras que el script cree los CSV directamente en tu **Drive personal** de forma automática, el flujo sería este:

* **Configura la Pantalla de Consentimiento:**

  * Ve a la **Consola de Google Cloud** > **APIs y servicios** > **Pantalla de consentimiento de OAuth**.
  * Selecciona **Externo**, rellena los datos de tu aplicación y añade tu email como usuario de prueba.

* **Crea las Credenciales:**

  * En **APIs y servicios** > **Credenciales**, haz clic en **+ CREAR CREDENCIALES** > **ID de cliente de OAuth**.
  * Selecciona **Aplicación de escritorio**.
  * Descarga el archivo JSON y renómbralo a `client_secrets.json` en la carpeta del scraper.

* **Configura la Carpeta en Drive:**

  * Crea una carpeta en tu Google Drive para los CSV.
  * Copia el ID de la carpeta desde la URL y pégalo en el archivo `.env` del scraper.

> ⚠️ Nota: Este flujo permite que el script escriba en tu Drive personal, pero **el token de OAuth caduca y refrescarlo es engorroso**. Por eso, hemos decidido usar una **Service Account**, que no caduca.
> ⚠️ Limitación: Como tu cuenta no es Google Workspace, la Service Account **no puede crear archivos directamente en tu Drive personal**. Para que funcione, **debes crear manualmente los CSV vacíos en la carpeta de Drive antes de ejecutar el scraper**.

---

## ⚠️ Notas Importantes

* **Primera ejecución local**: Requiere autorización manual en el navegador para acceder a Google Drive (solo si usas OAuth).
* **Seguridad**: Nunca subas el archivo `biwenger-tools-sa.json` al repositorio.