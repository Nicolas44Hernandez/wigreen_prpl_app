import pytest
from unittest.mock import patch, MagicMock
from server.managers.wifi_bands_manager.model import WifiBandStatus
from server.orchestrator.polling.service import OrchestratorPolling, WifiStatusPoller


@pytest.fixture
def mock_wifi_bands_manager():
    """Fixture to mock wifi bands manager service"""
    with patch(
        "server.orchestrator.polling.service.wifi_bands_manager_service"
    ) as mock_wifi_service:
        yield mock_wifi_service


@pytest.fixture
def mock_threading():
    """Fixture to mock threading service"""
    with patch("server.orchestrator.polling.service.threading") as mock_threading:
        yield mock_threading


@pytest.fixture
def wifi_status_poller():
    """Create an instance of WifiStatusPoller for testing."""
    return WifiStatusPoller(wifi_status_polling_period_in_secs=1)


@pytest.fixture
def orchestrator_poller():
    """Create an instance of OrchestratorPolling for testing."""
    return OrchestratorPolling()


def test_poll_wifi_status(wifi_status_poller, mock_wifi_bands_manager):
    # GIVEN
    wifi_status_poller._stop_event = MagicMock()
    wifi_status_poller._stop_event.is_set.side_effect = [False, True]
    mock_wifi_bands_manager.update_wifi_status_attribute = MagicMock()

    # WHEN
    wifi_status_poller.poll_wifi_status()

    # THEN
    mock_wifi_bands_manager.update_wifi_status_attribute.assert_called()


def test_cloud_notifier_start_and_stop(wifi_status_poller, mock_threading):
    # WHEN
    wifi_status_poller.start()

    # THEN
    mock_threading.Thread.assert_called_once()
    assert wifi_status_poller.thread is not None

    # WHEN
    wifi_status_poller.stop()

    # THEN
    assert wifi_status_poller._stop_event.is_set()
    mock_threading.Thread().join.assert_called_once()


def test_poll_wifi_status_with_stop_event(wifi_status_poller, mock_wifi_bands_manager):
    # GIVEN
    mock_wifi_bands_manager.update_wifi_status_attribute = MagicMock()

    # WHEN
    wifi_status_poller.start()
    wifi_status_poller.stop()

    # THEN
    assert wifi_status_poller._stop_event.is_set()
    mock_wifi_bands_manager.update_wifi_status_attribute.assert_called()


def test_init_polling_module(orchestrator_poller):
    # GIVEN
    wifi_status_polling_period = 5
    with patch(
        "server.orchestrator.polling.service.OrchestratorPolling.schedule_resources_status_polling"
    ) as mock_schedule_resources_status_polling:
        # WHEN
        orchestrator_poller.init_polling_module(wifi_status_polling_period)

        # THEN
        mock_schedule_resources_status_polling.assert_called_once()
        assert orchestrator_poller.wifi_status_polling_period_in_secs == wifi_status_polling_period


def test_schedule_resources_status_polling(
    orchestrator_poller,
):
    # GIVEN
    wifi_status_polling_period = 5
    orchestrator_poller.wifi_status_polling_period_in_secs = wifi_status_polling_period

    with patch("server.orchestrator.polling.service.WifiStatusPoller") as mock_wifi_status_poller:
        # WHEN
        orchestrator_poller.schedule_resources_status_polling()

        # THEN
        mock_wifi_status_poller.assert_called_once_with(
            wifi_status_polling_period_in_secs=wifi_status_polling_period
        )
        mock_wifi_status_poller.return_value.start.assert_called_once()
