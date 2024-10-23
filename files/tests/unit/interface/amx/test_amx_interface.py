import os
import pytest
from server.interfaces.amx_usp_interface import AmxUspInterface
from server.common import ServerBoxException, ErrorCode
from pytest_mock import MockerFixture
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_pamx(mocker: MockerFixture):

    fake_pamx = MagicMock()
    fake_pamx.backend.load = MagicMock()
    fake_pamx.backend.set_config = MagicMock()
    fake_pamx.bus.connect = MagicMock()
    return mocker.patch("server.interfaces.amx_usp_interface.service.pamx", new=fake_pamx)


def test_interface_dev():
    """Test for create interface in development environement"""
    # WHEN
    interface = AmxUspInterface()
    interface.read_object(path="test")
    interface.set_object(path="test", params={"test": "test"})
    interface.add_object(path="test", params={"test": "test"})
    interface.del_object(path="test")

    # THEN
    assert type(interface) == AmxUspInterface


def test_create_interface_prod(mock_pamx):
    """Test for create interface in production environement"""

    # WHEN
    interface = AmxUspInterface()

    # THEN
    assert type(interface) == AmxUspInterface
    mock_pamx.backend.load.assert_called_with("/usr/bin/mods/usp/mod-amxb-usp.so")
    mock_pamx.backend.set_config.assert_called_with({})
    mock_pamx.bus.connect.assert_called_with("usp:/var/run/usp/endpoint_agent_path")


def test_create_interface_prod_excepion(mock_pamx):
    """Test for set datamodel object in production environement
    An exeption is raised in .connect()"""

    # GIVEN
    mock_pamx.bus.connect.side_effect = Exception("An error occurred")

    # WHEN
    with pytest.raises(ServerBoxException) as exc_info:
        AmxUspInterface()

    # THEN
    mock_pamx.backend.load.assert_called_with("/usr/bin/mods/usp/mod-amxb-usp.so")
    mock_pamx.backend.set_config.assert_called_with({})
    mock_pamx.bus.connect.assert_called_with("usp:/var/run/usp/endpoint_agent_path")
    assert exc_info.value.code == ErrorCode.USP_LOAD_ERROR.value
    assert exc_info.value.message == ErrorCode.USP_LOAD_ERROR.message


def test_read_objet(mock_pamx):
    """Test for read datamodel object in production environement"""

    # GIVEN
    interface = AmxUspInterface()
    mock_pamx.bus.connect().get.return_value = "object"

    # WHEN
    ret = interface.read_object(path="datamodel.object")

    # THEN
    assert ret == "object"
    mock_pamx.bus.connect().get.assert_called_with("datamodel.object")


def test_set_objet(mock_pamx):
    """Test for set datamodel object in production environement"""

    # GIVEN
    interface = AmxUspInterface()
    mock_pamx.bus.connect().set.return_value = {"datamodel.object": "object"}

    # WHEN
    ret = interface.set_object(path="datamodel.object", params={"datamodel.object": "object"})

    # THEN
    assert ret == {"datamodel.object": "object"}
    mock_pamx.bus.connect().set.assert_called_with(
        "datamodel.object", {"datamodel.object": "object"}
    )


def test_add_objet(mock_pamx):
    """Test for add datamodel object in production environement"""

    # GIVEN
    interface = AmxUspInterface()
    mock_pamx.bus.connect().add.return_value = {"datamodel.new_object": "new_object"}

    # WHEN
    ret = interface.add_object(
        path="datamodel.new_object", params={"datamodel.new_object": "new_object"}
    )

    # THEN
    assert ret == {"datamodel.new_object": "new_object"}
    mock_pamx.bus.connect().add.assert_called_with(
        "datamodel.new_object", {"datamodel.new_object": "new_object"}
    )


def test_delete_objet(mock_pamx):
    """Test for delete datamodel object in production environement"""

    # GIVEN
    interface = AmxUspInterface()
    mock_pamx.bus.connect().delete.return_value = "deleted"

    # WHEN
    ret = interface.del_object(path="datamodel.object")

    # THEN
    assert ret == "deleted"
    mock_pamx.bus.connect().delete.assert_called_with("datamodel.object")


def test_read_objet_exception(mock_pamx):
    """Test for read datamodel object in production environement
    An exeption is raised in .get()"""

    # GIVEN
    interface = AmxUspInterface()
    mock_pamx.bus.connect().get.side_effect = Exception("An error occurred")

    # WHEN
    with pytest.raises(ServerBoxException) as exc_info:
        interface.read_object(path="datamodel.object")

    # THEN
    mock_pamx.bus.connect().get.assert_called_with("datamodel.object")
    assert exc_info.value.code == ErrorCode.USP_ERROR.value
    assert exc_info.value.message == ErrorCode.USP_ERROR.message


def test_set_objet_exception(mock_pamx):
    """Test for set datamodel object in production environement
    An exeption is raised in .set()"""

    # GIVEN
    interface = AmxUspInterface()
    mock_pamx.bus.connect().set.side_effect = Exception("An error occurred")

    # WHEN
    with pytest.raises(ServerBoxException) as exc_info:
        interface.set_object(path="datamodel.object", params={"datamodel.object": "object"})

    # THEN
    mock_pamx.bus.connect().set.assert_called_with(
        "datamodel.object", {"datamodel.object": "object"}
    )
    assert exc_info.value.code == ErrorCode.USP_ERROR.value
    assert exc_info.value.message == ErrorCode.USP_ERROR.message


def test_add_objet_exception(mock_pamx):
    """Test for add datamodel object in production environement
    An exeption is raised in .set()"""

    # GIVEN
    interface = AmxUspInterface()
    mock_pamx.bus.connect().add.side_effect = Exception("An error occurred")

    # WHEN
    with pytest.raises(ServerBoxException) as exc_info:
        interface.add_object(
            path="datamodel.new_object", params={"datamodel.new_object": "new_object"}
        )

    # THEN
    mock_pamx.bus.connect().add.assert_called_with(
        "datamodel.new_object", {"datamodel.new_object": "new_object"}
    )
    assert exc_info.value.code == ErrorCode.USP_ERROR.value
    assert exc_info.value.message == ErrorCode.USP_ERROR.message


def test_delete_objet_exception(mock_pamx):
    """Test for delete datamodel object in production environement
    An exeption is raised in .get()"""

    # GIVEN
    interface = AmxUspInterface()
    mock_pamx.bus.connect().delete.side_effect = Exception("An error occurred")

    # WHEN
    with pytest.raises(ServerBoxException) as exc_info:
        interface.del_object(path="datamodel.object")

    # THEN
    mock_pamx.bus.connect().delete.assert_called_with("datamodel.object")
    assert exc_info.value.code == ErrorCode.USP_ERROR.value
    assert exc_info.value.message == ErrorCode.USP_ERROR.message
