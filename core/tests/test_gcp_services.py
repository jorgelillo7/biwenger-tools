import pytest
from unittest.mock import patch, MagicMock, mock_open
import io
import csv
from core.sdk import gcp

# --- Tests para la autenticación y el servicio ---


@patch("core.sdk.gcp.service_account")
@patch("core.sdk.gcp.build")
def test_get_google_service(mock_build, mock_service_account):
    """Verifica que el servicio se construye con las credenciales correctas."""
    mock_credentials = MagicMock()
    mock_service_account.Credentials.from_service_account_file.return_value = (
        mock_credentials
    )
    api_name = "test_api"
    api_version = "v1"
    service_account_file = "service_account.json"
    scopes = ["scope1"]
    service = gcp.get_google_service(
        api_name, api_version, service_account_file, scopes
    )
    mock_service_account.Credentials.from_service_account_file.assert_called_once_with(
        service_account_file, scopes=scopes
    )
    mock_build.assert_called_once_with(
        api_name, api_version, credentials=mock_credentials
    )
    assert service == mock_build.return_value


# --- Tests para las operaciones con Google Drive ---


def test_find_file_on_drive_found(mock_google_service):
    """Verifica que devuelve el archivo cuando se encuentra."""
    mock_response = {"files": [{"id": "file1", "name": "file1.txt"}]}
    mock_google_service.files().list().execute.return_value = mock_response
    result = gcp.find_file_on_drive(mock_google_service, "file1.txt", "folder123")
    assert result == mock_response["files"][0]


def test_find_file_on_drive_not_found(mock_google_service):
    """Verifica que devuelve None cuando no se encuentra el archivo."""
    mock_response = {"files": []}
    mock_google_service.files().list().execute.return_value = mock_response
    result = gcp.find_file_on_drive(
        mock_google_service, "non_existent.txt", "folder123"
    )
    assert result is None


@patch("core.sdk.gcp.MediaIoBaseDownload")
@patch("core.sdk.gcp.io.BytesIO")
def test_download_csv_from_drive(mock_bytesio, mock_download, mock_google_service):
    """Verifica que el archivo se descarga y decodifica correctamente."""
    mock_file_id = "test_file_id"
    mock_content = b"header1,header2\nvalue1,value2"
    mock_bytesio_instance = MagicMock()
    mock_bytesio_instance.getvalue.return_value = mock_content
    mock_bytesio.return_value = mock_bytesio_instance
    mock_downloader = MagicMock()
    mock_downloader.next_chunk.side_effect = [(None, False), (None, True)]
    mock_download.return_value = mock_downloader
    result = gcp.download_csv_from_drive(mock_google_service, mock_file_id)
    assert result == mock_content.decode("utf-8")


@patch("core.sdk.gcp.download_csv_from_drive")
def test_download_csv_as_dict_success(mock_download_csv):
    """Verifica la descarga y conversión exitosa a lista de diccionarios."""
    csv_string = "col1,col2\nval1,val2\nval3,val4"
    mock_download_csv.return_value = csv_string
    result = gcp.download_csv_as_dict(None, "file_id")
    assert len(result) == 2
    assert result[0] == {"col1": "val1", "col2": "val2"}


def test_download_csv_as_dict_no_file_id():
    """Verifica que se levanta un error si no hay ID de archivo."""
    with pytest.raises(FileNotFoundError):
        gcp.download_csv_as_dict(None, None)


@patch("core.sdk.gcp.MediaIoBaseUpload")
def test_upload_csv_to_drive_update(mock_upload, mock_google_service, capsys):
    """Verifica que se llama a 'update' si el archivo ya existe."""
    existing_file_id = "existing_id"
    # Mock para el flujo .files().update().execute()
    mock_google_service.files.return_value.update.return_value.execute.return_value = {}
    gcp.upload_csv_to_drive(
        mock_google_service, "folder_id", "test.csv", "a,b\n1,2", existing_file_id
    )
    captured = capsys.readouterr()
    assert "✅ Archivo 'test.csv' actualizado en Drive." in captured.out
    # Verificamos que update fue llamado una sola vez
    mock_google_service.files.return_value.update.assert_called_once()
    mock_google_service.files.return_value.create.assert_not_called()


@patch("core.sdk.gcp.MediaIoBaseUpload")
def test_upload_csv_to_drive_create_new(mock_upload, mock_google_service, capsys):
    """Verifica que se llama a 'create' si es un archivo nuevo y se añaden permisos."""
    # Mock para el flujo .files().create().execute()
    mock_google_service.files.return_value.create.return_value.execute.return_value = {
        "id": "new_id"
    }
    # Mock para el flujo .permissions().create().execute()
    mock_google_service.permissions.return_value.create.return_value.execute.return_value = (
        {}
    )
    gcp.upload_csv_to_drive(
        mock_google_service, "folder_id", "new.csv", "a,b\n1,2", None
    )
    captured = capsys.readouterr()
    assert (
        "✅ Archivo 'new.csv' creado y compartido públicamente en Drive."
        in captured.out
    )
    # Verificamos que create fue llamado una sola vez
    mock_google_service.files.return_value.create.assert_called_once()
    mock_google_service.files.return_value.update.assert_not_called()
    mock_google_service.permissions.return_value.create.assert_called_once()


# --- Tests para las operaciones con Google Sheets ---


def test_get_sheets_data_success(mock_sheets_service):
    """Verifica que se leen los datos de múltiples hojas correctamente."""
    # Simula la respuesta de .spreadsheets().get().execute()
    mock_sheets_service.spreadsheets.return_value.get.return_value.execute.return_value = {
        "sheets": [
            {"properties": {"title": "Hoja1"}},
            {"properties": {"title": "Hoja2"}},
        ]
    }
    # Simula las respuestas de .spreadsheets().values().get().execute() para cada hoja
    mock_get_values_execute = MagicMock()
    mock_get_values_execute.side_effect = [
        {
            "values": [
                ["Nombre de la Liga:", "Liga Test 1"],
                ["Descripción:", "Desc. 1"],
                ["Premio:", "100€"],
                ["", ""],
                ["Col1", "Col2"],
                ["val1", "val2"],
            ]
        },
        {
            "values": [
                ["Nombre de la Liga:", "Liga Test 2"],
                ["Descripción:", "Desc. 2"],
                ["Premio:", "200€"],
                ["", ""],
                ["ColA", "ColB"],
                ["valA", "valB"],
            ]
        },
    ]
    mock_sheets_service.spreadsheets.return_value.values.return_value.get.return_value.execute = (
        mock_get_values_execute
    )

    result = gcp.get_sheets_data(mock_sheets_service, "spreadsheet_id")

    assert len(result) == 2
    assert result[0]["nombre"] == "Liga Test 1"
    assert result[1]["headers"] == ["ColA", "ColB"]


def test_get_sheets_data_no_data(mock_sheets_service):
    """Verifica que se manejan correctamente las hojas sin datos."""
    # Simula la respuesta de .spreadsheets().get().execute()
    mock_sheets_service.spreadsheets.return_value.get.return_value.execute.return_value = {
        "sheets": [{"properties": {"title": "HojaVacia"}}]
    }
    # Simula la respuesta de .spreadsheets().values().get().execute() con datos vacíos
    mock_get_values_execute = MagicMock()
    mock_get_values_execute.return_value = {"values": []}
    mock_sheets_service.spreadsheets.return_value.values.return_value.get.return_value.execute = (
        mock_get_values_execute
    )

    result = gcp.get_sheets_data(mock_sheets_service, "spreadsheet_id")

    assert result == []
