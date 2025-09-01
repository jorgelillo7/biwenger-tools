#!/bin/bash

# Carga todas las variables desde el archivo .env a la sesión actual de la terminal
source .env

# Ahora, ejecuta el comando de despliegue usando todas las variables cargadas
# La terminal reemplazará cada variable ($COMUNICADOS_CSV_URL, etc.) por su valor real del .env
gcloud run deploy biwenger-summary \
  --image europe-southwest1-docker.pkg.dev/biwenger-tools/biwenger-docker/web \
  --platform managed \
  --region europe-southwest1 \
  --allow-unauthenticated \
  --update-secrets=/gdrive_sa/biwenger-tools-sa.json=biwenger_tools_sa:latest \
  --set-env-vars="COMUNICADOS_CSV_URL=$COMUNICADOS_CSV_URL,PALMARES_CSV_URL=$PALMARES_CSV_URL,PARTICIPACION_CSV_URL=$PARTICIPACION_CSV_URL,LIGAS_ESPECIALES_SHEET_ID_25_26=$LIGAS_ESPECIALES_SHEET_ID_25_26,GDRIVE_FOLDER_ID=$GDRIVE_FOLDER_ID,GCP_PROJECT_ID=$GCP_PROJECT_ID,CLOUD_RUN_JOB_NAME=$CLOUD_RUN_JOB_NAME,CLOUD_RUN_REGION=$CLOUD_RUN_REGION,SECRET_KEY=$SECRET_KEY,ADMIN_PASSWORD=$ADMIN_PASSWORD"
