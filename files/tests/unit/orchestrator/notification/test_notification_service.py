from datetime import datetime
import pytest
from unittest.mock import patch, MagicMock
from server.interfaces.mqtt_interface.model import RelaysStatus
from server.orchestrator.notification.service import (
    CloudServerNotifier,
    MqttWifiStatusNotifier,
    OrchestratorNotification,
)
from server.managers.wifi_bands_manager.model import WifiBandStatus
from server.orchestrator.notification.service import POST_TIMEOUT_IN_SECS


@pytest.fixture
def mock_services():
    """Fixture to mock external services."""
    with patch(
        "server.orchestrator.notification.service.wifi_bands_manager_service"
    ) as mock_wifi_service, patch(
        "server.orchestrator.notification.service.electrical_panel_manager_service"
    ) as mock_electrical_service, patch(
        "server.orchestrator.notification.service.orchestrator_notification_service"
    ) as mock_notification_service, patch(
        "server.orchestrator.notification.service.orchestrator_use_situations_service"
    ) as mock_use_situations_service, patch(
        "server.orchestrator.notification.service.mqtt_manager_service"
    ) as mock_mqtt_manager_service:
        yield mock_wifi_service, mock_electrical_service, mock_notification_service, mock_use_situations_service, mock_mqtt_manager_service


@pytest.fixture
def mock_http():
    """Fixture to mock http service"""
    with patch("server.orchestrator.notification.service.http.client.HTTPConnection") as mock_http:
        yield mock_http


@pytest.fixture
def mock_threading():
    """Fixture to mock threading service"""
    with patch("server.orchestrator.notification.service.threading") as mock_threading:
        yield mock_threading


@pytest.fixture
def mock_socket():
    """Fixture to mock socket service"""
    with patch("server.orchestrator.notification.service.socket.socket") as mock_socket:
        yield mock_socket


@pytest.fixture
def cloud_server_notifier():
    """Create an instance of CloudServerNotifier for testing."""
    return CloudServerNotifier(cloud_notification_period_in_secs=1)


@pytest.fixture
def mqtt_wifi_status_notifier():
    """Create an instance of MqttWifiStatusNotifier for testing."""
    return MqttWifiStatusNotifier(mqtt_notification_period_in_secs=1)


@pytest.fixture
def orchestrator_notifier():
    """Create an instance of OrchestratorNotification for testing."""
    return OrchestratorNotification()


def test_cloud_notifier_start_and_stop(cloud_server_notifier, mock_threading):
    # WHEN
    cloud_server_notifier.start()

    # THEN
    mock_threading.Thread.assert_called_once()
    assert cloud_server_notifier.thread is not None

    # WHEN
    cloud_server_notifier.stop()

    # THEN
    assert cloud_server_notifier._stop_event.is_set()
    mock_threading.Thread().join.assert_called_once()


def test_post_cloud_notification_success(
    cloud_server_notifier,
    mock_services,
    relays_status_off,
    wifi_status_off,
    mock_sleep,
):
    # GIVEN
    (
        mock_wifi_service,
        mock_electrical_service,
        mock_notification_service,
        mock_use_situations_service,
        _,
    ) = mock_services
    mock_wifi_service.get_current_wifi_status.return_value = wifi_status_off
    mock_use_situations_service.get_current_use_situation.return_value = "CURRENT_USE_SITUATION"
    mock_electrical_service.get_relays_last_received_status.return_value = relays_status_off
    cloud_server_notifier._stop_event = MagicMock()
    cloud_server_notifier._stop_event.is_set.side_effect = [False, True]

    # WHEN
    cloud_server_notifier.post_cloud_notification()

    # THEN
    mock_wifi_service.update_wifi_status_attribute.assert_called_once()
    mock_wifi_service.get_current_wifi_status.assert_called_once()
    mock_use_situations_service.get_current_use_situation.assert_called_once()
    mock_notification_service.notify_cloud_server.assert_called_once_with(
        bands_status=wifi_status_off.bands_status,
        use_situation="CURRENT_USE_SITUATION",
        relay_statuses=relays_status_off,
    )
    assert cloud_server_notifier._stop_event.is_set.call_count == 2


