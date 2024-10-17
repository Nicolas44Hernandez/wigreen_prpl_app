"""Wifi Bands manager"""

import logging
import json
from flask import Flask
from server.interfaces.amx_usp_interface import AmxUspInterface
from server.common import ServerBoxException, ErrorCode

logger = logging.getLogger(__name__)

BANDS = ["2.4GHz", "5GHz", "6GHz"]

class WifiBandsManager:
    """Manager for wifi control"""

    amx_usp_interface: AmxUspInterface
    datamodel: dict

    def __init__(self, app: Flask = None) -> None:
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Initialize WifiBandsManager"""
        if app is not None:
            logger.info("initializing the WifiBandsManager")
            # Initialize configuration
            self.amx_usp_interface = AmxUspInterface()
            # Load datamodel
            self.load_datamodel(app.config["WIFI_DATAMODEL_CONFIG_FILE"])
    
    def load_datamodel(self, datamodel_json_file: str):
        """Load the wifi datamodel dict from file"""
        logger.info("Livebox datamodel file: %s", datamodel_json_file)
        # Load configuration file
        with open(datamodel_json_file, 'r') as config_file:
            try:
                self.datamodel = json.load(config_file)
            except Exception as exc:
                raise ServerBoxException(ErrorCode.DATAMODEL_FILE_ERROR)

    def get_band_status(self, band: str):
        """Execute get wifi band status command in the livebox using AMX USP """
        # Check if band number exists
        if band not in BANDS:
            raise ServerBoxException(ErrorCode.UNKNOWN_BAND_WIFI)
        path = self.datamodel[band]["STATUS"]
        logger.info(f"Getting wifi band {band} status -  path:{path}")
        ret = self.amx_usp_interface.read_object(path=path)
        logger.info(f"Value: {ret}")
        status = ret[0][list(ret[0].keys())[0]]["Status"]
        logger.info(f"status: {status}")
        return status    

    def get_wifi_status(self):
        """Get WiFi status using AMX USP"""
        for band in BANDS:
            band_status = self.get_band_status(band=band)
            if band_status:
                return True
        return False      


wifi_bands_manager_service: WifiBandsManager = WifiBandsManager()
""" Wifi manager service singleton"""
