# test_orchestrator_use_situations.py
import pytest
from unittest.mock import patch, MagicMock, mock_open
import json
from datetime import datetime
from server.orchestrator.use_situations.service import (
    OrchestratorUseSituations,
    ServerBoxException,
    ErrorCode,
)
from server.interfaces.mqtt_interface import SingleRelayStatus, RelaysStatus


@pytest.fixture
def orchestrator_use_situations():
    return OrchestratorUseSituations()


@pytest.fixture
def use_situations_dict():
    use_situations_dict = {
        "PRESENCE_HOME_OFFICE": {
            "SWITCH_TO": "ABSENCE_LOW_CONSUMPTION",
            "WIFI": {"2.4GHz": True, "5GHz": True, "6GHz": True},
            "ELECTRICAL_OUTLETS": {"0": True, "1": True, "2": True},
            "POWER_STRIP": {"1": True, "2": True, "3": True, "4": True},
        },
        "PRESENCE_DAY_LOW_CONSUMPTION": {
            "SWITCH_TO": "ABSENCE_LOW_CONSUMPTION",
            "WIFI": {"2.4GHz": True, "5GHz": False, "6GHz": False},
            "ELECTRICAL_OUTLETS": {"0": True, "1": True, "2": True},
            "POWER_STRIP": {"1": True, "2": True, "3": False, "4": False},
        },
    }
    return use_situations_dict


def test_init_use_situations_module(orchestrator_use_situations):
    # GIVEN
    mock_config_file = "use-situations-config.json"
    mock_default_situation = "DEFAULT_USE_SITUATION"

    with patch.object(
        orchestrator_use_situations, "load_use_situations"
    ) as mock_load, patch.object(orchestrator_use_situations, "set_use_situation") as mock_set:

        # WHEN
        orchestrator_use_situations.init_use_situations_module(
            mock_config_file, mock_default_situation
        )

        # THEN
        mock_load.assert_called_once_with(mock_config_file)
        mock_set.assert_called_once_with(use_situation=mock_default_situation)


def test_load_use_situations_success(orchestrator_use_situations, use_situations_dict):
    # GIVEN
    mock_config_file = "use-situations-config.json"
    mock_configuration = {"USE_SITUATIONS": use_situations_dict}

    with patch("builtins.open", mock_open(read_data=json.dumps(mock_configuration))) as mock_file:
        # WHEN
        orchestrator_use_situations.load_use_situations(mock_config_file)

        # THEN
        assert (
            orchestrator_use_situations.use_situations_dict == mock_configuration["USE_SITUATIONS"]
        )
        mock_file.assert_called_once_with(mock_config_file)


def test_load_use_situations_file_not_found(orchestrator_use_situations):
    # GIVEN
    mock_config_file = "invalid_config.json"

    with patch("builtins.open", mock_open()):
        # WHEN
        with pytest.raises(ServerBoxException) as exc_info:
            orchestrator_use_situations.load_use_situations(mock_config_file)
        # THEN
        assert exc_info.value.code == ErrorCode.USE_SITUATIONS_CONFIG_FILE_ERROR.value


def test_load_use_situations_json_decode_error(orchestrator_use_situations):
    # GIVEN
    mock_config_file = "use-situations-config.json"

    with patch("builtins.open", mock_open(read_data="invalid json")) as mock_file:
        # GIVEN
        with pytest.raises(ServerBoxException) as exc_info:
            orchestrator_use_situations.load_use_situations(mock_config_file)
        # THEN
        assert exc_info.value.code == ErrorCode.USE_SITUATIONS_CONFIG_FILE_ERROR.value


def test_set_use_situation_valid(orchestrator_use_situations, use_situations_dict):
    # GIVEN
    orchestrator_use_situations.use_situations_dict = use_situations_dict
    orchestrator_use_situations.set_use_situation_wifi_status = MagicMock()
    orchestrator_use_situations.set_use_situation_electrical_panel_status = MagicMock()

    # WHEN
    orchestrator_use_situations.set_use_situation("PRESENCE_DAY_LOW_CONSUMPTION")

    # THEN
    assert orchestrator_use_situations.current_use_situation == "PRESENCE_DAY_LOW_CONSUMPTION"
    orchestrator_use_situations.set_use_situation_wifi_status.assert_called_once_with(
        use_situations_dict["PRESENCE_DAY_LOW_CONSUMPTION"]["WIFI"]
    )
    orchestrator_use_situations.set_use_situation_electrical_panel_status.assert_called_once_with(
        use_situations_dict["PRESENCE_DAY_LOW_CONSUMPTION"]["ELECTRICAL_OUTLETS"]
    )


def test_set_use_situation_invalid(orchestrator_use_situations, use_situations_dict):
    # GIVEN
    orchestrator_use_situations.use_situations_dict = use_situations_dict

    # WHEN
    with pytest.raises(ServerBoxException) as exc_info:
        orchestrator_use_situations.set_use_situation("invalid")
    # THEN
    assert exc_info.value.code == ErrorCode.INVALID_USE_SITUATION.value
    assert orchestrator_use_situations.current_use_situation is None


