from unittest.mock import patch
from server.common import ErrorCode


def test_get_relays_status(client, relays_status_off):
    # GIVEN
    with patch(
        "server.rest_api.electrical_panel_controller.rest_controller.electrical_panel_manager_service"
    ) as mock_service:
        mock_service.get_relays_last_received_status.return_value = relays_status_off

        # WHEN
        response = client.get("api/electrical_panel")

        # THEN
        assert response.status_code == 200
        assert response.json["relay_statuses"] == relays_status_off.to_json()["relay_statuses"]
        mock_service.get_relays_last_received_status.assert_called_once()


def test_post_relays_status(client):
    # GIVEN
    with patch(
        "server.rest_api.electrical_panel_controller.rest_controller.electrical_panel_manager_service"
    ) as mock_service:
        mock_service.publish_mqtt_relays_status_command.return_value = None

        # WHEN
        response = client.post(
            "api/electrical_panel",
            query_string={"relay_0": "true", "relay_1": "false", "relay_2": "yes"},
        )

        # THEN
        assert response.status_code == 200
        assert response.json["relay_statuses"][0]["status"] == True
        assert response.json["relay_statuses"][1]["status"] == False
        assert response.json["relay_statuses"][2]["status"] == True
        mock_service.publish_mqtt_relays_status_command.assert_called_once()


def test_post_relays_status_missing_args(client):
    # GIVEN
    with patch(
        "server.rest_api.electrical_panel_controller.rest_controller.electrical_panel_manager_service"
    ):
        # WHEN
        response = client.post("api/electrical_panel")

        # THEN
        assert response.status_code == 400
        assert response.json["status"] == ErrorCode.ERROR_IN_REQUEST_ARGS.message


def test_post_relays_status_exception(client):
    # GIVEN
    with patch(
        "server.rest_api.electrical_panel_controller.rest_controller.electrical_panel_manager_service"
    ):
        # WHEN
        response = client.post("api/electrical_panel", query_string={"relay_0": "invalid_value"})

        # THEN
        assert response.status_code == 400
        assert response.json["status"] == ErrorCode.ERROR_IN_REQUEST_ARGS.message


def test_get_single_relay_status(client, relays_status_off):
    # GIVEN
    with patch(
        "server.rest_api.electrical_panel_controller.rest_controller.electrical_panel_manager_service"
    ) as mock_service:
        mock_service.get_single_relay_last_received_status.return_value = (
            relays_status_off.relay_statuses[1]
        )

        # WHEN
        response = client.get("api/electrical_panel/relay", query_string={"relay": "1"})

        # THEN
        assert response.status_code == 200
        assert response.json == {"relay_number": 1, "status": False, "powered": False}
        mock_service.get_single_relay_last_received_status.assert_called_once_with(1)


def test_get_single_relay_status_missing_relay(client):
    # GIVEN
    with patch(
        "server.rest_api.electrical_panel_controller.rest_controller.electrical_panel_manager_service"
    ):
        # WHEN
        response = client.get("api/electrical_panel/relay")

        # THEN
        assert response.status_code == 400
        assert response.json["status"] == ErrorCode.ERROR_IN_REQUEST_ARGS.message


def test_get_single_relay_status_invalid_relay(client):
    # GIVEN
    with patch(
        "server.rest_api.electrical_panel_controller.rest_controller.electrical_panel_manager_service"
    ):
        # WHEN
        response = client.get("api/electrical_panel/relay", query_string={"relay": "invalid"})

        # THEN
        assert response.status_code == 400
        assert response.json["status"] == ErrorCode.ERROR_IN_REQUEST_ARGS.message
