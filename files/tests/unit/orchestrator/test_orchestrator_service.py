import pytest
from unittest.mock import patch
from flask import Flask
from server.orchestrator.service import Orchestrator


@pytest.fixture
def app():
    """Create a Flask app for testing."""
    app = Flask(__name__)
    app.config["CLOUD"] = {
        "SERVER_IP": "127.0.0.1",
        "PATHS": {"NOTIFY_STATUS": "/notify"},
        "PORT": 5000,
    }
    app.config["MQTT"] = {"TOPICS": {"MQTT_WIFI_STATUS_RELAYS_TOPIC": "wifi/status/relays"}}
    app.config["NOTIFICATION"] = {"CLOUD_SECS": 10, "MQTT_WIFI_STATUS_SECS": 10}
    app.config["POLLING"] = {"WIFI_STATUS_SECS": 5}
    return app


def test_init_app(app):
    # GIVEN
    with patch(
        "server.orchestrator.service.orchestrator_notification_service"
    ) as mock_notification_service, patch(
        "server.orchestrator.service.orchestrator_polling_service"
    ) as mock_polling_service:

        # WHEN
        Orchestrator(app)

        # THEN
        mock_notification_service.init_notification_module.assert_called_once_with(
            rpi_cloud_ip_addr="127.0.0.1",
            server_cloud_notify_status_path="/notify",
            server_cloud_port=5000,
            cloud_notification_period_in_secs=10,
            mqtt_wifi_status_relays_topic="wifi/status/relays",
            mqtt_wifi_status_notification_period_in_secs=10,
        )
        mock_polling_service.init_polling_module.assert_called_once_with(
            wifi_status_polling_period_in_secs=5,
        )
