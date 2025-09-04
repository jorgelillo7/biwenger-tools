import pytest
from teams_analyzer.logic.player_matching import (
    normalize_name,
    find_player_match,
    map_position,
)


@pytest.fixture
def analitica_map():
    """Fixture para simular el mapa de jugadores de Analítica Fantasy."""
    return {
        "oihan sancet": {"coeficiente": "8.5", "puntuacion_esperada": "150"},
        "javier hernandez": {"coeficiente": "7.2", "puntuacion_esperada": "120"},
        "vlachodimos": {"coeficiente": "6.8", "puntuacion_esperada": "110"},
        "rahim": {"coeficiente": "6.0", "puntuacion_esperada": "90"},
        "javi rueda": {"coeficiente": "5.5", "puntuacion_esperada": "80"},
        "brugui": {"coeficiente": "7.1", "puntuacion_esperada": "125"},
        "r. rodriguez": {"coeficiente": "6.5", "puntuacion_esperada": "100"},
        "m. moreno": {"coeficiente": "6.2", "puntuacion_esperada": "95"},
        "espino": {"coeficiente": "7.8", "puntuacion_esperada": "135"},
        "giuliano": {"coeficiente": "7.0", "puntuacion_esperada": "115"},
        "c. vicente": {"coeficiente": "7.5", "puntuacion_esperada": "130"},
        "cristian": {"coeficiente": "5.0", "puntuacion_esperada": "70"},
        "jose luis morales": {"coeficiente": "8.0", "puntuacion_esperada": "140"},
    }


def test_normalize_name():
    """Prueba que la función normaliza nombres correctamente."""
    assert normalize_name("Oihan Sancet") == "oihan sancet"
    assert normalize_name("Javier HernáNDez ") == "javier hernandez"
    assert normalize_name("odysséas") == "odysseas"


def test_find_player_match_direct(analitica_map):
    """Prueba la coincidencia por nombre normalizado (Estrategia 1)."""
    result = find_player_match("Oihan Sancet", analitica_map)
    assert result["coeficiente"] == "8.5"


def test_find_player_match_manual_mapping(analitica_map):
    """Prueba la coincidencia por mapeo manual (Estrategia 2)."""
    result = find_player_match("Odysseas", analitica_map)
    assert result["coeficiente"] == "6.8"
    result = find_player_match("Alhassane", analitica_map)
    assert result["coeficiente"] == "6.0"


def test_find_player_match_last_name(analitica_map):
    """Prueba la coincidencia solo con el apellido (Estrategia 3)."""
    result = find_player_match("Pacha Espino", analitica_map)
    assert result["coeficiente"] == "7.8"


def test_find_player_match_first_name(analitica_map):
    """Prueba la coincidencia solo con el nombre (Estrategia 3)."""
    result = find_player_match("Giuliano Simeone", analitica_map)
    assert result["coeficiente"] == "7.0"


def test_find_player_match_initial_last_name(analitica_map):
    """Prueba la coincidencia con la inicial del nombre y el apellido (Estrategia 3)."""
    result = find_player_match("Carlos Vicente", analitica_map)
    assert result["coeficiente"] == "7.5"


def test_find_player_match_fallback_subset(analitica_map):
    """Prueba la coincidencia por subconjunto (Estrategia 4)."""
    result = find_player_match("Morales", analitica_map)
    assert result["puntuacion_esperada"] == "140"
    result = find_player_match("Cristian", analitica_map)
    assert result["puntuacion_esperada"] == "70"


def test_find_player_match_no_match(analitica_map):
    """Prueba el caso en que no se encuentra ninguna coincidencia."""
    result = find_player_match("Jugador Ficticio", analitica_map)
    assert result["coeficiente"] == "N/A"
    assert result["puntuacion_esperada"] == "N/A"


def test_map_position():
    """Prueba que el mapeo de posiciones funciona correctamente."""
    assert map_position(1) == "Portero"
    assert map_position(2) == "Defensa"
    assert map_position(3) == "Centrocampista"
    assert map_position(4) == "Delantero"
    assert map_position(99) == "N/A"
