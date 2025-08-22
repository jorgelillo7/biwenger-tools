import requests
import os

def send_telegram_notification(api_url_template, bot_token, chat_id, caption, filepath):
    """
    Envía un archivo a un chat de Telegram.
    La URL de la API se pasa como parámetro para desacoplar de la configuración.
    """
    print("\n▶️  Enviando notificación a Telegram...")
    url = api_url_template.format(token=bot_token)
    try:
        with open(filepath, 'rb') as f:
            files = {'document': (os.path.basename(filepath), f)}
            data = {'chat_id': chat_id, 'caption': caption}
            response = requests.post(url, data=data, files=files)
            response.raise_for_status()
        print("✅ Notificación enviada a Telegram con éxito.")
    except Exception as e:
        print(f"❌ Error al enviar la notificación a Telegram: {e}")
