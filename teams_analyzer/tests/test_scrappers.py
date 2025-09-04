import os
import shutil
import tempfile
from unittest.mock import MagicMock, patch, Mock
import pytest
from teams_analyzer.logic.scrapers import (
    create_chrome_driver,
    fetch_analitica_fantasy_coeffs,
)
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException


# Mockea la variable de entorno para las pruebas.
@pytest.fixture(autouse=True)
def mock_running_in_docker():
    """Mockea la variable RUNNING_IN_DOCKER para los tests."""
    with patch("teams_analyzer.logic.scrapers.RUNNING_IN_DOCKER", False):
        yield


@pytest.fixture
def mock_selenium_driver():
    """
    Fixture para mockear el driver de Selenium de forma segura.
    Esto evita que el test inicie un navegador real.
    """
    mock_driver = MagicMock()
    with patch(
        "teams_analyzer.logic.scrapers.create_chrome_driver", return_value=mock_driver
    ):
        yield mock_driver


@patch("teams_analyzer.logic.scrapers.tempfile.mkdtemp")
@patch("teams_analyzer.logic.scrapers.os.path.exists", return_value=False)
@patch("teams_analyzer.logic.scrapers.ChromeDriverManager")
@patch("teams_analyzer.logic.scrapers.shutil.rmtree")
def test_create_chrome_driver_local(
    mock_rmtree, mock_chrome_driver_manager, mock_exists, mock_mkdtemp
):
    """
    Prueba que el driver se inicializa correctamente en un entorno local.
    """
    mock_mkdtemp.return_value = "/mock/temp/dir"
    mock_driver = MagicMock()
    mock_chrome_driver_manager.return_value.install.return_value = (
        "/mock/path/to/driver"
    )

    with patch(
        "teams_analyzer.logic.scrapers.webdriver.Chrome", return_value=mock_driver
    ):
        with patch("teams_analyzer.logic.scrapers.RUNNING_IN_DOCKER", False):
            driver = create_chrome_driver()
            assert driver == mock_driver
            mock_chrome_driver_manager.return_value.install.assert_called_once()
            mock_rmtree.assert_not_called()


@patch("teams_analyzer.logic.scrapers.tempfile.mkdtemp")
@patch("teams_analyzer.logic.scrapers.os.path.exists", return_value=True)
@patch("teams_analyzer.logic.scrapers.webdriver.Chrome")
@patch("teams_analyzer.logic.scrapers.shutil.rmtree")
def test_create_chrome_driver_docker(
    mock_rmtree, mock_chrome, mock_exists, mock_mkdtemp
):
    """
    Prueba que el driver se inicializa correctamente en un entorno Docker,
    verificando que se llama a webdriver.Chrome con los paths correctos.
    """
    mock_mkdtemp.return_value = "/mock/temp/dir"
    mock_driver = MagicMock()
    mock_chrome.return_value = mock_driver

    with patch("teams_analyzer.logic.scrapers.RUNNING_IN_DOCKER", True):
        driver = create_chrome_driver()
        assert driver == mock_driver
        mock_chrome.assert_called_once()
        mock_rmtree.assert_called_once_with(mock_mkdtemp.return_value)


