import logging
from flask import Blueprint, jsonify, request
from flask.views import MethodView
from server.managers.wifi_bands_manager import wifi_bands_manager_service 
from server.common import ServerBoxException, ErrorCode

logger = logging.getLogger(__name__)

bp = Blueprint("wifi", __name__)

class WifiStatusApi(MethodView):
    """API to retrieve wifi general status"""
    def get(self):
        """Get livebox wifi status"""
        logger.info(f"GET api/wifi/status")
        status = wifi_bands_manager_service.get_wifi_status()
        return jsonify({"status": status}) , 200
    
class WifiBandStatusApi(MethodView):
    """API to retrieve wifi band status"""
    def get(self):
        """Get livebox wifi status"""
        logger.info(f"GET api/wifi/band/status")
        # Retrieve query parameters
        try:
            band = request.args.get('band')
        except Exception:
            raise ServerBoxException(ErrorCode.ERROR_IN_PARAMETER_IN_REQUEST) 
        status = wifi_bands_manager_service.get_band_status(band=band)
        return jsonify({"status": status}) , 200