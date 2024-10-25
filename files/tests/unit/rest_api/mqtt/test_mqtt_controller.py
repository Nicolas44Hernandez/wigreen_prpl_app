import pytest
from unittest.mock import patch
from flask import Flask
from server.rest_api.mqtt_controller.rest_controller import bp as mqtt_controller_bp
from server.common import ServerBoxException, handle_server_box_exception


@pytest.fixture
def app_with_bp():
    """Create a Flask app for testing."""
    app = Flask(__name__)
    app.register_error_handler(ServerBoxException, handle_server_box_exception)
    app.register_blueprint(mqtt_controller_bp, url_prefix="/api/mqtt")

    return app


@pytest.fixture
def client(app_with_bp):
    """Create a test client."""
    return app_with_bp.test_client()


def test_get_mqtt_message(client):
    # GIVEN
    with patch(
        "server.rest_api.mqtt_controller.rest_controller.mqtt_manager_service"
    ) as mock_mqtt_manager:
        # WHEN
        response = client.get("/api/mqtt/msg")

        # THEN
        assert response.status_code == 200
        assert response.json == {"done": True}
        mock_mqtt_manager.publish_message.assert_called_once_with(
            topic="command/relays", message={"data": "relays_status_test"}
        )
