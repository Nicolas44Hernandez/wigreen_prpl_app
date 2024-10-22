import pytest


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