def test_post_cloud_notification_with_exception(
    cloud_server_notifier,
    mock_services,
    wifi_status_off,
    mock_sleep,
):
    # GIVEN
    (
        mock_wifi_service,
        mock_electrical_service,
        mock_notification_service,
        mock_use_situations_service,
        _,
    ) = mock_services
    mock_use_situations_service.get_current_use_situation.return_value = "CURRENT_USE_SITUATION"
    mock_wifi_service.get_current_wifi_status.return_value = wifi_status_off
    mock_electrical_service.get_relays_last_received_status.side_effect = Exception("Error")
    cloud_server_notifier._stop_event = MagicMock()
    cloud_server_notifier._stop_event.is_set.side_effect = [False, True]

    # WHEN
    cloud_server_notifier.post_cloud_notification()

    # THEN
    mock_wifi_service.update_wifi_status_attribute.assert_called_once()
    mock_wifi_service.get_current_wifi_status.assert_called_once()
    mock_notification_service.notify_cloud_server.assert_called_once_with(
        bands_status=wifi_status_off.bands_status,
        use_situation="CURRENT_USE_SITUATION",
        relay_statuses=None,
    )
    assert cloud_server_notifier._stop_event.is_set.call_count == 2


def test_mqtt_wifi_status_notifier_start_and_stop(mqtt_wifi_status_notifier, mock_threading):
    # WHEN
    mqtt_wifi_status_notifier.start()

    # THEN
    mock_threading.Thread.assert_called_once()
    assert mqtt_wifi_status_notifier.thread is not None

    # WHEN
    mqtt_wifi_status_notifier.stop()

    # THEN
    assert mqtt_wifi_status_notifier._stop_event.is_set()
    mock_threading.Thread().join.assert_called_once()


def test_publish_mqtt_notification(mqtt_wifi_status_notifier, mock_services, wifi_status_on):
    # GIVEN
    mock_wifi_service, _, mock_notification_service, _, _ = mock_services
    mock_wifi_service.get_current_wifi_status.return_value = wifi_status_on
    mqtt_wifi_status_notifier._stop_event = MagicMock()
    mqtt_wifi_status_notifier._stop_event.is_set.side_effect = [False, True]

    # WHEN
    mqtt_wifi_status_notifier.publish_mqtt_notification()

    # THEN
    mock_wifi_service.get_current_wifi_status.assert_called()
    mock_notification_service.notify_wifi_status_mqtt.assert_called_once_with(
        bands_status=wifi_status_on.bands_status
    )


def test_publish_mqtt_notification_with_no_status(mqtt_wifi_status_notifier, mock_services):
    # GIVEN
    mock_wifi_service, _, mock_notification_service, _, _ = mock_services
    mock_wifi_service.get_current_wifi_status.return_value = None
    mqtt_wifi_status_notifier._stop_event = MagicMock()
    mqtt_wifi_status_notifier._stop_event.is_set.side_effect = [False, True]

    # WHEN
    mqtt_wifi_status_notifier.publish_mqtt_notification()

    # Assert
    mock_wifi_service.get_current_wifi_status.assert_called()
    mock_notification_service.notify_wifi_status_mqtt.assert_not_called()


def test_orchestrator_notification_init():
    # GIVEN
    orchestrator = OrchestratorNotification()
    orchestrator.schedule_notifications = MagicMock()

    # WHEN
    orchestrator.init_notification_module(
        rpi_cloud_ip_addr="127.0.0.1",
        server_cloud_notify_status_path="/notify",
        server_cloud_port=5000,
        cloud_notification_period_in_secs=10,
        mqtt_wifi_status_notification_period_in_secs=10,
        mqtt_wifi_status_relays_topic="/topic",
        server_port=5000,
    )

    # THEN
    assert orchestrator.rpi_cloud_ip_addr == "127.0.0.1"
    assert orchestrator.server_cloud_notify_status_path == "/notify"
    assert orchestrator.server_cloud_port == 5000
    assert orchestrator.cloud_notification_period_in_secs == 10
    assert orchestrator.mqtt_wifi_status_notification_period_in_secs == 10
    assert orchestrator.mqtt_wifi_status_relays_topic == "/topic"
    assert orchestrator.server_port == 5000
    orchestrator.schedule_notifications.assert_called_once()


def test_notify_cloud_server_success(orchestrator_notifier, relays_status_off, mock_socket):
    # GIVEN
    bands_status = [
        WifiBandStatus(band="2.4GHz", status="Up"),
        WifiBandStatus(band="5GHz", status="Down"),
        WifiBandStatus(band="6GHz", status="Up"),
    ]

    orchestrator_notifier.rpi_cloud_ip_addr = "127.0.0.1"
    orchestrator_notifier.server_cloud_port = 5000
    orchestrator_notifier.server_cloud_notify_status_path = "/notify"
    orchestrator_notifier.server_port = 5000
    orchestrator_notifier.http_post_in_dedicated_thread = MagicMock()
    mock_socket.return_value.getsockname.return_value = ("192.168.1.100", 0)

    # WHEN
    orchestrator_notifier.notify_cloud_server(bands_status, "Test Situation", relays_status_off)

    # THEN
    orchestrator_notifier.http_post_in_dedicated_thread.assert_called_once()
    data = orchestrator_notifier.http_post_in_dedicated_thread.call_args.kwargs["data"]
    assert data["orquestrator_base_url"] == "http://192.168.1.100:5000/api/"
    assert data["wifi_status"] is True
    assert data["band_2GHz_status"] is True
    assert data["band_5GHz_status"] is False
    assert data["band_6GHz_status"] is True
    assert data["po0_status"] is False
    assert data["po1_status"] is False
    assert data["po2_status"] is False


