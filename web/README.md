# config local

pip3 install Flask --break-system-packages

python3 app.py

http://127.0.0.1:8080


# deploy

gcloud auth login
gcloud config set project biwenger-tools

gcloud builds submit --tag gcr.io/biwenger-tools/web

./deploy.sh (lee del .env)


url:
  https://biwenger-summary-pjpqofuevq-no.a.run.app/