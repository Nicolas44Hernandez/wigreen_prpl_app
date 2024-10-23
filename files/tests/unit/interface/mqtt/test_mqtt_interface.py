import pytest
from server.interfaces.mqtt_interface import mqtt_client_interface
from unittest.mock import MagicMock
from socket import error as socket_error


class MsgPiblishInfo:
    def __init__(self, published, qos=1, topic="topic", payload='{"msg":"msg"}'):
        self._published = published
        self.mid = 1
        self.dup = "dup"
        self.qos = qos
        self.topic = topic
        self.payload = payload


@pytest.fixture
def mqtt_client():
    mqtt_client = mqtt_client_interface(
        broker_address="test.broker", username="username", password="pwd"
    )
    mqtt_client._client = MagicMock()  # Mock the MQTT client
    return mqtt_client


def test_create_interface():
    """Test for create interface"""
    # WHEN
    interface = mqtt_client_interface(broker_address="test.broker", username="username")

    # THEN
    assert type(interface) == mqtt_client_interface


def test_connect(mqtt_client, mock_sleep):
    """Test connect"""

    # WHEN
    mqtt_client.connect(remaining_attempts=3)

    # THEN
    mqtt_client._client.connect.assert_called_with("test.broker")


def test_connect_exception(mqtt_client, mock_sleep):
    """Test connect an exeption is raised"""
    # GIVEN
    mqtt_client._client.connect.side_effect = [socket_error(), True]

    # WHEN
    mqtt_client.connect(remaining_attempts=3)

    # THEN
    mqtt_client._client.connect.assert_called_with("test.broker")
    assert mqtt_client._client.connect.call_count == 2


def test_connect_no_remaining_attemps(mqtt_client, mock_sleep):
    """Test connect an exeption is raised, no remaning attemps"""
    # GIVEN
    mqtt_client._client.connect.side_effect = socket_error()

    # WHEN
    ret = mqtt_client.connect(remaining_attempts=2)

    # THEN
    assert not ret
    mqtt_client._client.connect.assert_called_with("test.broker")
    assert mqtt_client._client.connect.call_count == 2


def test_disconnect(mqtt_client, mock_sleep):
    """Test disconnect"""

    # WHEN
    mqtt_client.disconnect()

    # THEN
    mqtt_client._client.disconnect.assert_called()


def test_publish(mqtt_client, mock_sleep):
    """Test disconnect"""

    # WHEN
    mqtt_client.publish(topic="topic", message={"msg": "data"}, qos=1)

    # THEN
    mqtt_client._client.publish.assert_called_with("topic", '{"msg": "data"}', 1)


def test_publish_fail_reconnect_in_first_attemp(mqtt_client, mock_sleep):
    """Test disconnect"""

    # GIVEN
    mqtt_client._client.publish.side_effect = [MsgPiblishInfo(False), MsgPiblishInfo(True)]

    # WHEN
    mqtt_client.publish(topic="topic", message={"msg": "data"}, qos=1)

    # THEN
    mqtt_client._client.publish.assert_called_with("topic", '{"msg": "data"}', 1)
    mqtt_client._client.connect.assert_called_with("test.broker")


def test_publish_fail_reconnect(mqtt_client, mock_sleep):
    """Test disconnect"""

    # GIVEN
    mqtt_client._client.publish.return_value = MsgPiblishInfo(False)
    mqtt_client._client.connect.side_effect = socket_error()

    # WHEN
    mqtt_client.publish(topic="topic", message={"msg": "data"}, qos=1)

    # THEN
    mqtt_client._client.publish.assert_called_with("topic", '{"msg": "data"}', 1)
    mqtt_client._client.connect.assert_called_with("test.broker")
    mqtt_client._client.connect.call_count == 5


def test_subscribe(mqtt_client, mock_sleep):
    """Test subscribe"""

    # GIVEN
    mqtt_client.connected = True

    def callback_fn():
        pass

    # WHEN
    ret = mqtt_client.subscribe(topic="topic", callback=callback_fn)

    # THEN
    assert ret
    mqtt_client._client.subscribe.assert_called_with("topic", 1)


