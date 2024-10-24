import pytest
import json
from flask import Flask
from unittest.mock import call
from server.interfaces.amx_usp_interface import AmxUspInterface
from server.managers.wifi_bands_manager.service import WifiBandsManager, BANDS, STATUSES
from server.common import ServerBoxException, ErrorCode
from pytest_mock import MockerFixture
from unittest.mock import MagicMock, patch, mock_open


@pytest.fixture
def wifi_datamodel():
    return {
        "2.4GHz": {
            "STATUS": "Device.WiFi.Radio.1.Status",
            "Up": {"PATH": "Device.WiFi.Radio.1", "PARAMS": {"Enable": "1"}},
            "Down": {"PATH": "Device.WiFi.Radio.1", "PARAMS": {"Enable": "0"}},
        },
        "5GHz": {
            "STATUS": "Device.WiFi.Radio.2.Status",
            "Up": {"PATH": "Device.WiFi.Radio.2", "PARAMS": {"Enable": "1"}},
            "Down": {"PATH": "Device.WiFi.Radio.2", "PARAMS": {"Enable": "0"}},
        },
        "6GHz": {
            "STATUS": "Device.WiFi.Radio.3.Status",
            "Up": {"PATH": "Device.WiFi.Radio.3", "PARAMS": {"Enable": "1"}},
            "Down": {"PATH": "Device.WiFi.Radio.3", "PARAMS": {"Enable": "0"}},
        },
    }


@pytest.fixture
def wifi_bands_manager(wifi_datamodel):
    app = Flask("testapp")
    app.config.from_mapping(
        {
            "WIFI_DATAMODEL_CONFIG_FILE": "fake_file.json",
        }
    )

    # Mock the load_datamodel method
    with patch.object(WifiBandsManager, "load_datamodel", return_value=None) as mock_load:
        manager = WifiBandsManager(app)
        manager.datamodel = wifi_datamodel
        manager.amx_usp_interface = MagicMock()  # Mock the amx_usp_interface

        yield manager  # Use yield to allow for teardown if needed


def test_wifi_bands_manager_constructor():
    # GIVEN
    app = Flask(__name__)
    app.config["WIFI_DATAMODEL_CONFIG_FILE"] = "dummy_path.json"
    # Mock the load_datamodel method
    with patch.object(WifiBandsManager, "load_datamodel", return_value=None) as mock_load:

        # WHEN
        manager = WifiBandsManager(app)

        # THEN
        mock_load.assert_called_once_with(app.config["WIFI_DATAMODEL_CONFIG_FILE"])
        assert isinstance(manager.amx_usp_interface, AmxUspInterface)


def test_load_datamodel():
    # GIVEN
    mock_data = '{"key": "value"}'  # Example JSON data
    datamodel_json_file = "dummy_path.json"
    # Mock the open method
    with patch("builtins.open", mock_open(read_data=mock_data)):
        manager = WifiBandsManager()

        # WHEN
        manager.load_datamodel(datamodel_json_file)

        # THEN
        assert manager.datamodel == json.loads(mock_data)


def test_load_datamodel_exception():
    # GIVEN
    datamodel_json_file = "dummy_path.json"
    # Mock the open method to raise an exception
    with patch("builtins.open", mock_open()) as mocked_open:
        mocked_open.side_effect = IOError("File not found")
        manager = WifiBandsManager()

        # WHEN
        # Assert that the exception is raised
        with pytest.raises(ServerBoxException):
            manager.load_datamodel(datamodel_json_file)


def test_get_band_status_valid(wifi_bands_manager, wifi_datamodel):
    # GIVEN
    wifi_bands_manager.amx_usp_interface.read_object.return_value = [
        {"WiFi.Radio.1": {"Status": "Active"}}
    ]

    # WHEN
    status = wifi_bands_manager.get_band_status("2.4GHz")

    # THEN
    assert status == "Active"
    wifi_bands_manager.amx_usp_interface.read_object.assert_called_once_with(
        path=wifi_datamodel["2.4GHz"]["STATUS"]
    )


# Test function for unknown band
def test_get_band_status_unknown_band(wifi_bands_manager):
    # WHEN
    with pytest.raises(ServerBoxException) as exc_info:
        wifi_bands_manager.get_band_status("UnknownBand")

    # THEN
    assert exc_info.value.code == ErrorCode.UNKNOWN_BAND_WIFI.value
    assert exc_info.value.http_code == ErrorCode.UNKNOWN_BAND_WIFI.http_code
    assert exc_info.value.message == ErrorCode.UNKNOWN_BAND_WIFI.message


# Test function for unexpected error
def test_get_band_status_unexpected_error(wifi_bands_manager):
    # GIVEN
    wifi_bands_manager.amx_usp_interface.read_object.return_value = [{}]

    with pytest.raises(ServerBoxException) as exc_info:
        # WHEN
        wifi_bands_manager.get_band_status("2.4GHz")

    # THEN
    assert exc_info.value.code == ErrorCode.UNEXPECTED_ERROR.value
    assert exc_info.value.http_code == ErrorCode.UNEXPECTED_ERROR.http_code
    assert exc_info.value.message == ErrorCode.UNEXPECTED_ERROR.message


