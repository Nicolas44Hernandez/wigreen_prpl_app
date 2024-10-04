import logging
from flask_restful import Resource
from flask_apispec import doc
from flask_apispec.views import MethodResource
from server.managers.wifi_bands_manager import wifi_bands_manager_service  # Adjust the import as needed

logger = logging.getLogger(__name__)

class WifiStatusApi(MethodResource, Resource):
    """API to retrieve wifi general status"""

    @doc(description='Get livebox wifi status', responses={200: {'description': 'Successful response'}})
    def get(self):
        """Get livebox wifi status"""
        logger.info("GET wifi/")
        status = wifi_bands_manager_service.get_band_status(band="5GHz")
        return {"status": status}, 200