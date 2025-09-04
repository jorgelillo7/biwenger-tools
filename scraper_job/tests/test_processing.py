import pytest
import unidecode
from datetime import datetime
from freezegun import freeze_time

# Se actualiza la importación a absoluta
from scraper_job.logic.processing import (
    categorize_title,
    process_participation,
    sort_messages,
    get_all_board_messages,
)
from core.biwenger_client import BiwengerClient

# --- Tests unitarios para las funciones de lógica ---


def test_categorize_title():
    """Prueba que el título de los mensajes se clasifica correctamente."""
    assert categorize_title("Crónica - La final") == "cronica"
    assert categorize_title("CRONICAS") == "cronica"
    assert categorize_title("Dato - Venta de jugadores") == "dato"
    assert categorize_title("DATOS - Fichaje millonario") == "dato"
    assert categorize_title("Cesión - Última hora") == "cesion"
    assert categorize_title("Comunicado - La liga comienza") == "comunicado"
    assert categorize_title("Fichajes del mes") == "comunicado"
    assert categorize_title("") == "comunicado"
    assert categorize_title("  noticia sin categoria ") == "comunicado"
    assert categorize_title("Crónica - con acento") == "cronica"


def test_process_participation():
    """Prueba que los datos de participación se procesan y formatean correctamente."""
    mock_messages = [
        {"autor": "Autor1", "categoria": "comunicado", "id_hash": "id1"},
        {"autor": "Autor2", "categoria": "dato", "id_hash": "id2"},
        {"autor": "Autor1", "categoria": "dato", "id_hash": "id3"},
        {"autor": "Autor1", "categoria": "comunicado", "id_hash": "id1"},  # Duplicado
        {"autor": "Autor3", "categoria": "cronica", "id_hash": "id4"},
    ]
    mock_user_map = {1: "Autor1", 2: "Autor2", 3: "Autor3", 4: "Autor4"}

    result = process_participation(mock_messages, mock_user_map)
    result_map = {item["autor"]: item for item in result}

    assert len(result) == 4
    assert result_map["Autor1"]["comunicados"] == "id1"
    assert result_map["Autor1"]["datos"] == "id3"
    assert result_map["Autor2"]["comunicados"] == ""
    assert result_map["Autor2"]["datos"] == "id2"
    assert result_map["Autor3"]["cronicas"] == "id4"
    assert result_map["Autor4"]["comunicados"] == ""


def test_sort_messages():
    """Prueba que los mensajes se ordenan por fecha de más reciente a más antiguo."""
    messages = [
        {"fecha": "02-01-2024 10:00:00"},
        {"fecha": "01-01-2024 12:00:00"},
        {"fecha": "03-01-2024 08:00:00"},
        {"fecha": "fecha-invalida"},
    ]
    sorted_messages = sort_messages(messages)
    assert sorted_messages[0]["fecha"] == "03-01-2024 08:00:00"
    assert sorted_messages[1]["fecha"] == "02-01-2024 10:00:00"
    assert sorted_messages[2]["fecha"] == "01-01-2024 12:00:00"
    assert sorted_messages[3]["fecha"] == "fecha-invalida"
