""" REST controller for wifi bands management ressource """
import logging
from flask.views import MethodView
from flask_smorest import Blueprint
from server.managers.wifi_bands_manager import wifi_bands_manager_service


logger = logging.getLogger(__name__)

bp = Blueprint("wifi", __name__, url_prefix="/wifi")
""" The api blueprint. Should be registered in app main api object """


@bp.route("/")
class WifiStatusApi(MethodView):
    """API to retrieve wifi general status"""
    @bp.doc(
        security=[{"tokenAuth": []}],
        responses={400: "BAD_REQUEST", 404: "NOT_FOUND"},
    )
    @bp.response(status_code=200)
    def get(self):
        """Get livebox wifi status"""
        logger.info(f"GET wifi/")
        status = wifi_bands_manager_service.get_band_status(band="5GHz")
        return {"status": status}