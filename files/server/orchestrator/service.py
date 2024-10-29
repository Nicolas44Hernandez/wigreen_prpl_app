import logging
from flask import Flask
from server.orchestrator.polling import orchestrator_polling_service
from server.orchestrator.notification import orchestrator_notification_service

logger = logging.getLogger(__name__)


class Orchestrator:
    """Orchestrator service"""

    def __init__(self, app: Flask = None) -> None:
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Initialize Orchestrator"""
        if app is not None:
            logger.info("initializing Orchestrator")

            # Init notification module
            orchestrator_notification_service.init_notification_module(
                rpi_cloud_ip_addr=app.config["CLOUD"]["SERVER_IP"],
                server_cloud_notify_status_path=app.config["CLOUD"]["PATHS"]["NOTIFY_STATUS"],
                server_cloud_port=app.config["CLOUD"]["PORT"],
                cloud_notification_period_in_secs=app.config["NOTIFICATION"]["CLOUD_SECS"],
                mqtt_wifi_status_relays_topic=app.config["MQTT"]["TOPICS"][
                    "MQTT_WIFI_STATUS_RELAYS_TOPIC"
                ],
                mqtt_wifi_status_notification_period_in_secs=app.config["NOTIFICATION"][
                    "MQTT_WIFI_STATUS_SECS"
                ],
            )

            # Init ressources polling module
            orchestrator_polling_service.init_polling_module(
                wifi_status_polling_period_in_secs=app.config["POLLING"]["WIFI_STATUS_SECS"]
            )


orchestrator_service: Orchestrator = Orchestrator()
""" Orchestrator service singleton"""