def test_get_wifi_status_up(wifi_bands_manager):

    # GIVEN
    with patch.object(wifi_bands_manager, "get_band_status", return_value="Up"):

        # WHEN
        status = wifi_bands_manager.get_wifi_status()

        # THEN
        assert status == "Up"


def test_get_wifi_status_down(wifi_bands_manager):

    # GIVEN
    with patch.object(wifi_bands_manager, "get_band_status", return_value="Down"):

        # WHEN
        status = wifi_bands_manager.get_wifi_status()

        # THEN
        assert status == "Down"


def test_set_band_status_success(wifi_bands_manager, wifi_datamodel, mock_sleep):
    # GIVEN
    # Mock the get_band_status method
    with patch.object(wifi_bands_manager, "get_band_status", side_effect=["Down", "Up"]):
        # Mock the set_object method
        with patch.object(
            wifi_bands_manager.amx_usp_interface, "set_object", return_value="Success"
        ):
            # WHEN
            status = wifi_bands_manager.set_band_status("2.4GHz", "Up")

            # THEN
            assert status == "Up"
            wifi_bands_manager.amx_usp_interface.set_object.assert_called_once_with(
                path=wifi_datamodel["2.4GHz"]["Up"]["PATH"],
                params=wifi_datamodel["2.4GHz"]["Up"]["PARAMS"],
            )


def test_set_band_status_unknown_band(wifi_bands_manager, mock_sleep):

    # GIVEN
    with pytest.raises(ServerBoxException) as exc_info:
        wifi_bands_manager.set_band_status("UnknownBand", "Up")

    # THEN
    assert exc_info.value.code == ErrorCode.UNKNOWN_BAND_WIFI.value
    assert exc_info.value.http_code == ErrorCode.UNKNOWN_BAND_WIFI.http_code
    assert exc_info.value.message == ErrorCode.UNKNOWN_BAND_WIFI.message


def test_set_band_status_unknown_status(wifi_bands_manager, mock_sleep):
    # GIVEN
    with pytest.raises(ServerBoxException) as exc_info:
        wifi_bands_manager.set_band_status("2.4GHz", "UnknownStatus")

    # THEN
    assert exc_info.value.code == ErrorCode.UNKNOWN_WIFI_STATUS.value
    assert exc_info.value.http_code == ErrorCode.UNKNOWN_WIFI_STATUS.http_code
    assert exc_info.value.message == ErrorCode.UNKNOWN_WIFI_STATUS.message


def test_set_band_status_already_satisfied(wifi_bands_manager, mock_sleep):
    # GIVEN
    with patch.object(wifi_bands_manager, "get_band_status", return_value="Up"):

        # WHEN
        status = wifi_bands_manager.set_band_status("2.4GHz", "Up")

        # THEN
        assert status == "Up"


def test_set_band_status_error_getting_status(wifi_bands_manager, mock_sleep):
    # GIVEN
    with patch.object(wifi_bands_manager, "get_band_status", return_value=None):

        # WHEN
        status = wifi_bands_manager.set_band_status("2.4GHz", "Up")

        # THEN
        assert status is None


def test_set_band_status_too_long(wifi_bands_manager, wifi_datamodel, mock_sleep):
    # GIVEN
    with patch.object(wifi_bands_manager, "get_band_status", return_value="Down"):
        with patch.object(
            wifi_bands_manager.amx_usp_interface, "set_object", return_value="Success"
        ):
            # Mock the STATUS_CHANGE_TIMEOUT_IN_SECS variable
            with patch(
                "server.managers.wifi_bands_manager.service.STATUS_CHANGE_TIMEOUT_IN_SECS", new=1
            ):

                # WHEN
                status = wifi_bands_manager.set_band_status("2.4GHz", "Up")

                # THEN
                assert status == None
                wifi_bands_manager.amx_usp_interface.set_object.assert_called_once_with(
                    path=wifi_datamodel["2.4GHz"]["Up"]["PATH"],
                    params=wifi_datamodel["2.4GHz"]["Up"]["PARAMS"],
                )


def test_set_wifi_status_success(wifi_bands_manager):
    # GIVEN
    with patch.object(
        wifi_bands_manager, "set_band_status", return_value="Up"
    ) as mock_set_band_status:

        # WHEN
        result = wifi_bands_manager.set_wifi_status("Up")

        # THEN
        assert mock_set_band_status.call_count == len(BANDS)
        assert result == "Up"


# Test function for unknown status
def test_set_wifi_status_unknown_status(wifi_bands_manager):
    # GIVEN
    with pytest.raises(ServerBoxException) as exc_info:
        wifi_bands_manager.set_wifi_status("UnknownStatus")

    # THEN
    assert exc_info.value.code == ErrorCode.UNKNOWN_WIFI_STATUS.value
    assert exc_info.value.http_code == ErrorCode.UNKNOWN_WIFI_STATUS.http_code
    assert exc_info.value.message == ErrorCode.UNKNOWN_WIFI_STATUS.message
