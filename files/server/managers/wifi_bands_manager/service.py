"""Wifi Bands manager"""

import logging
import json
import time
from datetime import datetime, timedelta
from flask import Flask
from server.interfaces.amx_usp_interface import AmxUspInterface
from server.common import ServerBoxException, ErrorCode

logger = logging.getLogger(__name__)

BANDS = ["2.4GHz", "5GHz", "6GHz"]
STATUSES = ["Up", "Down"]
STATUS_CHANGE_TIMEOUT_IN_SECS = 15


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
        with open(datamodel_json_file, "r") as config_file:
            try:
                self.datamodel = json.load(config_file)
            except Exception as exc:
                raise ServerBoxException(ErrorCode.DATAMODEL_FILE_ERROR)

    def get_band_status(self, band: str):
        """Execute get wifi band status command in the livebox using AMX USP"""
        # Check if band number exists
        if band not in BANDS:
            raise ServerBoxException(ErrorCode.UNKNOWN_BAND_WIFI)
        path = self.datamodel[band]["STATUS"]
        logger.info(f"Getting wifi band {band} status -  path:{path}")
        ret = self.amx_usp_interface.read_object(path=path)
        logger.info(f"Value: {ret}")
        try:
            status = ret[0][list(ret[0].keys())[0]]["Status"]
        except Exception as e:
            logger.error(e)
            raise ServerBoxException(ErrorCode.UNEXPECTED_ERROR)
        logger.info(f"status: {status}")
        return status

    def get_wifi_status(self):
        """Get WiFi status using AMX USP"""
        for band in BANDS:
            band_status = self.get_band_status(band=band)
            if "Up" in band_status:
                return "Up"
        return "Down"

    def set_band_status(self, band: str, new_status: str):
        """Execute set wifi band status command in the livebox using AMX USP"""
        # Check if band number exists
        if band not in BANDS:
            raise ServerBoxException(ErrorCode.UNKNOWN_BAND_WIFI)

        # Check if status exists
        if new_status not in STATUSES:
            raise ServerBoxException(ErrorCode.UNKNOWN_WIFI_STATUS)

        # check if requested status is already satisfied
        current_band_status = self.get_band_status(band)
        if current_band_status is None:
            logger.error("Error when getting band status")
            return None
        if current_band_status == new_status:
            return current_band_status

        # Retrieve path and params
        path = self.datamodel[band][new_status]["PATH"]
        params = self.datamodel[band][new_status]["PARAMS"]
        # Set wifi band status
        logger.info(f"Setting wifi band {band} status to {new_status}")
        ret = self.amx_usp_interface.set_object(path=path, params=params)
        logger.info(f"Response: {ret}")
        time.sleep(2)

        # set max duration timmer
        now = datetime.now()
        status_change_timeout = now + timedelta(seconds=STATUS_CHANGE_TIMEOUT_IN_SECS)

        # Waiting loop
        while now < status_change_timeout:
            current_band_status = self.get_band_status(band)
            if current_band_status == new_status:
                logger.error(f"NEw band status: {current_band_status}")
                return current_band_status
            time.sleep(0.3)
            now = datetime.now()
        logger.error(f"Wifi status change is taking too long, verify wifi status")
        return None

    def set_wifi_status(self, new_status: str):
        """Set WiFi status using AMX USP"""

        # Check if status exists
        if new_status not in STATUSES:
            raise ServerBoxException(ErrorCode.UNKNOWN_WIFI_STATUS)

        for band in BANDS:
            self.set_band_status(band=band, new_status=new_status)

        return new_status


wifi_bands_manager_service: WifiBandsManager = WifiBandsManager()
""" Wifi manager service singleton"""
