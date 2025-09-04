import pytest
import requests_mock
from unittest.mock import patch, mock_open
import os
import requests
from core.telegram_notifier import send_telegram_notification

# Datos de prueba
TEST_API_URL = "https://api.telegram.org/bot{token}/sendDocument"
TEST_BOT_TOKEN = "test_bot_token"
TEST_CHAT_ID = "123456789"
TEST_CAPTION = "Test notification"
TEST_FILEPATH = "/path/to/test_file.txt"


def test_send_telegram_notification_success(capsys):
    """Verifica que la notificación se envía correctamente y se imprime el mensaje de éxito."""
    with requests_mock.Mocker() as m:
        m.post(
            TEST_API_URL.format(token=TEST_BOT_TOKEN),
            json={"ok": True},
            status_code=200,
        )

        with patch("builtins.open", mock_open(read_data=b"file content")):
            with patch("os.path.basename", return_value="test_file.txt"):
                send_telegram_notification(
                    TEST_API_URL,
                    TEST_BOT_TOKEN,
                    TEST_CHAT_ID,
                    TEST_CAPTION,
                    TEST_FILEPATH,
                )

        # Capturamos la salida estándar y verificamos los mensajes
        captured = capsys.readouterr()
        assert "✅ Notificación enviada a Telegram con éxito." in captured.out

        assert m.called_once
        assert m.last_request.url == TEST_API_URL.format(token=TEST_BOT_TOKEN)
        assert "chat_id" in m.last_request.text


def test_send_telegram_notification_failure_api(capsys):
    """Verifica que se maneja un error de la API y se imprime el mensaje de error."""
    with requests_mock.Mocker() as m:
        m.post(TEST_API_URL.format(token=TEST_BOT_TOKEN), status_code=404)

        with patch("builtins.open", mock_open(read_data=b"file content")):
            with patch("os.path.basename", return_value="test_file.txt"):
                send_telegram_notification(
                    TEST_API_URL,
                    TEST_BOT_TOKEN,
                    TEST_CHAT_ID,
                    TEST_CAPTION,
                    TEST_FILEPATH,
                )

    captured = capsys.readouterr()
    assert "❌ Error al enviar la notificación a Telegram:" in captured.out


def test_send_telegram_notification_failure_file(capsys):
    """Verifica que se maneja un error si el archivo no existe y se imprime el mensaje de error."""
    with requests_mock.Mocker() as m:
        send_telegram_notification(
            TEST_API_URL,
            TEST_BOT_TOKEN,
            TEST_CHAT_ID,
            TEST_CAPTION,
            "/non/existent/file.txt",
        )

    captured = capsys.readouterr()
    assert "❌ Error al enviar la notificación a Telegram:" in captured.out
    assert "No such file or directory: '/non/existent/file.txt'" in captured.out
