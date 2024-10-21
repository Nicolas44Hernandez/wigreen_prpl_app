import logging
from datetime import datetime, timedelta
from typing import Callable
import time
from socket import error as socket_error
from socket import timeout as socket_timeout
import paho.mqtt.client as mqtt
from .model import Msg, serialize, deserialize

logger = logging.getLogger(__name__)

MSG_PUBLISH_TIMEOUT_IN_SECS = 5


class MQTTClient:
    """Service class for MQTT client"""

    def __init__(
        self,
        broker_address: str,
        username: str,
        password: str = None,
        subscriptions: dict = {},
        qos: int = 1,
        reconnection_timeout_in_secs: int = 5,
        max_reconnection_attemps: int = 5,
        publish_timeout_in_secs: int = 1,
    ):
        uid = str(time.time_ns())
        self.username = f"{username}_{uid}"
        self.broker_address = broker_address
        self.password = password
        self.subscriptions = subscriptions
        self.qos = qos
        self.msg_ack = False
        self._callbacks = {}
        self.connected = False
        self.reconnection_timeout_in_secs = reconnection_timeout_in_secs
        self.max_reconnection_attemps = max_reconnection_attemps
        self.publish_timeout_in_secs = publish_timeout_in_secs

        self._client = mqtt.Client(self.username)
        if password:
            self._client.username_pw_set(username=self.username, password=self.password)

        def on_connect(client, userdata, flags, rc, qos=1):
            """When cnnection is established"""

            logger.info("MQTT Client connection established")
            if len(self.subscriptions) > 0:
                for topic, callback in self.subscriptions.items():
                    self.subscribe(topic, callback, qos)
                    logger.info(f"Subscribed to topic: {topic} qos: {qos}")
            self.connected = True

        def on_disconnect(client, userdata, reasonCode):
            """Stop reading and notify upon disconnecting"""

            logger.info("MQTT Client disconnected")
            self.connected = False
            self.loop_stop()

        def on_subscribe(client, userdata, mid, granted_qos):
            """Notify upon subscription"""

            logger.info("Subscription done garanted_qos: " + str(granted_qos))

        def on_message(client, userdata, message):
            """Notify upon message reception"""

            logger.info(f"Message received on topic {message.topic}")
            logger.debug(f"   mid : {message.mid}")
            logger.debug(f"   duplicated : {message.dup}")
            logger.debug(f"   qos : {message.qos}")
            callback = self._callbacks[message.topic]
            if callback:
                try:
                    msg = deserialize(message.payload)
                    logger.info(f"Message : {str(msg)}")
                    callback(msg)
                except Exception:
                    logger.error("Message processing failed")
                    raise

        def on_publish(client, userdata, mid):
            """Notify upon publishing message on queue"""

            logger.debug("Message puback received for message mid: %s", str(mid))
            self.msg_ack = True

        self._client.on_connect = on_connect
        self._client.on_disconnect = on_disconnect
        self._client.on_subscribe = on_subscribe
        self._client.on_message = on_message
        self._client.on_publish = on_publish

    def connect(self, remaining_attempts: int) -> bool:
        """Connect to broker, retry if connection unsuccessful"""
        if remaining_attempts > 0:
            try:
                self._client.connect(self.broker_address)
                time.sleep(1)
                return True
            except (socket_error, socket_timeout):
                self.connected = False
                logger.error("Connection to broker unsuccessful")
                logger.info("Retrying connection ...")
                time.sleep(self.reconnection_timeout_in_secs)
                return self.connect(remaining_attempts - 1)
        else:
            return False

    def disconnect(self):
        """Send disconnection message to broker"""

        logger.info("Disconnect from broker")
        self._client.disconnect()

    def publish(self, topic: str, message: Msg, qos=1) -> bool:
        """
        Try to publish a message to the broker, if error in publish launch reconnection
        """

        logger.info(f"Publish on topic {topic}  message: {str(message)}")
        message_publish_info = self._client.publish(topic, serialize(message), qos)
        logger.debug("trying to publish message mid: %s", str(message_publish_info.mid))
        
        # set max msg wait for publish timmer
        now = datetime.now()
        msg_publish_timeout = now + timedelta(seconds=MSG_PUBLISH_TIMEOUT_IN_SECS)

        # Waiting loop
        while not self.msg_ack and now < msg_publish_timeout:
            time.sleep(0.2)
            now = datetime.now()
        self.msg_ack = False
        if not message_publish_info._published:
            logger.error(f"The message mid: {message_publish_info.mid} could not be published")
            logger.error(f"Launching reconnection procedure")
            if self.connect(self.max_reconnection_attemps):
                logger.error(f"Succefully reconnected")
                return self.publish(topic, message)
            else:
                logger.error(f"Reconnection imposible, message not published")
                return False
        return True

    def subscribe(self, topic: str, callback: Callable[[Msg], None], qos=1):
        """Subscribe to a topic"""

        logger.info(f"Subscribe to topic {topic}")
        if self.connected:
            self._callbacks[topic] = callback
            self._client.subscribe(topic, qos)
            self.subscriptions[topic] = callback
            return True
        else:
            logger.info(f"Impossible to subscribe to topic, MQTT interface not connected")
            if self.connect(self.max_reconnection_attemps):
                logger.error(f"Succefully reconnected")
                self._client.subscribe(topic, qos)
                self.subscriptions[topic] = callback
                return True
            else:
                logger.error(f"Reconnection imposible not subscribed")
                return False

    def loop_forever(self):
        """Run loop forever"""

        logger.info("Run infinite loop")
        self._client.loop_forever()

    def loop_start(self):
        """Run loop in dedicated thread"""

        logger.info("Start loop in dedicated thread")
        return self._client.loop_start()

    def loop_stop(self):
        """Stop running loop"""

        logger.info("Stop loop")
        return self._client.loop_stop()
