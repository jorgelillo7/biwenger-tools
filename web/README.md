# config local

pip3 install Flask --break-system-packages

COMUNICADOS_CSV_URL="https://drive.google.com/uc?export=download&id=1t-yv13NPpuuhrbUUIJwoNYI0FSrsYS_q" \
PALMARES_CSV_URL="https://drive.google.com/uc?export=download&id=1cbXiUUo1RTG-6tlI0kK6tEx-DezfBAty" \
python3 app.py

http://127.0.0.1:8080


# deploy

gcloud auth login
gcloud config set project biwenger-tools

gcloud builds submit --tag gcr.io/biwenger-tools/web

gcloud run deploy biwenger-summary \
  --image gcr.io/biwenger-tools/web \
  --platform managed \
  --region europe-southwest1 \
  --allow-unauthenticated \
  --set-env-vars="COMUNICADOS_CSV_URL=https://drive.google.com/uc?export=download&id=1t-yv13NPpuuhrbUUIJwoNYI0FSrsYS_q,PALMARES_CSV_URL=https://drive.google.com/uc?export=download&id=1cbXiUUo1RTG-6tlI0kK6tEx-DezfBAty"