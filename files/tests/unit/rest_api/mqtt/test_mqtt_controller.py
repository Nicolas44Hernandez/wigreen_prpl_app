from unittest.mock import patch


def test_get_mqtt_message(client):
    # GIVEN
    with patch(
        "server.rest_api.mqtt_controller.rest_controller.mqtt_manager_service"
    ) as mock_mqtt_manager:
        # WHEN
        response = client.get("/api/mqtt")

        # THEN
        assert response.status_code == 200
        assert response.json == {"done": True}
        mock_mqtt_manager.publish_message.assert_called_once_with(
            topic="command/relays", message={"data": "relays_status_test"}
        )
