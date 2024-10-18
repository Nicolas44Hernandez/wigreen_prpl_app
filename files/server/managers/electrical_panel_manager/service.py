import logging
from flask import Flask
from server.managers.mqtt_manager import mqtt_manager_service
from datetime import datetime
from server.interfaces.mqtt_interface import RelaysStatus
from server.common import ServerBoxException, ErrorCode

logger = logging.getLogger(__name__)


class ElectricalPanelManager:
    """Manager for connected electrical panel"""

    mqtt_command_relays_topic: str
    mqtt_relays_status_topic: str
    last_relays_status_received: RelaysStatus = None

    def __init__(self, app: Flask = None) -> None:
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Initialize ElectricalPanelManager"""
        if app is not None:
            logger.info("initializing the ElectricalPanelManager")
            # Initialize configuration
            self.mqtt_command_relays_topic = app.config["MQTT"]["TOPICS"]["MQTT_COMMAND_RELAYS_TOPIC"]  
            self.mqtt_relays_status_topic = app.config["MQTT"]["TOPICS"]["MQTT_RELAYS_STATUS_TOPIC"]
            self.last_relays_status_received = None

            # Subscribe to relays command MQTT topic
            mqtt_manager_service.subscribe_to_topic(
                topic=self.mqtt_relays_status_topic,
                callback=self.receive_relays_statuses,
            )

    def get_relays_last_received_status(self):
        """retrieve relays last received status and timestamp"""
        if self.last_relays_status_received is None:
            logger.error(f"The relays status have not been received yet")
            raise ServerBoxException(ErrorCode.RELAYS_STATUS_NOT_RECEIVED)
        return self.last_relays_status_received

    def get_single_relay_last_received_status(self, relay_number: int):
        """get single relay last received status"""

        if relay_number not in range(0, 6):
            raise ServerBoxException(ErrorCode.INVALID_RELAY_NUMBER)

        if self.last_relays_status_received is None:
            raise ServerBoxException(ErrorCode.RELAYS_STATUS_NOT_RECEIVED)

        for relay_status in self.last_relays_status_received.relay_statuses:
            if relay_status.relay_number == relay_number:
                return relay_status
        raise ServerBoxException(ErrorCode.RELAYS_STATUS_NOT_RECEIVED)

    def receive_relays_statuses(self, relays_status: RelaysStatus):
        """Callback for relays/status topic"""
        logger.info(f"Relays status received")
        logger.info(f"{relays_status.to_json()}")

        # Update relays last status received
        relays_status.timestamp = datetime.now()
        self.last_relays_status_received = relays_status

    def publish_mqtt_relays_status_command(self, relays_status: RelaysStatus):
        """publish MQTT relays status command"""

        logger.debug(f"Publishing relays status command")
        mqtt_manager_service.publish_message(
            topic=self.mqtt_command_relays_topic, message=relays_status
        )


electrical_panel_manager_service: ElectricalPanelManager = ElectricalPanelManager()
""" Electrical panel manager service singleton"""
