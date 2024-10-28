import pytest
from datetime import datetime
from unittest.mock import patch
from unittest.mock import MagicMock
from server.interfaces.mqtt_interface import mqtt_client_interface, SingleRelayStatus, RelaysStatus
from server.managers.wifi_bands_manager.model import WifiBandStatus, WifiStatus


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


@pytest.fixture
def wifi_status_on():
    return WifiStatus(
        status=True,
        bands_status=[
            WifiBandStatus(band="2.4GHz", status=True),
            WifiBandStatus(band="5GHz", status=True),
            WifiBandStatus(band="6GHz", status=True),
        ],
    )


@pytest.fixture
def wifi_status_off():
    return WifiStatus(
        status=True,
        bands_status=[
            WifiBandStatus(band="2.4GHz", status=False),
            WifiBandStatus(band="5GHz", status=False),
            WifiBandStatus(band="6GHz", status=False),
        ],
    )


@pytest.fixture
def relays_status_off():
    RELAYS_STATUS = [
        SingleRelayStatus(relay_number=0, status=False, powered=False),
        SingleRelayStatus(relay_number=1, status=False, powered=False),
        SingleRelayStatus(relay_number=2, status=False, powered=False),
        SingleRelayStatus(relay_number=3, status=False, powered=False),
        SingleRelayStatus(relay_number=4, status=False, powered=False),
        SingleRelayStatus(relay_number=5, status=False, powered=False),
    ]

    relays_status = RelaysStatus(relay_statuses=RELAYS_STATUS, command=True)
    relays_status.timestamp = datetime(2024, 10, 24, 10, 12, 54, 566714)

    return relays_status


@pytest.fixture
def relays_status_no_2():
    RELAYS_STATUS = [
        SingleRelayStatus(relay_number=0, status=False, powered=False),
        SingleRelayStatus(relay_number=1, status=False, powered=False),
        SingleRelayStatus(relay_number=3, status=False, powered=False),
        SingleRelayStatus(relay_number=4, status=False, powered=False),
        SingleRelayStatus(relay_number=5, status=False, powered=False),
    ]

    relays_status = RelaysStatus(relay_statuses=RELAYS_STATUS, command=True)
    relays_status.timestamp = datetime(2024, 10, 24, 10, 12, 54, 566714)

    return relays_status
