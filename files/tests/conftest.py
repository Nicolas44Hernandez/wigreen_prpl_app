import pytest
from unittest.mock import patch
from unittest.mock import MagicMock
from server.interfaces.mqtt_interface import mqtt_client_interface


@pytest.fixture
def mock_sleep():
    with patch("time.sleep", return_value=None) as mock:
        yield mock  # Provide the mock to the test


@pytest.fixture
def mqtt_client():
    mqtt_client = mqtt_client_interface(
        broker_address="test.broker", username="username", password="pwd"
    )
    mqtt_client._client = MagicMock()  # Mock the MQTT client
    return mqtt_client
