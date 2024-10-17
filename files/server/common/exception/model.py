"""The module which gathers all custom exceptions"""

from .code import ErrorCode


class ServerBoxException(Exception):
    """Unique functional exception"""

    code: int
    """
    An integer coding the error type.
    This is given to caller so he can translate them if required.
    """
    http_code: int
    """ The http code which must be used for the error"""
    message: str
    """A short string that describes the error."""

    def __init__(self, code: ErrorCode, message_detailed: str = None) -> None:
        """Default constructor for ServerBoxException exception"""
        super().__init__(code)
        self.code = code.value
        self.http_code = code.http_code
        self.message = code.message
        if message_detailed:
            self.message += ": " + message_detailed
