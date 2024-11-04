""" REST controller for orchestrator use situation management ressource """

import logging
from flask import Blueprint, jsonify, request
from datetime import datetime
from flask.views import MethodView
from server.orchestrator.use_situations import orchestrator_use_situations_service
from server.common import ServerBoxException, ErrorCode

logger = logging.getLogger(__name__)

bp = Blueprint("use_situations", __name__)


class UseSituationsListApi(MethodView):
    """API to retrieve the available current situations"""

    def get(self):
        """Get use situation list"""
        logger.info(f"GET api/use_situations/")
        use_situations = orchestrator_use_situations_service.get_use_situation_list()
        return {"use_situations": use_situations}


class UseSituationsApi(MethodView):
    """API to retrieve and change current use situation"""

    def get(self):
        """Get current use situation"""
        logger.info(f"GET api/use_situations/current")
        current_use_situation = orchestrator_use_situations_service.get_current_use_situation()
        return {"use_situation": current_use_situation}

    def post(self):
        """
        Set current use situation
        """
        logger.info(f"POST api/use_situations/current")
        # Retrieve query args
        new_use_situation_from_query = request.args.get("use_situation", default=None)
        if new_use_situation_from_query is None:
            raise ServerBoxException(ErrorCode.ERROR_IN_REQUEST_ARGS)

        logger.info(f"Setting use situation: {new_use_situation_from_query}")
        orchestrator_use_situations_service.set_use_situation(
            use_situation=new_use_situation_from_query
        )

        return {"use_situation": new_use_situation_from_query}
