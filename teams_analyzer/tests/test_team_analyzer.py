import os
import pytest
from unittest.mock import patch, MagicMock, mock_open
from teams_analyzer.teams_analyzer import main
from teams_analyzer import config  # Importar el archivo config

# Asegúrate de que los datos de Analitica Fantasy y Jugadores
# estén en un formato que no cause errores.
mock_af_data = {
    "player a": {"coeficiente": 10.5, "puntuacion_esperada": 20.0},
    "player b": {"coeficiente": "N/A", "puntuacion_esperada": "N/A"},
}
mock_jp_data = {"player a": "muyRecomendable", "player b": "fondoDeArmario"}


# Mockear el módulo config para controlar las variables
@pytest.fixture(autouse=True)
def mock_config_module():
    with (
        patch("teams_analyzer.config.TELEGRAM_BOT_TOKEN", "mock_token"),
        patch("teams_analyzer.config.TELEGRAM_CHAT_ID", "mock_chat_id"),
        patch("teams_analyzer.config.FINAL_REPORT_NAME", "squads_export.csv"),
    ):
        yield


@pytest.fixture
def mock_all_dependencies():
    """
    Mocks all necessary dependencies for the main function.
    """
    with (
        patch("teams_analyzer.teams_analyzer.BiwengerClient") as mock_biwenger_client,
        patch(
            "teams_analyzer.teams_analyzer.fetch_analitica_fantasy_coeffs"
        ) as mock_fetch_af,
        patch("teams_analyzer.teams_analyzer.fetch_jp_player_tips") as mock_fetch_jp,
        patch("teams_analyzer.teams_analyzer.os.makedirs"),
        patch("teams_analyzer.teams_analyzer.os.path.join") as mock_join,
        # Mock de send_telegram_notification para evitar errores reales
        patch(
            "teams_analyzer.teams_analyzer.send_telegram_notification"
        ) as mock_telegram,
        patch("builtins.open", new_callable=mock_open) as mock_open_file,
    ):
        mock_biwenger = MagicMock()
        mock_biwenger_client.return_value = mock_biwenger

        players_data = {
            1: {
                "id": 1,
                "name": "Player A",
                "owner": {"id": 123, "clause": 5000000},
                "position": "defensa",
                "team_id": 1,
                "price": 1000000,
            },
            2: {
                "id": 2,
                "name": "Player B",
                "owner": {"id": 456, "clause": 6000000},
                "position": "delantero",
                "team_id": 2,
                "price": 1200000,
            },
        }

        mock_biwenger.get_all_players_data_map.return_value = players_data
        mock_biwenger.get_league_users.return_value = {
            123: "Manager A",
            456: "Manager B",
        }
        mock_biwenger.get_manager_squad.side_effect = [
            [players_data[1]],
            [players_data[2]],
        ]
        mock_biwenger.get_market_players.return_value = [
            {"player": {"id": 1}, "user": None, "price": 0}
        ]

        # Configuración del mock para la ruta del archivo.
        mock_join.side_effect = lambda *args: "/mocked/path/to/" + args[-1]

        # Salidas simuladas de los scrapers.
        mock_fetch_af.return_value = mock_af_data
        mock_fetch_jp.return_value = mock_jp_data

        yield {
            "mock_biwenger": mock_biwenger,
            "mock_fetch_af": mock_fetch_af,
            "mock_fetch_jp": mock_fetch_jp,
            "mock_open": mock_open_file,
            "mock_file": mock_open_file.return_value.__enter__.return_value,
            "mock_telegram": mock_telegram,
        }


def test_main_success(mock_all_dependencies):
    """
    Prueba el flujo completo cuando todo se ejecuta correctamente.
    """
    main()

    # 1. Comprobar que los scrapers se llamaron.
    mock_all_dependencies["mock_fetch_jp"].assert_called_once()
    mock_all_dependencies["mock_fetch_af"].assert_called_once()

    # 2. Comprobar que se llamaron a las funciones de Biwenger.
    mock_all_dependencies["mock_biwenger"].get_all_players_data_map.assert_called_once()
    mock_all_dependencies["mock_biwenger"].get_league_users.assert_called_once()
    mock_all_dependencies["mock_biwenger"].get_manager_squad.assert_any_call(
        "https://biwenger.as.com/api/v2/user/{manager_id}?fields=players(id,owner)", 123
    )
    mock_all_dependencies["mock_biwenger"].get_manager_squad.assert_any_call(
        "https://biwenger.as.com/api/v2/user/{manager_id}?fields=players(id,owner)", 456
    )
    mock_all_dependencies["mock_biwenger"].get_market_players.assert_called_once()

    # 3. Comprobar que el archivo CSV se creó y se escribió correctamente.
    # Usamos assert_called_with para verificar los argumentos de una de las llamadas
    # a `open`, ignorando las otras.
    mock_all_dependencies["mock_open"].assert_called_with(
        "/mocked/path/to/squads_export.csv", "w", newline="", encoding="utf-8"
    )

    # 4. Comprobar que la notificación de Telegram se llamó correctamente.
    mock_all_dependencies["mock_telegram"].assert_called_once_with(
        config.TELEGRAM_API_URL,
        "mock_token",
        "mock_chat_id",
        "📊 ¡Análisis de equipos completado! (3 jugadores)",
        "/mocked/path/to/squads_export.csv",
    )
