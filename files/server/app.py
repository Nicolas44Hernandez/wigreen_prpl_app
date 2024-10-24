""" App initialization module."""

import logging
from logging.config import dictConfig
import os
import json
from flask import Flask

# Managers
from server.managers.wifi_bands_manager import wifi_bands_manager_service
from server.managers.mqtt_manager import mqtt_manager_service
from server.managers.electrical_panel_manager import electrical_panel_manager_service

# Rest APIs
from server.rest_api.wifi_controller import bp as wifi_controller_bp
from server.rest_api.electrical_panel_controller import (
    bp as electrical_panel_controller_bp,
)
from server.rest_api.mqtt_controller import bp as mqtt_controller_bp

# Common
from server.common import ServerBoxException, handle_server_box_exception


logger = logging.getLogger(__name__)


def create_app(
    config_dir: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config"),
):
    """Create the Flask app"""

    # Create app Flask
    app = Flask("Orange Orchestrator")

    # Get server configuration files
    if os.getenv("FLASK_ENV") == "DEVELOPMENT":
        app_config = os.path.join(config_dir, "general-config-development.json")
    else:
        app_config = os.path.join(config_dir, "general-config.json")

    # Get logging configuration file
    logging_config = os.path.join(config_dir, "logging-config.json")

    # Load app configuration
    with open(app_config) as config_file:
        config = json.load(config_file)
        app.config.update(config)

    # Load logging configuration and configure flask application logger
    with open(logging_config, "r") as config_file:
        config = json.load(config_file)
        dictConfig(config)

    logger.info("App config file: %s", app_config)
    logger.info("Logging config file: %s", logging_config)

    # Register extensions
    register_extensions(app)
    # Register REST APIs
    register_apis(app)

    logger.info("App ready!!")

    return app


def register_extensions(app: Flask):
    """Initialize all extensions"""
    # MQTT service
    mqtt_manager_service.init_app(app=app)
    # Wifi bands manager extension
    wifi_bands_manager_service.init_app(app=app)
    # Electrical panel manager extension
    electrical_panel_manager_service.init_app(app=app)


def register_apis(app: Flask):
    """Store App APIs blueprints."""
    # Register error handler
    app.register_error_handler(ServerBoxException, handle_server_box_exception)
    # Register REST blueprints
    app.register_blueprint(wifi_controller_bp, url_prefix="/api/wifi")
    app.register_blueprint(electrical_panel_controller_bp, url_prefix="/api/electrical_panel")
    app.register_blueprint(mqtt_controller_bp, url_prefix="/api/mqtt")
