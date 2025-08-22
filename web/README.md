## 🏠 Entorno Local (Scraper)
### 1. Instalación de Dependencias
```bash
# Crea un entorno virtual (solo la primera vez)
python3 -m venv venv

# Activa el entorno (en macOS/Linux)
source venv/bin/activate

# En Windows usa: venv\Scripts\activate
```

```bash
pip3 install -r requirements.txt
```

### 2. Ejecución (desde raiz)
```bash
python3 -m web.app
```

### 3. Accedemos a la web
http://127.0.0.1:8080


## 🚀 Despliegue en Google Cloud
### 1. Configuración del proyecto
```bash
gcloud auth login
gcloud config set project biwenger-tools
```

### 2. Construye la imagen Docker
gcloud builds submit --tag gcr.io/biwenger-tools/web

### 3. Deploy en script que usa .env
```bash
./deploy.sh
```

### 4. Accedemos a la web
https://biwenger-summary-pjpqofuevq-no.a.run.app/