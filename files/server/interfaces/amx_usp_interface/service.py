"""AMX USP interface package"""

import logging
import os
import json
from server.common import ServerBoxException, ErrorCode

flask_env = os.getenv("FLASK_ENV")
if flask_env == "PRODUCTION":
    import pamx

logger = logging.getLogger(__name__)


class AmxUspClient:
    """Service class for AmxUsp interface"""

    def __init__(self):
        logger.info("initializing the AmxUspClient")
        if flask_env == "PRODUCTION":
            try:
                pamx.backend.load("/usr/bin/mods/usp/mod-amxb-usp.so")
                pamx.backend.set_config({})
                self.connection = pamx.bus.connect(
                    "usp:/var/run/usp/endpoint_agent_path"
                )
            except Exception:
                raise ServerBoxException(ErrorCode.USP_LOAD_ERROR)

    # Python AMX functions : get/set/add/delete
    def read_object(self, path: str):
        """Read USP Object"""
        logger.info(f"AMX USP Read object: {path}")
        if flask_env == "PRODUCTION":
            try:
                return self.connection.get(path)
            except Exception:
                raise ServerBoxException(ErrorCode.USP_ERROR)

    def set_object(self, path: str, params: dict):
        """Set USP Object"""
        logger.info(f"AMX USP Set object: {path}  params: {params}")
        if flask_env == "PRODUCTION":
            try:
                return self.connection.set(path, params)
            except Exception:
                raise ServerBoxException(ErrorCode.USP_ERROR)

    def add_object(self, path, params: dict):
        """Add USP Object"""
        logger.info(f"AMX USP Add object: {path}  params: {params}")
        if flask_env == "PRODUCTION":
            try:
                return self.connection.add(path, params)
            except Exception:
                raise ServerBoxException(ErrorCode.USP_ERROR)

    def del_object(self, path: str):
        """Delete USP Object"""
        logger.info(f"AMX USP Delete object: {path}")
        if flask_env == "PRODUCTION":
            try:
                return self.connection.delete(path)
            except Exception:
                raise ServerBoxException(ErrorCode.USP_ERROR)
