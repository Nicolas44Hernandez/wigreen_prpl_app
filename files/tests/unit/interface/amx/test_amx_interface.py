from server.interfaces.amx_usp_interface import AmxUspInterface
import os


def test_interface_dev():
    """Test for create interface in development environement"""
    # GIVEN
    os.environ["FLASK_ENV"] = "DEVELOPMENT"

    # WHEN
    interface = AmxUspInterface()
    interface.read_object(path="test")
    interface.set_object(path="test", params={"test": "test"})
    interface.add_object(path="test", params={"test": "test"})
    interface.del_object(path="test")

    # THEN
    assert type(interface) == AmxUspInterface