def test_set_use_situation_wifi_status_success(orchestrator_use_situations):
    # GIVEN
    wifi_bands_status = {
        "2.4GHz": "Up",
        "5GHz": "Up",
        "6GHz": "Up",
    }
    with patch(
        "server.orchestrator.use_situations.service.wifi_bands_manager_service"
    ) as mock_wifi_service:
        mock_wifi_service.set_band_status.return_value = "Up"

        # WHEN
        result = orchestrator_use_situations.set_use_situation_wifi_status(wifi_bands_status)

        # THEN
        mock_wifi_service.set_band_status.assert_any_call(band="2.4GHz", new_status="Up")
        mock_wifi_service.set_band_status.assert_any_call(band="5GHz", new_status="Up")
        mock_wifi_service.set_band_status.assert_any_call(band="5GHz", new_status="Up")


def test_set_use_situation_wifi_status_failure(orchestrator_use_situations):
    # GIVEN
    wifi_bands_status = {
        "2.4GHz": "Up",
        "5GHz": "Up",
        "6GHz": "Up",
    }

    with patch(
        "server.orchestrator.use_situations.service.wifi_bands_manager_service"
    ) as mock_wifi_service:
        mock_wifi_service.set_band_status.return_value = None

        # WHEN
        result = orchestrator_use_situations.set_use_situation_wifi_status(wifi_bands_status)

        # THEN
        assert result is False
        mock_wifi_service.set_band_status.assert_any_call(band="2.4GHz", new_status="Up")


def test_set_use_situation_electrical_panel_status(orchestrator_use_situations):
    # GIVEN
    electrical_panel_status = {
        0: True,
        1: False,
        2: False,
        3: False,
        4: True,
        5: True,
    }
    with patch(
        "server.orchestrator.use_situations.service.electrical_panel_manager_service"
    ) as mock_electrical_service:
        # WHEN
        orchestrator_use_situations.set_use_situation_electrical_panel_status(
            electrical_panel_status
        )

        # THEN
        expected_relays_statuses = RelaysStatus(
            relay_statuses=[
                SingleRelayStatus(relay_number=0, status=True, powered=False),
                SingleRelayStatus(relay_number=1, status=False, powered=False),
                SingleRelayStatus(relay_number=2, status=True, powered=False),
                SingleRelayStatus(relay_number=3, status=False, powered=False),
                SingleRelayStatus(relay_number=4, status=False, powered=False),
                SingleRelayStatus(relay_number=5, status=False, powered=False),
            ],
            command=True,
            timestamp=datetime.now(),
        )

        # THEN
        mock_electrical_service.publish_mqtt_relays_status_command.assert_called_once()
        call_args = mock_electrical_service.publish_mqtt_relays_status_command.call_args[0][0]
        assert call_args.relay_statuses == expected_relays_statuses.relay_statuses
        assert call_args.command == expected_relays_statuses.command


def test_set_use_situation_electrical_panel_status_empty(orchestrator_use_situations):
    # GIVEN
    electrical_panel_status = {}

    with patch(
        "server.orchestrator.use_situations.service.electrical_panel_manager_service"
    ) as mock_electrical_service:
        # WHEN
        orchestrator_use_situations.set_use_situation_electrical_panel_status(
            electrical_panel_status
        )

        # THEN
        expected_relays_statuses = RelaysStatus(
            relay_statuses=[
                SingleRelayStatus(relay_number=0, status=False, powered=False),
                SingleRelayStatus(relay_number=1, status=False, powered=False),
                SingleRelayStatus(relay_number=2, status=False, powered=False),
                SingleRelayStatus(relay_number=3, status=False, powered=False),
                SingleRelayStatus(relay_number=4, status=False, powered=False),
                SingleRelayStatus(relay_number=5, status=False, powered=False),
            ],
            command=True,
            timestamp=datetime.now(),
        )

        # THEN
        mock_electrical_service.publish_mqtt_relays_status_command.assert_called_once()
        call_args = mock_electrical_service.publish_mqtt_relays_status_command.call_args[0][0]
        assert call_args.relay_statuses == expected_relays_statuses.relay_statuses
        assert call_args.command == expected_relays_statuses.command


def test_get_current_use_situation(orchestrator_use_situations):
    # GIVEN
    orchestrator_use_situations.current_use_situation = "PRESENCE_DAY_LOW_CONSUMPTION"
    # WHEN
    current_situation = orchestrator_use_situations.get_current_use_situation()

    # THEN
    assert current_situation == "PRESENCE_DAY_LOW_CONSUMPTION"


def test_get_use_situation_list(orchestrator_use_situations, use_situations_dict):
    # GIVEN
    orchestrator_use_situations.use_situations_dict = use_situations_dict

    # WHEN
    use_situations_list = orchestrator_use_situations.get_use_situation_list()

    # WHEN
    assert use_situations_list == list(use_situations_dict.keys())


def test_get_use_situation_to_switch(orchestrator_use_situations, use_situations_dict):
    # GIVEN
    orchestrator_use_situations.use_situations_dict = use_situations_dict
    orchestrator_use_situations.current_use_situation = "PRESENCE_DAY_LOW_CONSUMPTION"

    # WHEN
    situation_to_switch = orchestrator_use_situations.get_use_situation_to_switch()

    # THEN
    assert situation_to_switch == "ABSENCE_LOW_CONSUMPTION"
