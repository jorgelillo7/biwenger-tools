# local:

pip3 install requests --break-system-packages
pip3 install beautifulsoup4 --break-system-packages
pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib --break-system-packages
pip3 install python-dotenv --break-system-packages
pip3 install google-cloud-secret-manager --break-system-packages
pip3 install google-auth --break-system-packages
pip3 install Unidecode --break-system-packages


python3 get_messages.py


## Guía: Configurar API de Drive para Cuentas Personales (OAuth 2.0)
Este método permitirá que el script te pida permiso a través de tu navegador para acceder a tu Google Drive.

### Paso 1: Configurar la Pantalla de Consentimiento
Ve a la Consola de Google Cloud y selecciona tu proyecto.

En el menú de la izquierda (☰), ve a APIs y servicios > Pantalla de consentimiento de OAuth.

En "Tipo de usuario", selecciona Externo y haz clic en CREAR.

Rellena los campos obligatorios:

Nombre de la aplicación: Ponle un nombre, por ejemplo, "Biwenger Scraper".

Correo electrónico de asistencia al usuario: Selecciona tu dirección de email.

Información de contacto del desarrollador: Vuelve a poner tu dirección de email.

Haz clic en GUARDAR Y CONTINUAR. En la página de "Permisos", no añadas nada y haz clic en GUARDAR Y CONTINUAR.

En la página de "Usuarios de prueba", haz clic en + ADD USERS y añade tu propia dirección de Gmail. Haz clic en AÑADIR y luego en GUARDAR Y CONTINUAR.

### Paso 2: Crear las Credenciales
En el menú de la izquierda, ve a APIs y servicios > Credenciales.

Haz clic en + CREAR CREDENCIALES en la parte superior y selecciona ID de cliente de OAuth.

En "Tipo de aplicación", elige Aplicación de escritorio.

Dale un nombre (ej. "Credenciales de Escritorio") y haz clic en CREAR.

Aparecerá una ventana con tu ID y secreto de cliente. Haz clic en el botón DESCARGAR JSON.

Renombra el archivo descargado a client_secrets.json y guárdalo en la misma carpeta que tu script de Python.

### Paso 3: Configurar la Carpeta en tu Drive
Ve a tu Google Drive y crea una carpeta normal en "Mi unidad". Dale un nombre como "Biwenger CSV".

Abre la carpeta y copia el ID de la carpeta de la URL, como hiciste antes.

Pega este ID en la variable GDRIVE_FOLDER_ID de tu script de Python.

¡Y ya está! La primera vez que ejecutes el nuevo script, se abrirá una ventana en tu navegador pidiéndote que inicies sesión y aceptes los permisos. Una vez lo hagas, se creará un archivo token.json y no tendrás que volver a iniciar sesión.



# deploy

## secret manager
gcloud secrets create client_secrets_json --data-file="client_secrets.json"
gcloud secrets create token_json --data-file="token.json"
echo -n "XXXXX@gmail.com" | gcloud secrets create biwenger-email --data-file=-
echo -n "XXXXX" | gcloud secrets create biwenger-password --data-file=-

## cloud run
gcloud builds submit --tag gcr.io/biwenger-tools/scraper-job


gcloud run jobs create biwenger-scraper-data \
  --image gcr.io/biwenger-tools/scraper-job \
  --region europe-southwest1 \
  --set-secrets="/gdrive_client/client_secrets.json=client_secrets_json:latest" \
  --set-secrets="/gdrive_token/token.json=token_json:latest" \
  --set-secrets="/biwenger_email/biwenger-email=biwenger-email:latest" \
  --set-secrets="/biwenger_password/biwenger-password=biwenger-password:latest"


  gcloud run jobs execute biwenger-scraper-data --region europe-southwest1


  update

  gcloud run jobs update biwenger-scraper-data \
  --image gcr.io/biwenger-tools/scraper-job \
  --region europe-southwest1