@patch("teams_analyzer.logic.scrapers.WebDriverWait")
@patch("teams_analyzer.logic.scrapers.By")
@patch("teams_analyzer.logic.scrapers.create_chrome_driver")
@patch("teams_analyzer.logic.scrapers.os.path.abspath")
@patch("teams_analyzer.logic.scrapers.os.path.dirname")
@patch("teams_analyzer.logic.scrapers.os.path.join")
@patch("teams_analyzer.logic.scrapers.csv.writer")
@patch("builtins.open")
def test_fetch_analitica_fantasy_coeffs_success_with_pagination(
    mock_open,
    mock_csv_writer,
    mock_join,
    mock_dirname,
    mock_abspath,
    mock_create_chrome_driver,
    mock_by,
    mock_webdriverwait,
):
    """
    Prueba que la función descarga y parsea los coeficientes de Analítica Fantasy
    simulando la paginación y el final del scraping.
    """
    # Configurar mocks para simular una página con datos
    mock_driver = MagicMock()
    mock_create_chrome_driver.return_value = mock_driver
    mock_wait = MagicMock()
    mock_webdriverwait.return_value = mock_wait

    # Mock de los elementos de la página
    mock_cookie_button = MagicMock()
    mock_table_presence = MagicMock()
    mock_pagination_container = MagicMock()
    mock_page_size_dropdown = MagicMock()
    mock_option_50 = MagicMock()
    mock_next_button = MagicMock(is_enabled=MagicMock(return_value=True))

    # Definir el comportamiento de `wait.until`
    mock_wait.until.side_effect = [
        mock_cookie_button,  # Botón de cookies
        mock_table_presence,  # Presencia de la tabla
        mock_pagination_container,  # Contenedor de paginación
        mock_page_size_dropdown,  # Dropdown de elementos por página
        mock_option_50,  # Opción de 50 jugadores
        mock_table_presence,  # Tabla después del cambio de vista
    ]

    # Simular las filas con datos y estructura correctas
    def create_mock_row(player_name, coefficient, expected_score):
        mock_row = MagicMock()

        # Mockear el elemento que contiene el nombre del jugador
        mock_player_name_element = MagicMock(text=player_name)

        # Mockear el elemento que contiene el coeficiente
        mock_coefficient_element = MagicMock(text=str(coefficient).replace(".", ","))

        # Mockear el elemento que contiene la puntuación esperada
        mock_expected_score_element = MagicMock(text=str(expected_score))

        mock_cells = [
            MagicMock(),  # celda 0
            MagicMock(
                find_element=MagicMock(return_value=mock_player_name_element)
            ),  # celda 1
            MagicMock(
                find_element=MagicMock(return_value=mock_coefficient_element)
            ),  # celda 2
            MagicMock(),  # celda 3
            MagicMock(),  # celda 4
            MagicMock(),  # celda 5
            mock_expected_score_element,  # celda 6, el código accede directamente a .text
            MagicMock(),  # celda 7
            MagicMock(),  # celda 8
            MagicMock(),  # celda 9
        ]

        # El código base accede a cells[6].text directamente, sin un find_element.
        # Así que el mock para la celda 6 debe ser el objeto que tiene el atributo .text
        mock_cells[6].text = str(expected_score)

        mock_row.find_elements.return_value = mock_cells
        return mock_row

    # Primera página
    mock_row_1 = create_mock_row("Test Player 1", "10,5", "20.0")
    # Segunda página
    mock_row_2 = create_mock_row("Test Player 2", "8,2", "15.0")

    # Mockear `find_elements` para que simule la paginación.
    mock_driver.find_elements.side_effect = [
        [mock_row_1],
        [mock_row_2],
        [],
    ]

    # Mockear el botón "Siguiente" para simular su estado
    next_button_mock = Mock()
    next_button_mock.is_enabled.side_effect = [True, False]
    mock_driver.find_element.side_effect = [
        mock_pagination_container,
        next_button_mock,
        NoSuchElementException,
    ]

    # Mockear las funciones de path para guardar el CSV
    mock_abspath.return_value = "/mock/path/teams_analyzer/logic/scrapers.py"
    mock_dirname.return_value = "/mock/path/teams_analyzer/logic"
    mock_join.return_value = "/mock/path/teams_analyzer/squads_export.csv"

    # Actuar
    coeffs_map = fetch_analitica_fantasy_coeffs()

    # Comprobar el resultado
    assert len(coeffs_map) == 2
    assert "test player 1" in coeffs_map
    assert "test player 2" in coeffs_map
    assert coeffs_map["test player 1"]["coeficiente"] == "10,5"
    assert coeffs_map["test player 2"]["coeficiente"] == "8,2"
    assert coeffs_map["test player 1"]["puntuacion_esperada"] == "20.0"
    assert coeffs_map["test player 2"]["puntuacion_esperada"] == "15.0"
    mock_create_chrome_driver.assert_called_once()
    mock_driver.quit.assert_called_once()

    # Comprobar que el archivo se ha escrito
    mock_open.assert_called_with(
        mock_join.return_value, "w", newline="", encoding="utf-8"
    )
    mock_csv_writer.return_value.writerow.assert_any_call(
        ["nombre_normalizado", "coeficiente", "puntuacion_esperada"]
    )
    mock_csv_writer.return_value.writerow.assert_any_call(
        ["test player 1", "10,5", "20.0"]
    )
    mock_csv_writer.return_value.writerow.assert_any_call(
        ["test player 2", "8,2", "15.0"]
    )
