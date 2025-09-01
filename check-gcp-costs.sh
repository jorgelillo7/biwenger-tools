#!/bin/bash

PROJECT="biwenger-tools"
FREE_STORAGE=5          # GB
FREE_ARTIFACT=0.5       # GB
FREE_CLOUDRUN_CPU=180000     # vCPU-sec
FREE_CLOUDRUN_MEM=360000     # GiB-sec

echo "=== Estimación de costes para el proyecto $PROJECT ==="
echo

# ---------------------------
# Cloud Storage
# ---------------------------
STORAGE_USED=$(gcloud storage buckets list --project $PROJECT --format="get(sizeGb)" | awk '{sum+=$1} END {print sum+0}')
echo "💾 Cloud Storage:"
echo "  Uso: ${STORAGE_USED} GB"
echo "  Free Tier: ${FREE_STORAGE} GB / mes"
echo

# ---------------------------
# Artifact Registry
# ---------------------------
ARTIFACT_USED=$(gcloud artifacts repositories list --project $PROJECT --format="get(sizeBytes)" | awk '{sum+=$1} END {printf "%.2f", sum/1024/1024/1024}')
ARTIFACT_PERCENT=$(awk "BEGIN {printf \"%.0f\", ($ARTIFACT_USED/$FREE_ARTIFACT)*100}")

echo "🖼 Artifact Registry (Docker):"
echo "  Uso: ${ARTIFACT_USED} GB (${ARTIFACT_PERCENT}%)"
echo "  Free Tier: ${FREE_ARTIFACT} GB / mes"
echo

# ---------------------------
# Cloud Run
# ---------------------------
echo "🚀 Cloud Run estimación:"
CLOUDRUN_SERVICES=$(gcloud run services list --platform managed --project $PROJECT --format="value(name,region)")

while read -r SERVICE REGION; do
    if [ -z "$SERVICE" ]; then continue; fi
    DESC=$(gcloud run services describe $SERVICE --region $REGION --project $PROJECT --format="value(spec.template.spec.containers[].resources.limits.memory, spec.template.spec.containers[].resources.limits.cpu)")

    MEM_TOTAL=$(echo $DESC | awk '{sum+=$1} END{print sum}' | sed 's/MiB//; s/Mi//')
    CPU_TOTAL=$(echo $DESC | awk '{sum+=$2} END{print sum}' | sed 's/m//')

    MEM_TOTAL=${MEM_TOTAL:-0}
    CPU_TOTAL=${CPU_TOTAL:-0}

    echo "  - $SERVICE ($REGION)"
    echo "      Memoria total usada: ${MEM_TOTAL} MiB (Free Tier: 360000 GiB-sec / mes)"
    echo "      CPU total usada: ${CPU_TOTAL} mCPU (Free Tier: 180000 vCPU-sec / mes)"
done <<< "$CLOUDRUN_SERVICES"

# ---------------------------
# Evaluación Free Tier
# ---------------------------
OVER=0
(( $(echo "$STORAGE_USED > $FREE_STORAGE" | bc -l) )) && OVER=1
(( $(echo "$ARTIFACT_USED > $FREE_ARTIFACT" | bc -l) )) && OVER=1
# Cloud Run consumo ficticio 0

if [ $OVER -eq 0 ]; then
    echo "✅ Estás dentro del Free Tier de GCP. No hay costes a pagar."
else
    echo "⚠️ Atención: algún servicio supera el Free Tier. Podrías tener costes."
fi
