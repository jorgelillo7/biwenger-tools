# 🛠 OPERATIONS - Biwenger Tools

Este documento centraliza comandos reproducibles para **desarrollo, pruebas, despliegue y mantenimiento**.


---
### 🚀 Configuración de Linter y Formateo Automático con Black y Flake8

Este documento detalla cómo configurar tu entorno de desarrollo en VS Code para aplicar linter y formateo automático utilizando **Flake8** y **Black Formatter**. Esto asegura que tu código Python mantenga un estilo consistente y libre de errores.

---

#### 🛠️ Requisitos Previos

Antes de comenzar, asegúrate de tener:

* **Python 3.x** instalado en tu sistema.
* **Visual Studio Code** instalado.

---

#### 📦 Configuración del Entorno Virtual y Herramientas

Sigue estos pasos para preparar tu entorno de desarrollo:

##### 1. Crear y Activar el Entorno Virtual

En la raíz de tu proyecto, ejecuta los siguientes comandos en tu terminal:

```bash
python3 -m venv venv
source venv/bin/activate  # En Windows usa: .venv\Scripts\activate
````

### 2\. Instalar Black y Flake8

Con el entorno virtual activado, instala las herramientas de linting y formateo:

```bash
pip install flake8 black
pip install flake8-bugbear
```

-----

#### ⚙️ Configuración en Visual Studio Code

Para que VS Code utilice estas herramientas, necesitarás instalar algunas extensiones y ajustar la configuración del espacio de trabajo.

##### 1\. Instalar las Extensiones Necesarias

Abre VS Code y ve a la vista de Extensiones (`Ctrl+Shift+X` o `Cmd+Shift+X` en macOS). Instala las siguientes extensiones:

  * **Python**: La extensión oficial de Microsoft (ID: `ms-python.python`). Es fundamental para el soporte de Python en VS Code.
  * **Black Formatter**: La extensión oficial de Microsoft para Black (ID: `ms-python.black-formatter`).

#### 2\. Seleccionar el Intérprete de Python

Es crucial que VS Code sepa qué intérprete de Python usar para tu proyecto.

1.  Abre la **Paleta de Comandos** (`Ctrl+Shift+P` o `Cmd+Shift+P`).
2.  Escribe `Python: Select Interpreter` y presiona `Enter`.
3.  Selecciona el intérprete de tu proyecto, que debería aparecer como: `./venv/bin/python`

##### 3\. Configurar Linting y Formateo Automático

Ahora, configura tu espacio de trabajo para usar Black y Flake8.

1.  Abre la **Paleta de Comandos** (`Ctrl+Shift+P` o `Cmd+Shift+P`).
2.  Escribe `Preferences: Open Workspace Settings (JSON)` y selecciona esta opción. Esto abrirá el archivo `settings.json` dentro de la carpeta `.vscode` de tu proyecto.
3.  Copia y pega la siguiente configuración dentro de las llaves `{}` de tu archivo `settings.json`. Si ya tienes configuraciones, simplemente añade estas líneas, asegurándote de no duplicar llaves.

```json
{
    // Activa el linter de Python
    "python.linting.enabled": true,
    // Establece flake8 como tu linter
    "python.linting.flake8Enabled": true,

    // --- Configuración para Black Formatter ---
    // Establece Black como el formateador por defecto para Python
    "editor.defaultFormatter": "ms-python.black-formatter",
    // Formatea el código automáticamente al guardar
    "editor.formatOnSave": true,

    // (Opcional) Permite que las acciones de código (como los arreglos del linter) se apliquen al guardar
    "editor.codeActionsOnSave": {
        "source.fixAll": "explicit",
        "source.organizeImports": "explicit" // Opcional: para ordenar automáticamente los imports con isort
    }
}
```

##### 4\. Configuración de Flake8 (Opcional)

Puedes personalizar las reglas de Flake8 creando un archivo llamado `.flake8` en la raíz de tu proyecto. Un ejemplo común para compatibilidad con Black es:

```ini
# .flake8
[flake8]
max-line-length = 88
ignore = E203, W503
exclude = .git,
          __pycache__,
          .venv,
          venv,
          *.md
```

  * `max-line-length = 88`: Alinea la longitud máxima de línea con la de Black.
  * `ignore = E203, W503`: Ignora reglas que pueden entrar en conflicto con Black.
  * `exclude`: Lista de directorios y archivos a ignorar por Flake8.

-----

#### ✅ Verificación

Una vez que hayas completado estos pasos:

1.  **Reinicia VS Code**.
2.  Abre un archivo Python (`.py`) en tu proyecto.
3.  Escribe código que contenga un error de sintaxis o que no siga las reglas de estilo (por ejemplo, una línea muy larga).
4.  Deberías ver advertencias o errores subrayados por Flake8.
5.  Al guardar el archivo (`Ctrl+S` o `Cmd+S`), Black debería formatear automáticamente el código.

---

---

### 1️⃣ Entorno Local

* **1.1 Web App**
    * **Crear entorno virtual e instalar dependencias:**
        ```bash
        cd web
        python3 -m venv venv
        source venv/bin/activate  # Windows: venv\Scripts\activate
        pip install -r requirements.txt
        ```
    * **Ejecutar localmente desde la raíz:**
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
        cd scraper-job
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
        ```
    * **Ejecutar local desde la raíz:**
        ```bash
        python3 -m scraper-job.get_messages
        ```
    * **Docker local desde la raíz:**
        ```bash
        docker build -t biwenger-scraper:latest -f scraper-job/Dockerfile .
        docker run --rm biwenger-scraper:latest
        ```

* **1.3 Teams Analyzer**
    * **Crear entorno virtual e instalar dependencias:**
        ```bash
        cd teams_analyzer
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
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