import pytest
from flask import Flask
from server.managers.mqtt_manager.service import MQTTManager
from unittest.mock import MagicMock, patch


@pytest.fixture
def app_mqtt_config():
    return {
        "MQTT": {
            "BASIC": {
                "MQTT_BROKER_ADDRESS": "localhost",
                "MQTT_USERNAME": "rpi_box",
                "MQTT_PASSWORD": "lamp",
                "MQTT_QOS": 1,
                "MQTT_RECONNECTION_TIMEOUT_IN_SEG": 1,
                "MQTT_MAX_RECONNECTION_ATTEMPS": 3,
                "MQTT_MSG_PUBLISH_TIMEOUT_IN_SECS": 5,
            },
            "TOPICS": {
                "MQTT_COMMAND_TOPIC": "command/general",
                "MQTT_COMMAND_RELAYS_TOPIC": "command/relays",
                "MQTT_RELAYS_STATUS_TOPIC": "status/relays",
                "MQTT_WIFI_STATUS_RELAYS_TOPIC": "wifi/status/relays",
            },
        },
    }


@pytest.fixture
def mqtt_manager(app_mqtt_config):
    app = Flask("testapp")
    app.config.from_mapping(app_mqtt_config)

    # Mock the init_mqtt_service method
    with patch.object(MQTTManager, "init_mqtt_service", return_value=None) as mock_load:
        manager = MQTTManager(app)
        manager.mqtt_client = MagicMock()  # Mock the mqtt_interface

        yield manager


def test_mqtt_manager_constructor(app_mqtt_config):
    # GIVEN
    app = Flask(__name__)
    app.config.from_mapping(app_mqtt_config)
    with patch.object(MQTTManager, "init_mqtt_service", return_value=None) as mock_load:

        # WHEN
        manager = MQTTManager(app)

        # THEN
        mock_load.assert_called_once()
        assert manager.broker_address == app_mqtt_config["MQTT"]["BASIC"]["MQTT_BROKER_ADDRESS"]
        assert manager.username == app_mqtt_config["MQTT"]["BASIC"]["MQTT_USERNAME"]
        assert manager.password == app_mqtt_config["MQTT"]["BASIC"]["MQTT_PASSWORD"]
        assert manager.qos == app_mqtt_config["MQTT"]["BASIC"]["MQTT_QOS"]
        assert (
            manager.reconnection_timeout_in_secs
            == app_mqtt_config["MQTT"]["BASIC"]["MQTT_RECONNECTION_TIMEOUT_IN_SEG"]
        )
        assert (
            manager.max_reconnection_attemps
            == app_mqtt_config["MQTT"]["BASIC"]["MQTT_MAX_RECONNECTION_ATTEMPS"]
        )
        assert (
            manager.publish_timeout_in_secs
            == app_mqtt_config["MQTT"]["BASIC"]["MQTT_MSG_PUBLISH_TIMEOUT_IN_SECS"]
        )


def test_subscribe_to_topic(mqtt_manager):
    # GIVEN
    mqtt_manager.mqtt_client.subscribe.return_value = True

    def callback_fn():
        pass

    # WHEN
    mqtt_manager.subscribe_to_topic(topic="topic1", callback=callback_fn)

    # THEN
    mqtt_manager.mqtt_client.subscribe.assert_called_with(topic="topic1", callback=callback_fn)


def test_publish_msg(mqtt_manager):
    # GIVEN
    mqtt_manager.mqtt_client.publish.return_value = True

    # WHEN
    mqtt_manager.publish_message(topic="topic1", message="msg")

    # THEN
    mqtt_manager.mqtt_client.publish.assert_called_with(topic="topic1", message="msg")
