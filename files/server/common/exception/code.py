""" Server box errors """

from enum import Enum


class ErrorCode(Enum):
    """Enumerate which gather all data about possible errors"""

    # Please enrich this enumeration in order to handle other kind of errors
    UNEXPECTED_ERROR = (0, 500, "Unexpected error occurs")
    USP_LOAD_ERROR = (1, 500, "Error when loading USP agent")
    USP_ERROR = (2, 500, "Error in USP agent")
    DATAMODEL_FILE_ERROR = (
        3,
        500,
        "Error in Datamodel configuration load, check file",
    )
    UNKNOWN_BAND_WIFI = (4, 400, "Wifi band doesnt exist") 
    ERROR_IN_PARAMETER_IN_REQUEST = (5, 400, "Error in request parameters")    

    # pylint: disable=unused-argument
    def __new__(cls, *args, **kwds):
        """Custom new in order to initialize properties"""
        obj = object.__new__(cls)
        obj._value_ = args[0]
        obj._http_code_ = args[1]
        obj._message_ = args[2]
        return obj

    @property
    def http_code(self):
        """The http code corresponding to the error"""
        return self._http_code_

    @property
    def message(self):
        """The message corresponding to the error"""
        return self._message_
