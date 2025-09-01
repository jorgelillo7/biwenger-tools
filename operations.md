# 🛠 OPERATIONS - Biwenger Tools

Este documento centraliza comandos reproducibles para **desarrollo, pruebas, despliegue y mantenimiento**.

---

### 1️⃣ Entorno Local

* **1.1 Web App**
    * **Crear entorno virtual e instalar dependencias:**
        ```bash
        python3 -m venv venv
        source venv/bin/activate  # Windows: venv\Scripts\activate
        pip install -r web/requirements.txt
        ```
    * **Ejecutar localmente:**
        ```bash
        python3 -m web.app
        ```
    * **Docker local desde la raíz:**
        ```bash
        docker build -t biwenger-web:latest -f web/Dockerfile .
        docker run -p 8080:8080 biwenger-web:latest
        ```

* **1.2 Scraper Job**
    * **Crear entorno virtual e instalar dependencias:**
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        pip install -r scraper-job/requirements.txt
        ```
    * **Ejecutar local desde la raíz:**
        ```bash
        python3 -m scraper-job.get_messages
        ```
    * **Docker local:**
        ```bash
        docker build -t biwenger-scraper:latest -f scraper-job/Dockerfile .
        docker run --rm biwenger-scraper:latest
        ```

* **1.3 Teams Analyzer**
    * **Crear entorno virtual e instalar dependencias:**
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        pip install -r teams_analyzer/requirements.txt
        ```
    * **Configurar .env con credenciales de Biwenger y Telegram.**
    * **Ejecutar local desde la raíz:**
        ```bash
        python3 -m teams_analyzer.teams_analyzer
        ```
    * **Docker local:**
        ```bash
        docker build -t biwenger-teams-analyzer:latest -f teams_analyzer/Dockerfile .
        docker run --rm --shm-size=2g biwenger-teams-analyzer:latest
        ```

---

### 2️⃣ Despliegue en Google Cloud
```bash
gcloud auth login
gcloud config set project biwenger-tools
gcloud auth configure-docker europe-southwest1-docker.pkg.dev
```

* **2.1 Web App**
    * **Construir y subir imagen Docker desde la raíz:**
        ```bash
        docker build --platform linux/amd64 -t europe-southwest1-docker.pkg.dev/biwenger-tools/biwenger-docker/web -f web/Dockerfile .
        docker push europe-southwest1-docker.pkg.dev/biwenger-tools/biwenger-docker/web
        ```
    * **Deploy usando script que lee .env:**
        ```bash
        cd web
        ./deploy.sh
        ```

* **2.2 Scraper Job**
    * **Construir y subir imagen Docker:**
        ```bash
        docker build --platform linux/amd64 -t europe-southwest1-docker.pkg.dev/biwenger-tools/biwenger-docker/scraper-job -f scraper-job/Dockerfile .
        docker push europe-southwest1-docker.pkg.dev/biwenger-tools/biwenger-docker/scraper-job
        ```
    * **Crear Job (solo la primera vez):**
        ```bash
        gcloud run jobs create biwenger-scraper-data \
            --image europe-southwest1-docker.pkg.dev/biwenger-tools/biwenger-docker/scraper-job \
            --region europe-southwest1 \
            --set-secrets="/gdrive_client/client_secrets.json=client_secrets_json:latest" \
            --set-secrets="/gdrive_token/token.json=token_json:latest" \
            --set-secrets="/biwenger_email/biwenger-email=biwenger-email:latest" \
            --set-secrets="/biwenger_password/biwenger-password=biwenger-password:latest" \
            --set-secrets="/gdrive_folder_id/gdrive-folder-id=gdrive-folder-id:latest"
        ```
    * **Actualizar Job (nueva versión o secretos):**
        ```bash
        gcloud run jobs update biwenger-scraper-data \
            --image europe-southwest1-docker.pkg.dev/biwenger-tools/biwenger-docker/scraper-job \
            --region europe-southwest1
        ```

        ```bash
        gcloud run jobs update biwenger-scraper-data \
        --image europe-southwest1-docker.pkg.dev/biwenger-tools/biwenger-docker/scraper-job \
        --region europe-southwest1 \
        --set-secrets="/gdrive_sa/biwenger-tools-sa.json=biwenger_tools_sa:latest" \
        --set-secrets="/biwenger_email/biwenger-email=biwenger-email:latest" \
        --set-secrets="/biwenger_password/biwenger-password=biwenger-password:latest" \
        --set-secrets="/gdrive_folder_id/gdrive-folder-id=gdrive-folder-id:latest"
        ```
    * **Ejecutar Job manualmente:**
        ```bash
        gcloud run jobs execute biwenger-scraper-data --region europe-southwest1
        ```

* **2.3 Teams Analyzer**
    * Pendiente: despliegue en Cloud Run cuando sea necesario.

---

### 3️⃣ Gestión de Secretos

* **Variables locales:** usar `.env` para desarrollo.
* **Producción:** usar Google Secret Manager.

#### ejemplos
```bash
# Asegúrate de que los archivos están en la carpeta dónde ejecutas el comando
gcloud secrets create biwenger_tools_sa --data-file="biwenger-tools-sa.json"
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

---

### 4️⃣ Limpieza de imágenes y control de costos

-----

#### Artifact Registry

  * **Crear repositorio Docker (1º vez):**
    ```
    gcloud artifacts repositories create biwenger-docker \
        --repository-format=docker \
        --location=europe-southwest1 \
        --description="Docker images for Biwenger Tools"
    ```
  * **Listar repositorios:**
    ```
    gcloud artifacts repositories list --project=biwenger-tools
    ```
  * **Listar imágenes:**
    ```
    gcloud artifacts docker images list europe-southwest1-docker.pkg.dev/biwenger-tools/biwenger-docker
    ```
  * **Limpiar imágenes antiguas (script):**
    ```
    ./clean-images-artifact.sh
    ```
    Este script elimina todas las versiones viejas de cada imagen, dejando solo la última con la etiqueta `latest`.
  * **Revisar costes (script):**
    ```
    ./check-gcp-costs.sh
    ```
    Este script muestra el almacenamiento usado y el uso de **Artifact Registry** y **Cloud Run**, comparándolo con el **Free Tier**.

-----

### 5️⃣ Notas importantes

-----

  * Nunca subir archivos `biwenger-tools-sa.json`.
  * Revisar logs en **Cloud Run** / **GCP Console** si hay fallos.
  * Mantener `.env` en la raíz de cada miniproyecto para su ejecución.