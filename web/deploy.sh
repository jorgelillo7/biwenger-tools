#!/bin/bash

# Carga las variables desde el archivo .env a la sesión actual de la terminal
source .env

# Ahora, ejecuta el comando de despliegue usando las variables cargadas
# La terminal reemplazará $COMUNICADOS_CSV_URL (y las demás) por su valor real
gcloud run deploy biwenger-summary \
  --image gcr.io/biwenger-tools/web \
  --platform managed \
  --region europe-southwest1 \
  --allow-unauthenticated \
  --set-env-vars="COMUNICADOS_CSV_URL=$COMUNICADOS_CSV_URL,PALMARES_CSV_URL=$PALMARES_CSV_URL,PARTICIPACION_CSV_URL=$PARTICIPACION_CSV_URL,LIGAS_ESPECIALES_SHEET_ID=$LIGAS_ESPECIALES_SHEET_ID"