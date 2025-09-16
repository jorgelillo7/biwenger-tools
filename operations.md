# 🛠 OPERATIONS - Biwenger Tools

Este documento centraliza comandos reproducibles para **desarrollo, pruebas, despliegue y mantenimiento**.

---

### **Configuración del Entorno Local**

Antes de ejecutar cualquier comando, asegúrate de tener un entorno virtual general configurado para evitar conflictos de dependencias entre los diferentes módulos.

**Nota:** El entorno virtual se ha configurado de forma centralizada en la raíz del proyecto para simplificar el flujo de trabajo y evitar colisiones de dependencias entre los diferentes módulos.

```
brew install bazelisk
brew install buildifier
```

extensión vs code Bazel (The Bazel Team)
bazel clean --expunge

pip install pip-tools
```
{
  for req_file in core/requirements.txt scraper_job/requirements.txt teams_analyzer/requirements.txt web/requirements.txt; do
    echo; echo "# From: $req_file"; cat "$req_file";
  done
} > requirements.in
```
pip-compile requirements.in -o requirements_lock.txt






Sí, por supuesto. Tienes toda la razón, es una idea excelente.

Añadir ese paso previo es el **flujo de trabajo profesional y recomendado** para un monorepo. Mantiene cada módulo (`core`, `web`, etc.) declarando sus propias dependencias, lo que lo hace mucho más limpio y escalable.

He reescrito la sección del `README` para reflejar este proceso mejorado.

-----

## 📦 Cómo Añadir o Actualizar Dependencias de Python

Nuestro proyecto usa un sistema de tres niveles para gestionar las dependencias, manteniendo los módulos aislados y garantizando builds 100% reproducibles.

1.  **`[módulo]/requirements.txt`** (ej: `core/requirements.txt`): Es el **punto de partida y la fuente de verdad**. Aquí es donde tú, como desarrollador, añades o quitas las librerías que necesita un módulo específico.
2.  **`requirements.in`**: Es un fichero **intermedio y autogenerado**. Consolida las listas de todos los módulos en un solo lugar para la siguiente herramienta. **Nunca debes editar este fichero a mano.**
3.  **`requirements_lock.txt`**: Es el **fichero final y bloqueado** que genera el ordenador. Contiene la lista exacta de todas las librerías (directas e indirectas) con sus versiones y hashes, que es lo que Bazel usa. **Nunca debes editar este fichero a mano.**

El flujo de trabajo para añadir una nueva librería (usaremos `numpy` en el módulo `core` como ejemplo) es el siguiente:

### \#\#\# Paso 1: Añade la librería al `requirements.txt` del Módulo

Decides que el módulo `core` necesita `numpy`. Abres `core/requirements.txt` y lo añades.

**Fichero: `core/requirements.txt`**

```diff
requests
google-api-python-client
google-auth-oauthlib
google-auth
pytz
python-dateutil
black
flake8
pytest
requests-mock
+ numpy
```

-----

### \#\#\# Paso 2: Regenera el `requirements.in` Central

Ahora, ejecuta este comando desde la raíz del proyecto. Recogerá los cambios que hiciste en `core/requirements.txt` y actualizará el fichero central.

```bash
{
  for req_file in core/requirements.txt scraper_job/requirements.txt teams_analyzer/requirements.txt web/requirements.txt; do
    echo; echo "# From: $req_file"; cat "$req_file";
  done
} > requirements.in
```

-----

### \#\#\# Paso 3: Regenera el Fichero de Lock

Este comando lee el `requirements.in` que acabas de generar y resuelve todas las dependencias, creando el `requirements_lock.txt` final.

*(Recuerda tener `pip-tools` instalado: `pip install pip-tools`)*

```bash
pip-compile requirements.in -o requirements_lock.txt
```

-----

### \#\#\# Paso 4: Usa la Nueva Librería en el `BUILD.bazel`

Ahora que la librería ya está disponible para Bazel, ve a `core/BUILD.bazel` y añádela a la lista de dependencias (`deps`) del `py_library`.

Recuerda que Bazel convierte los guiones (-) a guiones bajos (_). Para numpy, el nombre es el mismo.

**Fichero: `core/BUILD.bazel`**

```python
py_library(
    name = "core",
    srcs = glob(["*.py"]),
    deps = [
        "@pypi//requests",
        # ... (resto de dependencias)
        # Añadimos la nueva dependencia
        "@pypi//numpy",
    ],
    visibility = ["//visibility:public"],
)
```

-----

### \#\#\# Paso 5: Verifica con Bazel

Finalmente, ejecuta un comando de Bazel para confirmar que todo funciona.

```bash
bazel build //...
```

Si el comando termina con éxito, has añadido la dependencia de forma limpia, aislada y reproducible.














---

### 1️⃣ Entorno Local (comandos siempre desde la raíz)
* **1.1 Web App**
    * **Ejecutar localmente:**
        ```bash
            bazel run //web:web_dev_server
        ```
    * **Docker local:**
        ```bash
            bazel run //web:load_image_to_docker
            docker run --rm -p 8080:8080 bazel/web:latest
        ```

bazel run //web:push_image_to_gcp

* **1.2 Scraper Job**
    * **Ejecutar local:**
        ```bash
        python3 -m scraper_job.get_messages
        ```
    * **Docker local:**
        ```bash
        docker build -t biwenger-scraper:latest -f scraper_job/Dockerfile .
        docker run --rm biwenger-scraper:latest
        ```

* **1.3 Teams Analyzer**
    * **Configurar .env con credenciales de Biwenger y Telegram.**
    * **Ejecutar local:**
        ```bash
        python3 -m teams_analyzer.teams_analyzer
        ```
    * **Docker local:**
        ```bash
        docker build -t biwenger-teams-analyzer:latest -f teams_analyzer/Dockerfile .
        docker run --rm --shm-size=2g biwenger-teams-analyzer:latest
        ```
* **1.4: Pruebas Unitarias**
Las pruebas son esenciales para asegurar la calidad y fiabilidad del código. Con **`pytest`**, puedes ejecutar todas las pruebas desde la raíz del proyecto para validar que todo funciona correctamente.

```bash
# Ejecuta todas las pruebas unitarias del proyecto
pytest

# Para ejecutar las pruebas de un módulo específico, por ejemplo, el core:
pytest core/tests/
```

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
        docker build --platform linux/amd64 -t europe-southwest1-docker.pkg.dev/biwenger-tools/biwenger-docker/scraper_job -f scraper_job/Dockerfile .
        docker push europe-southwest1-docker.pkg.dev/biwenger-tools/biwenger-docker/scraper_job
        ```
    * **Crear Job (solo la primera vez):**
        ```bash
        gcloud run jobs create biwenger-scraper-data \
            --image europe-southwest1-docker.pkg.dev/biwenger-tools/biwenger-docker/scraper_job \
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
            --image europe-southwest1-docker.pkg.dev/biwenger-tools/biwenger-docker/scraper_job \
            --region europe-southwest1
        ```

        ```bash
        gcloud run jobs update biwenger-scraper-data \
        --image europe-southwest1-docker.pkg.dev/biwenger-tools/biwenger-docker/scraper_job \
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

En el modulo deseado activa el entorno virutal e instala las dependencias del requirement

```bash
python3 -m venv venv
source venv/bin/activate  # En Windows usa: .venv\Scripts\activate
```

##### 2. Instalar Black y Flake8 

Con el entorno virtual activado, instala las herramientas de linting y formateo (inluidas en cada requirements.txt)

```bash
pip install -r requirements.txt
pip install -e ../core
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