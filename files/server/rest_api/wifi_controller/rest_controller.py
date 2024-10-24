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
        return jsonify({"status": status}), 200

    def post(self):
        """Update wifi status"""
        # Retrieve query args
        new_status = request.args.get("status")
        if new_status is None:
            raise ServerBoxException(ErrorCode.ERROR_IN_REQUEST_ARGS)

        # Set band status
        new_wifi_status = wifi_bands_manager_service.set_wifi_status(new_status=new_status)
        return jsonify({"status": new_wifi_status}), 200


class WifiBandStatusApi(MethodView):
    """API to retrieve wifi band status"""

    def get(self):
        """Get livebox wifi status"""
        logger.info(f"GET api/wifi/band/status")
        # Retrieve query args
        band = request.args.get("band")
        if band is None:
            raise ServerBoxException(ErrorCode.ERROR_IN_REQUEST_ARGS)
        status = wifi_bands_manager_service.get_band_status(band=band)
        return jsonify({"status": status}), 200

    def post(self):
        """Update wifi band status"""
        # Retrieve query args
        band = request.args.get("band")
        new_status = request.args.get("status")
        if band is None or new_status is None:
            raise ServerBoxException(ErrorCode.ERROR_IN_REQUEST_ARGS)

        # Set band status
        new_band_status = wifi_bands_manager_service.set_band_status(
            band=band, new_status=new_status
        )
        return jsonify({"status": new_band_status}), 200
