import pytest
from flask import Flask
from server.common import ServerBoxException, handle_server_box_exception
from server.rest_api.wifi_controller.rest_controller import bp as wifi_controller_bp
from server.rest_api.mqtt_controller.rest_controller import bp as mqtt_controller_bp
from server.rest_api.electrical_panel_controller.rest_controller import (
    bp as electrical_panel_controller_bp,
)
from server.rest_api.use_situations_controller.rest_controller import (
    bp as use_situations_controller_bp,
)


@pytest.fixture
def app_with_bp():
    """Create a Flask app for testing."""
    app = Flask(__name__)
    app.register_error_handler(ServerBoxException, handle_server_box_exception)
    app.register_blueprint(mqtt_controller_bp, url_prefix="/api")
    app.register_blueprint(wifi_controller_bp, url_prefix="/api")
    app.register_blueprint(electrical_panel_controller_bp, url_prefix="/api")
    app.register_blueprint(use_situations_controller_bp, url_prefix="/api")

    return app


@pytest.fixture
def client(app_with_bp):
    """Create a test client."""
    return app_with_bp.test_client()
