"""REST API Wifi controller package"""
from .rest_controller import bp, WifiStatusApi

bp.add_url_rule('/status', view_func=WifiStatusApi.as_view('wifi_api'))
