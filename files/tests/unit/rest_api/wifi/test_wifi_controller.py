from unittest.mock import patch
from server.common import ErrorCode


def test_get_wifi_status(client):
    # GIVEN
    with patch(
        "server.rest_api.wifi_controller.rest_controller.wifi_bands_manager_service"
    ) as mock_service:
        mock_service.get_wifi_status.return_value = "Connected"

        # WHEN
        response = client.get("/api/wifi")

        # THEN
        assert response.status_code == 200
        assert response.json == {"status": "Connected"}
        mock_service.get_wifi_status.assert_called_once()


def test_post_wifi_status_up(client):
    # GIVEN
    with patch(
        "server.rest_api.wifi_controller.rest_controller.wifi_bands_manager_service"
    ) as mock_service:
        mock_service.set_wifi_status.return_value = "Up"

        # WHEN
        response = client.post("/api/wifi", query_string={"status": "Up"})

        # Then
        assert response.status_code == 200
        assert response.json == {"status": "Up"}
        mock_service.set_wifi_status.assert_called_once_with(new_status="Up")


def test_post_wifi_status_down(client):
    # GIVEN
    with patch(
        "server.rest_api.wifi_controller.rest_controller.wifi_bands_manager_service"
    ) as mock_service:
        mock_service.set_wifi_status.return_value = "Down"

        # WHEN
        response = client.post("/api/wifi", query_string={"status": "Down"})

        # Then
        assert response.status_code == 200
        assert response.json == {"status": "Down"}
        mock_service.set_wifi_status.assert_called_once_with(new_status="Down")


def test_post_wifi_status_wrong_args(client):
    # GIVEN
    with patch("server.rest_api.wifi_controller.rest_controller.wifi_bands_manager_service"):
        # WHEN
        response = client.post("/api/wifi", query_string={"status": "wrong"})

        # THEN
        assert response.status_code == 400
        assert response.json["status"] == ErrorCode.ERROR_IN_REQUEST_ARGS.message


def test_post_wifi_status_missing_args(client):
    # GIVEN
    with patch("server.rest_api.wifi_controller.rest_controller.wifi_bands_manager_service"):
        # WHEN
        response = client.post("/api/wifi")

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
        response = client.get("/api/wifi/bands", query_string={"band": "2.4GHz"})

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
        response = client.get("/api/wifi/bands")

        # THEN
        assert response.status_code == 400
        assert response.json["status"] == ErrorCode.ERROR_IN_REQUEST_ARGS.message


def test_post_band_status_up(client):
    # GIVEN
    with patch(
        "server.rest_api.wifi_controller.rest_controller.wifi_bands_manager_service"
    ) as mock_service:
        mock_service.set_band_status.return_value = "Up"

        # WHEN
        response = client.post("/api/wifi/bands", query_string={"band": "5GHz", "status": "Up"})

        # THEN
        assert response.status_code == 200
        assert response.json == {"status": "Up"}
        mock_service.set_band_status.assert_called_once_with(band="5GHz", new_status="Up")


def test_post_band_status_down(client):
    # GIVEN
    with patch(
        "server.rest_api.wifi_controller.rest_controller.wifi_bands_manager_service"
    ) as mock_service:
        mock_service.set_band_status.return_value = "Down"

        # WHEN
        response = client.post("/api/wifi/bands", query_string={"band": "5GHz", "status": "Down"})

        # THEN
        assert response.status_code == 200
        assert response.json == {"status": "Down"}
        mock_service.set_band_status.assert_called_once_with(band="5GHz", new_status="Down")


def test_post_band_status_wrong_args(client):
    # GIVEN
    with patch("server.rest_api.wifi_controller.rest_controller.wifi_bands_manager_service"):
        # WHEN
        response = client.post("/api/wifi/bands", query_string={"band": "wrong", "status": "wrong"})

        # THEN
        assert response.status_code == 400
        assert response.json["status"] == ErrorCode.ERROR_IN_REQUEST_ARGS.message


def test_post_band_status_missing_args(client):
    # GIVEN
    with patch("server.rest_api.wifi_controller.rest_controller.wifi_bands_manager_service"):
        # WHEN
        response = client.post("/api/wifi/bands")

        # THEN
        assert response.status_code == 400
        assert response.json["status"] == ErrorCode.ERROR_IN_REQUEST_ARGS.message
