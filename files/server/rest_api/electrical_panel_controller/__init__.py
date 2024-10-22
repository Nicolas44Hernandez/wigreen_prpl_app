"""REST API Wifi controller package"""

from .rest_controller import bp, RelaysStatusApi, SingleRelayStatusApi

bp.add_url_rule("/status", view_func=RelaysStatusApi.as_view("electrical_pannel_api"))
bp.add_url_rule(
    "/relay/status", view_func=SingleRelayStatusApi.as_view("single_relay_api")
)
