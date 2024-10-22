import logging
import time
from flask import Flask
from server.interfaces.mqtt_interface import mqtt_client_interface

logger = logging.getLogger(__name__)


class MQTTManager:
    """Manager for MQTT service"""

    mqtt_client: mqtt_client_interface
    broker_address: str
    username: str
    password: str
    qos: int
    reconnection_timeout_in_secs: int
    max_reconnection_attemps: int
    publish_timeout_in_secs: int

    def __init__(self, app: Flask = None) -> None:
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Initialize MQTTManager"""
        if app is not None:
            logger.info("initializing the MQTTManager")
            # Initialize configuration
            self.broker_address = app.config["MQTT"]["BASIC"]["MQTT_BROKER_ADDRESS"]
            self.username = app.config["MQTT"]["BASIC"]["MQTT_USERNAME"]
            self.password = app.config["MQTT"]["BASIC"]["MQTT_PASSWORD"]
            self.qos = app.config["MQTT"]["BASIC"]["MQTT_QOS"]
            self.reconnection_timeout_in_secs = app.config["MQTT"]["BASIC"][
                "MQTT_RECONNECTION_TIMEOUT_IN_SEG"
            ]
            self.max_reconnection_attemps = app.config["MQTT"]["BASIC"][
                "MQTT_MAX_RECONNECTION_ATTEMPS"
            ]
            self.publish_timeout_in_secs = app.config["MQTT"]["BASIC"][
                "MQTT_MSG_PUBLISH_TIMEOUT_IN_SECS"
            ]

            # Connect to MQTT broker
            self.init_mqtt_service()

    def subscribe_to_topic(self, topic: str, callback: callable):
        """Subscribe to MQTT topic"""
        return self.mqtt_client.subscribe(topic=topic, callback=callback)

    def publish_message(self, topic: str, message: str) -> bool:
        """Publish message to topic"""
        return self.mqtt_client.publish(topic=topic, message=message)

    def init_mqtt_service(self):
        """Connect to MQTT broker"""

        self.mqtt_client = mqtt_client_interface(
            broker_address=self.broker_address,
            username=self.username,
            password=self.password,
            reconnection_timeout_in_secs=self.reconnection_timeout_in_secs,
            max_reconnection_attemps=self.max_reconnection_attemps,
            publish_timeout_in_secs=self.publish_timeout_in_secs,
        )
        if self.mqtt_client.connect(self.max_reconnection_attemps):
            self.mqtt_client.loop_start()
            time.sleep(5)
        else:
            logger.error("Impossible to connect to MQTT broker")


mqtt_manager_service: MQTTManager = MQTTManager()
""" MQTT service singleton"""
