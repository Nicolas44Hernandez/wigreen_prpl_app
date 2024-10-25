"""REST API Wifi controller package"""

from .rest_controller import bp, WifiStatusApi, WifiBandStatusApi

bp.add_url_rule("/status", view_func=WifiStatusApi.as_view("wifi_api"))
bp.add_url_rule("/band/status", view_func=WifiBandStatusApi.as_view("wifi_band_api"))
