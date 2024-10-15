import logging
from flask import Blueprint, jsonify
from flask.views import MethodView
from server.managers.mqtt_manager import mqtt_manager_service 

logger = logging.getLogger(__name__)

bp = Blueprint("mqtt", __name__)

class MQTTMessageApi(MethodView):
    """API to retrieve wifi general status"""
    def get(self):
        """Send message to MQTT broker"""

        logger.info(f"GET mqtt/local")
        mqtt_manager_service.publish_message(
            topic="command/relays", message={"data":"relays_status_test"}
        )
        return jsonify({"done": True}) , 200