def test_notify_cloud_server_no_bands(orchestrator_notifier, relays_status_off, mock_socket):
    # GIVEN
    bands_status = []
    orchestrator_notifier.rpi_cloud_ip_addr = "127.0.0.1"
    orchestrator_notifier.server_cloud_port = 5000
    orchestrator_notifier.server_cloud_notify_status_path = "/notify"
    orchestrator_notifier.http_post_in_dedicated_thread = MagicMock()
    mock_socket.return_value.getsockname.return_value = ("192.168.1.100", 0)

    # WHEN
    orchestrator_notifier.notify_cloud_server(bands_status, "Test Situation", relays_status_off)

    # THEN
    orchestrator_notifier.http_post_in_dedicated_thread.assert_called_once()
    data = orchestrator_notifier.http_post_in_dedicated_thread.call_args.kwargs["data"]
    assert data["wifi_status"] is False
    assert data["band_2GHz_status"] is False
    assert data["band_5GHz_status"] is False
    assert data["band_6GHz_status"] is False
    assert data["po0_status"] is False
    assert data["po1_status"] is False
    assert data["po2_status"] is False


def test_notify_cloud_server_error_handling(orchestrator_notifier, relays_status_off, mock_socket):
    # GIVEN
    bands_status = [
        WifiBandStatus(band="2.4GHz", status="Up"),
        WifiBandStatus(band="5GHz", status="Down"),
        WifiBandStatus(band="6GHz", status="Up"),
    ]
    orchestrator_notifier.rpi_cloud_ip_addr = "127.0.0.1"
    orchestrator_notifier.server_cloud_port = 5000
    orchestrator_notifier.server_cloud_notify_status_path = "/notify"
    orchestrator_notifier.http_post_in_dedicated_thread = MagicMock()
    mock_socket.side_effect = Exception("Socket error")

    # WHEN
    orchestrator_notifier.notify_cloud_server(bands_status, "Test Situation", relays_status_off)

    # THEN
    data = orchestrator_notifier.http_post_in_dedicated_thread.call_args.kwargs["data"]
    assert data["wifi_status"] is True
    assert data["band_2GHz_status"] is True
    assert data["band_5GHz_status"] is False
    assert data["band_6GHz_status"] is True
    assert data["po0_status"] is False
    assert data["po1_status"] is False
    assert data["po2_status"] is False


def test_schedule_notifications(orchestrator_notifier):
    # GIVEN
    cloud_notification_period = 5
    mqtt_notification_period = 1
    orchestrator_notifier.cloud_notification_period_in_secs = cloud_notification_period
    orchestrator_notifier.mqtt_wifi_status_notification_period_in_secs = mqtt_notification_period

    with patch(
        "server.orchestrator.notification.service.CloudServerNotifier"
    ) as mock_cloud_notifier, patch(
        "server.orchestrator.notification.service.MqttWifiStatusNotifier"
    ) as mock_mqtt_notifier:

        # WHEN
        orchestrator_notifier.schedule_notifications()

        # THEN
        mock_cloud_notifier.assert_called_once_with(
            cloud_notification_period_in_secs=cloud_notification_period
        )
        mock_mqtt_notifier.assert_called_once_with(
            mqtt_notification_period_in_secs=mqtt_notification_period
        )
        mock_cloud_notifier().start.assert_called_once()
        mock_mqtt_notifier().start.assert_called_once()