def test_subscribe_reconnection(mqtt_client, mock_sleep):
    """Test subscribe"""

    # GIVEN
    mqtt_client.connected = False

    def callback_fn():
        pass

    # WHEN
    ret = mqtt_client.subscribe(topic="topic", callback=callback_fn)

    # THEN
    assert ret
    mqtt_client._client.subscribe.assert_called_with("topic", 1)
    mqtt_client._client.connect.assert_called_with("test.broker")


def test_subscribe_reconnection_impossible(mqtt_client, mock_sleep):
    """Test subscribe reconnection impossible"""

    # GIVEN
    mqtt_client._client.connect.side_effect = socket_error()
    mqtt_client.connected = False

    def callback_fn():
        pass

    # WHEN
    ret = mqtt_client.subscribe(topic="topic", callback=callback_fn)

    # THEN
    assert not ret
    mqtt_client._client.subscribe.assert_not_called()
    mqtt_client._client.connect.assert_called_with("test.broker")
    mqtt_client._client.connect.call_count == 5


def test_loop_forever(mqtt_client, mock_sleep):
    """Test loop_forever"""

    # WHEN
    mqtt_client.loop_forever()

    # THEN
    mqtt_client._client.loop_forever.assert_called()


def test_loop_start(mqtt_client, mock_sleep):
    """Test loop_start"""

    # WHEN
    mqtt_client.loop_start()

    # THEN
    mqtt_client._client.loop_start.assert_called()


def test_loop_stop(mqtt_client, mock_sleep):
    """Test loop_stop"""

    # WHEN
    mqtt_client.loop_stop()

    # THEN
    mqtt_client._client.loop_stop.assert_called()


def test_on_connect(mqtt_client, mock_sleep):
    """Test on_connect"""

    # GIVEN
    fn = MagicMock()
    mqtt_client.subscriptions = {"topic": fn}

    # WHEN
    mqtt_client.on_connect("client", "userdata", "flags", "rc", qos=1)

    # THEN
    assert mqtt_client.connected == True
    mqtt_client._client.subscribe.assert_called_with("topic", 1)


def test_on_disconnect(mqtt_client, mock_sleep):
    """Test on_disconnect"""

    # WHEN
    mqtt_client.on_disconnect("client", "userdata", "reasonCode")

    # THEN
    assert not mqtt_client.connected
    mqtt_client._client.loop_stop.assert_called()


def test_on_subscribe(mqtt_client, mock_sleep):
    """Test on_subscribe"""
    # GIVEN
    mqtt_client.connected = True

    # WHEN
    mqtt_client.on_subscribe("client", "userdata", "mid", "granted_qos")

    # THEN
    assert mqtt_client.connected == True


def test_on_message(mqtt_client, mock_sleep):
    """Test on_message"""

    # GIVEN
    callback_fn = MagicMock()
    mqtt_client._callbacks = {"topic": callback_fn}
    msg = MsgPiblishInfo(published=True, qos=1, topic="topic", payload='{"msg":"msg"}')

    # WHEN
    mqtt_client.on_message("client", "userdata", msg)

    # THEN
    callback_fn.assert_called_with({"msg": "msg"})


def test_on_message_wrong_format(mqtt_client, mock_sleep):
    """Test on_message wrong message format"""

    # GIVEN
    callback_fn = MagicMock()
    mqtt_client._callbacks = {"topic": callback_fn}
    msg = MsgPiblishInfo(published=True, qos=1, topic="topic", payload="wrong_format")

    # WHEN
    mqtt_client.on_message("client", "userdata", msg)

    # THEN
    callback_fn.assert_not_called()


def test_on_publish(mqtt_client, mock_sleep):
    """Test on_publish"""

    # WHEN
    mqtt_client.on_publish("client", "userdata", "mid")

    # THEN
    assert mqtt_client.msg_ack == True
