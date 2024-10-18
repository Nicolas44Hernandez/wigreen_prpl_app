""" REST controller for relays management ressource """
import logging
from flask import Blueprint, jsonify, request
from datetime import datetime
from flask.views import MethodView
from server.managers.electrical_panel_manager import electrical_panel_manager_service
#from .rest_model import SingleRelayStatusSchema, RelaysStatusResponseSchema, RelaysStatusQuerySchema
from server.common import ServerBoxException, ErrorCode

from server.interfaces.mqtt_interface import SingleRelayStatus, RelaysStatus


RELAYS = ["relay_0", "relay_1", "relay_2", "relay_3", "relay_4", "relay_5"]

logger = logging.getLogger(__name__)

bp = Blueprint("electrical_panel", __name__)


class RelaysStatusApi(MethodView):
    """API to retrieve or set electrical panel status"""

    def get(self):
        """Get relays status"""

        logger.info(f"GET api/electrical_panel/status")

        # Call electrical panel manager service to get relays status
        relays_status = electrical_panel_manager_service.get_relays_last_received_status()

        return relays_status.to_json()


class SingleRelayStatusApi(MethodView):
    """API to retrieve single relay status"""
    
    def get(self):
        """Get single relay status"""
        # Retrieve query args
        try:
            relay = request.args.get('relay')
            logger.info(f"GET rapi/electrical_panel/status relay:{relay}")
        except Exception:
            raise ServerBoxException(ErrorCode.ERROR_IN_REQUEST_ARGS) 
        if relay is None:
            raise ServerBoxException(ErrorCode.ERROR_IN_REQUEST_ARGS) 

        # Call electrical panel manager service to get relay status
        relay_status =  electrical_panel_manager_service.get_single_relay_last_received_status(int(relay))
        return relay_status.to_json()