def test_http_post_success(orchestrator_notifier, mock_http):
    # GIVEN
    url = "127.0.0.1"
    port = 5000
    endpoint = "/notify"
    data = {"key": "value"}
    encoded_data = "key=value"

    # GIVEN
    mock_conn = MagicMock()
    mock_http.return_value = mock_conn
    mock_response = MagicMock(status=200, reason="OK")
    mock_conn.getresponse.return_value = mock_response

    # WHEN
    orchestrator_notifier.http_post(url, port, endpoint, data)

    # THEN
    mock_http.assert_called_once_with(url, port, timeout=POST_TIMEOUT_IN_SECS)
    mock_conn.request.assert_called_once_with(
        "POST",
        endpoint,
        body=encoded_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    mock_conn.getresponse.assert_called_once()


def test_http_post_failure(orchestrator_notifier, mock_http):
    # GIVEN
    url = "127.0.0.1"
    port = 5000
    endpoint = "/notify"
    data = {"key": "value"}
    encoded_data = "key=value"

    mock_conn = MagicMock()
    mock_http.return_value = mock_conn
    mock_response = MagicMock(status=500, reason="Internal Server Error")
    mock_conn.getresponse.return_value = mock_response

    # WHEN
    orchestrator_notifier.http_post(url, port, endpoint, data)

    # THEN
    mock_conn.request.assert_called_once_with(
        "POST",
        endpoint,
        body=encoded_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    mock_conn.getresponse.assert_called_once()


def test_http_post_exception(orchestrator_notifier, mock_http):
    # GIVEN
    url = "127.0.0.1"
    port = 5000
    endpoint = "/notify"
    data = {"key": "value"}
    mock_http.side_effect = Exception("Connection error")

    # WHEN
    with patch("server.orchestrator.notification.service.logger.error") as mock_logger_error:
        orchestrator_notifier.http_post(url, port, endpoint, data)

        # THEN
        mock_logger_error.assert_called_once_with("Error when posting to rpi cloud")


def test_http_post_in_dedicated_thread(orchestrator_notifier, mock_threading):
    # GIVEN
    url = "127.0.0.1"
    port = 5000
    endpoint = "/notify"
    data = {"wifi_status": True}
    timeout = 2

    # WHEN
    orchestrator_notifier.http_post_in_dedicated_thread(url, port, endpoint, data, timeout)

    # THEN
    mock_threading.Thread.assert_called_once()
    target_fn = mock_threading.Thread.call_args.kwargs["target"]
    thread_args = mock_threading.Thread.call_args.kwargs["args"]
    thread_name = mock_threading.Thread.call_args.kwargs["name"]
    assert target_fn == orchestrator_notifier.http_post
    assert thread_args == [url, port, endpoint, data, timeout]
    assert thread_name == "NotificationHttpPost"
    mock_threading.Thread().start.assert_called_once()


def test_notify_wifi_status_mqtt_success(orchestrator_notifier, mock_services, wifi_status_on):
    # GIVEN
    test_topic = "test/topic"
    orchestrator_notifier.mqtt_wifi_status_relays_topic = test_topic
    _, _, _, _, mock_mqtt_manager_service = mock_services

    expected_relays_statuses = RelaysStatus(
        relay_statuses=[
            MagicMock(relay_number=0, status=True, powered=True),
            MagicMock(relay_number=1, status=True, powered=True),
            MagicMock(relay_number=2, status=True, powered=True),
            MagicMock(relay_number=3, status=False, powered=False),
            MagicMock(relay_number=4, status=False, powered=False),
            MagicMock(relay_number=5, status=False, powered=False),
        ],
        command=True,
        timestamp=datetime.now(),
    )

    # WHEN
    orchestrator_notifier.notify_wifi_status_mqtt(wifi_status_on.bands_status)

    # THEN
    mock_mqtt_manager_service.publish_message.assert_called_once_with(
        topic=test_topic,
        message=expected_relays_statuses,
    )


def test_notify_wifi_status_mqtt_failure(orchestrator_notifier, mock_services, wifi_status_on):
    # GIVEN
    test_topic = "test/topic"
    orchestrator_notifier.mqtt_wifi_status_relays_topic = test_topic
    _, _, _, _, mock_mqtt_manager_service = mock_services
    expected_relays_statuses = RelaysStatus(
        relay_statuses=[
            MagicMock(relay_number=0, status=True, powered=True),
            MagicMock(relay_number=1, status=True, powered=True),
            MagicMock(relay_number=2, status=True, powered=True),
            MagicMock(relay_number=3, status=False, powered=False),
            MagicMock(relay_number=4, status=False, powered=False),
            MagicMock(relay_number=5, status=False, powered=False),
        ],
        command=True,
        timestamp=datetime.now(),
    )

    mock_mqtt_manager_service.publish_message.side_effect = Exception("Publish error")
    with patch("server.orchestrator.notification.service.logger") as mock_logger:
        # WHEN
        orchestrator_notifier.notify_wifi_status_mqtt(wifi_status_on.bands_status)

        # THEN
        mock_mqtt_manager_service.publish_message.assert_called_once_with(
            topic=test_topic,
            message=expected_relays_statuses,
        )
        assert mock_logger.error.call_count == 2
