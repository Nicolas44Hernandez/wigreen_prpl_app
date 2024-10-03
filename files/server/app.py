""" App initialization module."""

import logging
from logging.config import dictConfig
from os import path
import yaml
from flask import Flask
from flask_restful import Api

# Managers
from server.managers.wifi_bands_manager import wifi_bands_manager_service

# Rest APIs
api = Api()
from server.rest_api.wifi_controler import WifiStatusApi

logger = logging.getLogger(__name__)


def create_app(
    config_dir: str = path.join(path.dirname(path.abspath(__file__)), "config"),
):
    """Create the Flask app"""

    # Create app Flask
    app = Flask("Orange Orchestrator")

    # Get configuration files    
    app_config = path.join(config_dir, "general-config.yml")
    logging_config = path.join(config_dir, "logging-config.yml")

    logger.info("App config file: %s", app_config)
    logger.info("Logging config file: %s", logging_config)

    # Load configuration
    app.config.from_file(app_config, load=yaml.full_load)

    # Load logging configuration and configure flask application logger
    with open(logging_config) as stream:
        dictConfig(yaml.full_load(stream))

    # Register extensions
    register_extensions(app)
    # Register REST APIs
    register_apis(app)

    logger.info("App ready!!")

    return app


def register_extensions(app: Flask):
    """Initialize all extensions"""

    api.init_app(app)
    # Wifi bands manager extension
    wifi_bands_manager_service.init_app(app=app)
    

def register_apis(app: Flask):
    """Store App APIs blueprints."""
    api = Api(app)
    
    # Register REST blueprints
    api.add_resource(WifiStatusApi, '/wifi/status')
