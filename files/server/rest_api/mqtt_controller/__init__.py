"""REST API MQTT controller package"""

from .rest_controller import bp, MQTTMessageApi

bp.add_url_rule("/msg", view_func=MQTTMessageApi.as_view("mqtt_api"))
