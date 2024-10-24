import pytest
from unittest.mock import patch
from flask import Flask
from server.rest_api.wifi_controller.rest_controller import bp as wifi_controller_bp
from server.common import ServerBoxException, handle_server_box_exception, ErrorCode


@pytest.fixture
def app_with_bp():
    """Create a Flask app for testing."""
    app = Flask(__name__)
    app.register_error_handler(ServerBoxException, handle_server_box_exception)
    app.register_blueprint(wifi_controller_bp, url_prefix="/api/wifi")

    return app


@pytest.fixture
def client(app_with_bp):
    """Create a test client."""
    return app_with_bp.test_client()


def test_get_wifi_status(client):
    # GIVEN
    with patch(
        "server.rest_api.wifi_controller.rest_controller.wifi_bands_manager_service"
    ) as mock_service:
        mock_service.get_wifi_status.return_value = "Connected"

        # WHEN
        response = client.get("/api/wifi/status")

        # THEN
        assert response.status_code == 200
        assert response.json == {"status": "Connected"}
        mock_service.get_wifi_status.assert_called_once()


def test_post_wifi_status(client):
    # GIVEN
    with patch(
        "server.rest_api.wifi_controller.rest_controller.wifi_bands_manager_service"
    ) as mock_service:
        mock_service.set_wifi_status.return_value = "Up"

        # WHEN
        response = client.post("/api/wifi/status", query_string={"status": "Up"})

        # Then
        assert response.status_code == 200
        assert response.json == {"status": "Up"}
        mock_service.set_wifi_status.assert_called_once_with(new_status="Up")


def test_post_wifi_status_missing_args(client):
    # GIVEN
    with patch("server.rest_api.wifi_controller.rest_controller.wifi_bands_manager_service"):
        # WHEN
        response = client.post("/api/wifi/status")

        # THEN
        assert response.status_code == 400
        assert response.json["status"] == ErrorCode.ERROR_IN_REQUEST_ARGS.message


def test_get_band_status(client):
    # GIVEN
    with patch(
        "server.rest_api.wifi_controller.rest_controller.wifi_bands_manager_service"
    ) as mock_service:
        mock_service.get_band_status.return_value = "Up"

        # WHEN
        response = client.get("/api/wifi/band/status", query_string={"band": "2.4GHz"})

        # THEN
        assert response.status_code == 200
        assert response.json == {"status": "Up"}
        mock_service.get_band_status.assert_called_once_with(band="2.4GHz")


def test_get_band_status_missing_args(client):
    # GIVEN
    with patch(
        "server.rest_api.wifi_controller.rest_controller.wifi_bands_manager_service"
    ) as mock_service:

        # WHEN
        response = client.get("/api/wifi/band/status")

        # THEN
        assert response.status_code == 400
        assert response.json["status"] == ErrorCode.ERROR_IN_REQUEST_ARGS.message


def test_post_band_status(client):
    # GIVEN
    with patch(
        "server.rest_api.wifi_controller.rest_controller.wifi_bands_manager_service"
    ) as mock_service:
        mock_service.set_band_status.return_value = "Up"

        # WHEN
        response = client.post(
            "/api/wifi/band/status", query_string={"band": "5GHz", "status": "Up"}
        )

        # THEN
        assert response.status_code == 200
        assert response.json == {"status": "Up"}
        mock_service.set_band_status.assert_called_once_with(band="5GHz", new_status="Up")


def test_post_band_status_missing_args(client):
    # GIVEN
    with patch("server.rest_api.wifi_controller.rest_controller.wifi_bands_manager_service"):
        # WHEN
        response = client.post("/api/wifi/band/status")

        # THEN
        assert response.status_code == 400
        assert response.json["status"] == ErrorCode.ERROR_IN_REQUEST_ARGS.message
