# Guía de Puesta en Marcha y Despliegue

Esta guía detalla los pasos para configurar y ejecutar el proyecto tanto en un entorno local como en Google Cloud.

## 🏠 Entorno Local (Scraper)

Pasos para configurar y ejecutar el script `get_messages.py` en tu máquina.

### 1. Instalación de Dependencias
```bash
# Crea un entorno virtual (solo la primera vez)
python3 -m venv venv

# Activa el entorno (en macOS/Linux)
source venv/bin/activate

# En Windows usa: venv\Scripts\activate
```

```bash
pip3 install -r requirements.txt
```

### 2. Configuración de Google API (Solo la primera vez)

Sigue estos pasos para permitir que el script acceda a tu Google Drive.

#### Configura la Pantalla de Consentimiento:
- Ve a la **Consola de Google Cloud** > **APIs y servicios** > **Pantalla de consentimiento de OAuth**.
- Selecciona **Externo**, rellena los datos de tu aplicación y añade tu email como usuario de prueba.

#### Crea las Credenciales:
- En **APIs y servicios** > **Credenciales**, haz clic en **+ CREAR CREDENCIALES** > **ID de cliente de OAuth**.
- Selecciona **Aplicación de escritorio**.
- Descarga el archivo JSON y renómbralo a `client_secrets.json` en la carpeta del scraper.

#### Configura la Carpeta en Drive:
- Crea una carpeta en tu Google Drive para los CSVs.
- Copia el ID de la carpeta desde la URL y pégalo en el archivo `.env` del scraper.

### 3. Ejecución (desde raiz)

La primera vez que ejecutes el script, se abrirá un navegador para que autorices el acceso a tu cuenta de Google. Esto creará un archivo `token.json` que se usará en las siguientes ejecuciones.

```bash
python3 -m scraper-job.get_messages
```

### ALT. Docker (desde raiz)
```
docker build -t biwenger-scraper:latest -f scraper-job/Dockerfile .

```

```
docker run --rm biwenger-scraper:latest
```

## 🚀 Despliegue en Google Cloud

Pasos para desplegar el scraper como un Cloud Run Job automatizado.

### 1. Secret Manager

Guarda todas tus credenciales de forma segura.

#### Credenciales de Google (desde archivo):
```bash
# Asegúrate de que los archivos están en la carpeta del scraper
gcloud secrets create client_secrets_json --data-file="client_secrets.json"
gcloud secrets create token_json --data-file="token.json"
```

#### Credenciales de Biwenger y Drive (como texto):
```bash
echo -n "TU_EMAIL@gmail.com" | gcloud secrets create biwenger-email --data-file=-
echo -n "TU_CONTRASEÑA" | gcloud secrets create biwenger-password --data-file=-
echo -n "ID_DE_LA_CARPETA_DE_DRIVE" | gcloud secrets create gdrive-folder-id --data-file=-
```

#### Para actualizar un secreto (ej. token.json):
```bash
gcloud secrets versions add token_json --data-file="token.json"
```

### 2. Cloud Run Jobs

Construye la imagen de Docker, despliega el job y ejecútalo.

#### Construye la imagen Docker:
```bash
gcloud builds submit --tag gcr.io/biwenger-tools/scraper-job

docker build --platform linux/amd64 \
  -t gcr.io/biwenger-tools/scraper-job \
  -f scraper-job/Dockerfile .

docker push gcr.io/biwenger-tools/scraper-job

```

#### Crea el Job (solo la primera vez):
Usa un nombre único y agrupa todos los secretos en un solo flag.

```bash
gcloud run jobs create biwenger-scraper-data \
  --image gcr.io/biwenger-tools/scraper-job \
  --region europe-southwest1 \
  --set-secrets="/gdrive_client/client_secrets.json=client_secrets_json:latest" \
  --set-secrets="/gdrive_token/token.json=token_json:latest" \
  --set-secrets="/biwenger_email/biwenger-email=biwenger-email:latest" \
  --set-secrets="/biwenger_password/biwenger-password=biwenger-password:latest" \
  --set-secrets="/gdrive_folder_id/gdrive-folder-id=gdrive-folder-id:latest"
```

#### Actualiza el Job (para nuevas versiones de código):
```bash
  gcloud run jobs update biwenger-scraper-data \
  --image gcr.io/biwenger-tools/scraper-job \
  --region europe-southwest1
```

o para añadirle nuevos secretos
```bash
gcloud run jobs update biwenger-scraper-data \
  --image gcr.io/biwenger-tools/scraper-job \
  --region europe-southwest1 \
  --set-secrets="/gdrive_client/client_secrets.json=client_secrets_json:latest" \
  --set-secrets="/gdrive_token/token.json=token_json:latest" \
  --set-secrets="/biwenger_email/biwenger-email=biwenger-email:latest" \
  --set-secrets="/biwenger_password/biwenger-password=biwenger-password:latest" \
  --set-secrets="/gdrive_folder_id/gdrive-folder-id=gdrive-folder-id:latest"
  ```

#### Ejecuta el Job manualmente:
```bash
  gcloud run jobs execute biwenger-scraper-data --region europe-southwest1
```

---

## 📋 Notas Importantes

- **Primera ejecución local**: Requiere autorización manual en el navegador
- **Seguridad**: Nunca subas archivos `client_secrets.json` o `token.json` al repositorio
- **Actualización de secrets**: Usa `gcloud secrets versions add` para actualizar credenciales
- **Monitoreo**: Revisa los logs en Google Cloud Console para verificar la ejecución