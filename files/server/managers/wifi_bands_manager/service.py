"""Wifi Bands manager"""

import logging
from flask import Flask
from server.interfaces.amx_usp_interface import AmxUspInterface


logger = logging.getLogger(__name__)

BANDS = ["2.4GHz", "5GHz", "6GHz"]

class WifiBandsManager:
    """Manager for wifi control"""

    amx_usp_interface: AmxUspInterface

    def __init__(self, app: Flask = None) -> None:
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Initialize WifiBandsManager"""
        if app is not None:
            logger.info("initializing the WifiBandsManager")
            # Initialize configuration
            self.amx_usp_interface = AmxUspInterface()

    def get_band_status(self, band: str):
        """Execute get wifi band status command in the livebox using AMX USP """
        # Check if band number exists
        #TODO: Validate if band doensnt exists
        logger.info("Getting wifi status - Device.WiFi.Radio.1.Status")
        status = self.amx_usp_interface.read_object(path="Device.WiFi.Radio.1.Status")
        logger.info(f"status: {status}")
        return status
        


wifi_bands_manager_service: WifiBandsManager = WifiBandsManager()
""" Wifi manager service singleton"""
