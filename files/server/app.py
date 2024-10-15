""" App initialization module."""

import logging
from logging.config import dictConfig
from os import path
import json
from flask import Flask
# Managers
from server.managers.wifi_bands_manager import wifi_bands_manager_service

# Rest APIs
from server.rest_api.wifi_controller import bp as wifi_controller_bp

logger = logging.getLogger(__name__)


def create_app(
    config_dir: str = path.join(path.dirname(path.abspath(__file__)), "config"),
):
    """Create the Flask app"""

    # Create app Flask
    app = Flask("Orange Orchestrator")

    # Get configuration files    
    app_config = path.join(config_dir, "general-config.json")
    logging_config = path.join(config_dir, "logging-config.json")

    logger.info("App config file: %s", app_config)
    logger.info("Logging config file: %s", logging_config)

    # Load app configuration
    with open(app_config) as config_file:
        config = json.load(config_file)
        app.config.update(config)

    # Load logging configuration and configure flask application logger
    with open(logging_config, 'r') as config_file:
        config = json.load(config_file)
        dictConfig(config)

    # Register extensions
    register_extensions(app)
    # Register REST APIs
    register_apis(app)

    logger.info("App ready!!")

    return app


def register_extensions(app: Flask):
    """Initialize all extensions"""
    # Wifi bands manager extension
    wifi_bands_manager_service.init_app(app=app)
    

def register_apis(app: Flask):
    """Store App APIs blueprints."""
    # Register REST blueprints
    app.register_blueprint(wifi_controller_bp, url_prefix='/api/wifi')