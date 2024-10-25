import pytest
import json
from flask import Flask
from unittest.mock import call
from server.interfaces.mqtt_interface import mqtt_client_interface
from server.managers.electrical_panel_manager.service import ElectricalPanelManager
from server.common import ServerBoxException, ErrorCode
from pytest_mock import MockerFixture
from unittest.mock import MagicMock, patch, mock_open


@pytest.fixture
def mock_mqtt_manager_service():
    with patch("server.managers.electrical_panel_manager.service.mqtt_manager_service") as mock:
        yield mock


@pytest.fixture
def electrical_panel_manager(app_mqtt_config, mock_mqtt_manager_service):
    app = Flask("testapp")
    app.config.from_mapping(app_mqtt_config)

    return ElectricalPanelManager(app)


def test_init_app(mock_mqtt_manager_service, app_mqtt_config):
    # GIVEN
    app = Flask(__name__)
    app.config.from_mapping(app_mqtt_config)
    manager = ElectricalPanelManager()

    # WHEN
    manager.init_app(app)

    # THEN
    assert (
        manager.mqtt_command_relays_topic
        == app.config["MQTT"]["TOPICS"]["MQTT_COMMAND_RELAYS_TOPIC"]
    )
    assert (
        manager.mqtt_relays_status_topic == app.config["MQTT"]["TOPICS"]["MQTT_RELAYS_STATUS_TOPIC"]
    )
    assert manager.last_relays_status_received is None

    mock_mqtt_manager_service.subscribe_to_topic.assert_called_once_with(
        topic=app.config["MQTT"]["TOPICS"]["MQTT_RELAYS_STATUS_TOPIC"],
        callback=manager.receive_relays_statuses,
    )


def test_get_relays_last_received_status_raises_exception(electrical_panel_manager):
    # WHEN
    with pytest.raises(ServerBoxException) as exc_info:
        electrical_panel_manager.get_relays_last_received_status()

    assert exc_info.value.code == ErrorCode.RELAYS_STATUS_NOT_RECEIVED.value
    assert exc_info.value.http_code == ErrorCode.RELAYS_STATUS_NOT_RECEIVED.http_code
    assert exc_info.value.message == ErrorCode.RELAYS_STATUS_NOT_RECEIVED.message


def test_get_relays_last_received_status_returns_value(electrical_panel_manager):
    # GIVEN
    expected_status = {"LastStatus": "Mock"}
    electrical_panel_manager.last_relays_status_received = expected_status

    # WHEN
    result = electrical_panel_manager.get_relays_last_received_status()

    # Assert
    assert result == expected_status


def test_get_single_relay_last_received_status_invalid_relay_number(electrical_panel_manager):
    # WHEN
    with pytest.raises(ServerBoxException) as exc_info:
        electrical_panel_manager.get_single_relay_last_received_status(7)  # Invalid relay number

    # THEN
    assert exc_info.value.code == ErrorCode.INVALID_RELAY_NUMBER.value
    assert exc_info.value.http_code == ErrorCode.INVALID_RELAY_NUMBER.http_code
    assert exc_info.value.message == ErrorCode.INVALID_RELAY_NUMBER.message


def test_get_single_relay_last_received_status_no_status_received(electrical_panel_manager):
    # WHEN
    with pytest.raises(ServerBoxException) as exc_info:
        electrical_panel_manager.get_single_relay_last_received_status(1)  # Valid relay number

    # THEN
    assert exc_info.value.code == ErrorCode.RELAYS_STATUS_NOT_RECEIVED.value
    assert exc_info.value.http_code == ErrorCode.RELAYS_STATUS_NOT_RECEIVED.http_code
    assert exc_info.value.message == ErrorCode.RELAYS_STATUS_NOT_RECEIVED.message


def test_get_single_relay_last_received_status_found(electrical_panel_manager, relays_status_off):
    # GIVEN
    electrical_panel_manager.last_relays_status_received = relays_status_off

    # WHEN
    result = electrical_panel_manager.get_single_relay_last_received_status(1)

    # Assert
    assert result.relay_number == 1
    assert result.status == relays_status_off.relay_statuses[1].status
    assert result.powered == relays_status_off.relay_statuses[1].powered


def test_get_single_relay_last_received_status_not_found(
    electrical_panel_manager, relays_status_no_2
):
    # GIVEN
    electrical_panel_manager.last_relays_status_received = relays_status_no_2

    # WHEN
    with pytest.raises(ServerBoxException) as exc_info:
        electrical_panel_manager.get_single_relay_last_received_status(2)  # Relay number not found

    # THEN
    assert exc_info.value.code == ErrorCode.RELAYS_STATUS_NOT_RECEIVED.value
    assert exc_info.value.http_code == ErrorCode.RELAYS_STATUS_NOT_RECEIVED.http_code
    assert exc_info.value.message == ErrorCode.RELAYS_STATUS_NOT_RECEIVED.message


def test_receive_relays_statuses_updates_last_status(electrical_panel_manager, relays_status_off):
    # WHEN
    electrical_panel_manager.receive_relays_statuses(relays_status_off)
    # Assert
    assert (
        electrical_panel_manager.last_relays_status_received.relay_statuses
        == relays_status_off.relay_statuses
    )


def test_publish_mqtt_relays_status_command(
    electrical_panel_manager, mock_mqtt_manager_service, relays_status_off, app_mqtt_config
):
    # GIVEN
    relays_status = relays_status_off

    # WHEN
    electrical_panel_manager.publish_mqtt_relays_status_command(relays_status)

    # THEN
    mock_mqtt_manager_service.publish_message.assert_called_once_with(
        topic=app_mqtt_config["MQTT"]["TOPICS"]["MQTT_COMMAND_RELAYS_TOPIC"], message=relays_status
    )
