#!/bin/bash

# Mantener solo la última imagen de cada nombre
REPO="europe-southwest1-docker.pkg.dev/biwenger-tools/biwenger-docker"

for IMAGE in web scraper_job; do
    echo "Limpiando imágenes de $IMAGE..."
    DIGESTS=$(gcloud artifacts docker images list $REPO/$IMAGE --sort-by=~CREATE_TIME --format="get(DIGEST)")
    FIRST=1
    for D in $DIGESTS; do
        if [ $FIRST -eq 1 ]; then
            FIRST=0
            continue
        fi
        echo "Borrando $D..."
        gcloud artifacts docker images delete $REPO/$IMAGE@$D --quiet
    done
done
