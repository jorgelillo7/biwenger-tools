import pytest
import os
from datetime import datetime, timedelta
from dateutil import parser
import pytz
from unittest.mock import patch, MagicMock

# Importamos las funciones a testear.
# Asume que utils.py está en la carpeta 'core'.
from core import utils

# --- Tests para read_secret_from_file ---


def test_read_secret_from_file_exists(mock_filesystem):
    """Verifica que lee el contenido de un archivo existente."""
    secret_content = "my_secret_password"
    secret_path = mock_filesystem("test_secret.txt", secret_content)

    result = utils.read_secret_from_file(secret_path)
    assert result == secret_content


def test_read_secret_from_file_not_exists():
    """Verifica que devuelve el valor por defecto si el archivo no existe."""
    fallback_value = "default_value"
    non_existent_path = "/path/to/non_existent_file.txt"

    result = utils.read_secret_from_file(non_existent_path, fallback_value)
    assert result == fallback_value


def test_read_secret_from_file_empty_path():
    """Verifica que devuelve el valor por defecto si la ruta está vacía."""
    fallback_value = "default_value"
    result = utils.read_secret_from_file("", fallback_value)
    assert result == fallback_value


# --- Tests para get_file_metadata ---


def test_get_file_metadata_found(mock_google_drive_service):
    """Verifica que el archivo encontrado es procesado correctamente."""
    # Mockear la fecha y hora actual para controlarla en el test
    with patch("core.utils.datetime") as mock_dt:
        now_madrid = parser.parse("2025-09-04T12:00:00Z").astimezone(
            pytz.timezone("Europe/Madrid")
        )
        mock_dt.now.return_value = now_madrid

        # Configurar la respuesta del servicio de Drive mockeado
        mock_response = {
            "files": [
                {
                    "id": "file1",
                    "name": "file1.txt",
                    "modifiedTime": "2025-09-04T10:00:00Z",
                }
            ]
        }
        mock_google_drive_service.files().list().execute.return_value = mock_response

        filenames = ["file1.txt"]
        dynamic_files = []

        result = utils.get_file_metadata(
            mock_google_drive_service, "folder_id", filenames, dynamic_files
        )

        assert len(result) == 1
        assert result[0]["name"] == "file1.txt"
        assert result[0]["status"] == "Encontrado"
        assert result[0]["is_stale"] is False


def test_get_file_metadata_stale(mock_google_drive_service):
    """Verifica que el archivo se marca como 'desactualizado' si es dinámico y viejo."""
    # Mockear la fecha y hora actual para controlarla en el test
    with patch("core.utils.datetime") as mock_dt:
        now_madrid = parser.parse("2025-09-04T12:00:00Z").astimezone(
            pytz.timezone("Europe/Madrid")
        )
        mock_dt.now.return_value = now_madrid

        # Configurar la respuesta del servicio de Drive mockeado (archivo de hace 8 días)
        mock_response = {
            "files": [
                {
                    "id": "file1",
                    "name": "file1.txt",
                    "modifiedTime": "2025-08-27T10:00:00Z",
                }
            ]
        }
        mock_google_drive_service.files().list().execute.return_value = mock_response

        filenames = ["file1.txt"]
        dynamic_files = ["file1.txt"]

        result = utils.get_file_metadata(
            mock_google_drive_service, "folder_id", filenames, dynamic_files
        )

        assert len(result) == 1
        assert result[0]["name"] == "file1.txt"
        assert result[0]["status"] == "Encontrado"
        assert result[0]["is_stale"] is True


def test_get_file_metadata_not_found(mock_google_drive_service):
    """Verifica que maneja correctamente los archivos no encontrados."""
    # Mockear la fecha y hora actual
    with patch("core.utils.datetime") as mock_dt:
        now_madrid = parser.parse("2025-09-04T12:00:00Z").astimezone(
            pytz.timezone("Europe/Madrid")
        )
        mock_dt.now.return_value = now_madrid

        # El mock de Drive devolverá una lista de archivos vacía por defecto
        mock_google_drive_service.files().list().execute.return_value = {"files": []}

        filenames = ["missing_file.txt"]
        dynamic_files = []

        result = utils.get_file_metadata(
            mock_google_drive_service, "folder_id", filenames, dynamic_files
        )

        assert len(result) == 1
        assert result[0]["name"] == "missing_file.txt"
        assert result[0]["status"] == "No Encontrado"
        assert result[0]["is_stale"] is False
