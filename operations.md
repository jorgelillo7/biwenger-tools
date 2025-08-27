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

---

### 2️⃣ Despliegue en Google Cloud
```bash
gcloud auth login
gcloud config set project biwenger-tools
gcloud auth configure-docker
```

* **2.1 Web App**
    * **Construir y subir imagen Docker desde la raíz:**
        ```bash
        docker build --platform linux/amd64 -t gcr.io/biwenger-tools/web -f web/Dockerfile .
        docker push gcr.io/biwenger-tools/web
        ```
    * **Deploy usando script que lee .env:**
        ```bash
        cd /web
        ./deploy.sh
        ```

* **2.2 Scraper Job**
    * **Construir y subir imagen Docker:**
        ```bash
        docker build --platform linux/amd64 -t gcr.io/biwenger-tools/scraper-job -f scraper-job/Dockerfile .
        docker push gcr.io/biwenger-tools/scraper-job
        ```
    * **Crear Job (solo la primera vez):**
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
    * **Actualizar Job (nueva versión o secretos):**
        ```bash
        gcloud run jobs update biwenger-scraper-data \
            --image gcr.io/biwenger-tools/scraper-job \
            --region europe-southwest1
        ```

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

---

### 4️⃣ Limpieza de imágenes y control de costos

* **Listar imágenes:**
    ```bash
    gcloud container images list --repository=gcr.io/biwenger-tools
    ```

    ```
    gcloud container images list-tags gcr.io/biwenger-tools/web
    gcloud container images list-tags gcr.io/biwenger-tools/scraper-job
    ```


* **Borrar imágenes antiguas:**
    ```bash
    gcloud container images list-tags gcr.io/biwenger-tools/web \
    --format="get(digest)" \
    --filter="tags!=latest" | xargs -I {} gcloud container images delete -q gcr.io/biwenger-tools/web@{}
    ```

    ```bash
    gcloud container images list-tags gcr.io/biwenger-tools/scraper-job \
    --format="get(digest)" \
    --filter="tags!=latest" | xargs -I {} gcloud container images delete -q gcr.io/biwenger-tools/scraper-job@{}
    ```

---

### 5️⃣ Notas Importantes

* La primera ejecución local del scraper requiere autorización manual en Google.
* Nunca subir archivos `client_secrets.json` o `token.json`.
* Revisar logs en Cloud Run / GCP Console ante fallos.
* Mantener `.env` en la raíz de cada miniproyecto para ejecución desde la raíz.