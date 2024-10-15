import logging
from flask import Blueprint, jsonify
from flask.views import MethodView
from server.managers.wifi_bands_manager import wifi_bands_manager_service 

logger = logging.getLogger(__name__)

bp = Blueprint("wifi", __name__)

class WifiStatusApi(MethodView):
    """API to retrieve wifi general status"""
    def get(self):
        """Get livebox wifi status"""
        logger.info(f"GET wifi/")
        status = wifi_bands_manager_service.get_band_status(band="5GHz")
        return jsonify({"status": status}) , 200