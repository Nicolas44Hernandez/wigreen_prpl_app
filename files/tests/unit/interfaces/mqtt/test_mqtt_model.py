from datetime import datetime
import ast
from server.interfaces.mqtt_interface import SingleRelayStatus, RelaysStatus
from server.interfaces.mqtt_interface.model import serialize, deserialize


class MsgPiblishInfo:
    def __init__(self, published, qos=1, topic="topic", payload='{"msg":"msg"}'):
        self._published = published
        self.mid = 1
        self.dup = "dup"
        self.qos = qos
        self.topic = topic
        self.payload = payload


RELAYS_STATUS = [
    SingleRelayStatus(relay_number=0, status=False, powered=False),
    SingleRelayStatus(relay_number=1, status=False, powered=False),
    SingleRelayStatus(relay_number=2, status=False, powered=False),
    SingleRelayStatus(relay_number=3, status=False, powered=False),
    SingleRelayStatus(relay_number=4, status=False, powered=False),
    SingleRelayStatus(relay_number=5, status=False, powered=False),
]


def test_relays_status_to_str():
    """Test for relays status to str"""
    # GIVEN
    relays_status = RelaysStatus(relay_statuses=RELAYS_STATUS, command=True)
    relays_status.timestamp = datetime(2024, 10, 24, 10, 12, 54, 566714)

    # WHEN
    ret = relays_status.__str__()

    # THEN
    assert (
        ret
        == "{'relay_statuses': [\"{'relay_number': 0, 'status': False, 'powered': False}\", \"{'relay_number': 1, 'status': False, 'powered': False}\", \"{'relay_number': 2, 'status': False, 'powered': False}\", \"{'relay_number': 3, 'status': False, 'powered': False}\", \"{'relay_number': 4, 'status': False, 'powered': False}\", \"{'relay_number': 5, 'status': False, 'powered': False}\"], 'timestamp': '2024-10-24T10:12:54.566714', 'command': True}"
    )


def test_relays_status_to_json():
    """Test relays status to json"""
    # GIVEN
    relays_status = RelaysStatus(relay_statuses=RELAYS_STATUS, command=True)

    # WHEN
    ret = relays_status.to_json()

    # THEN
    assert ret["command"]
    assert ret["relay_statuses"][0] == {"relay_number": 0, "status": False, "powered": False}
    assert ret["relay_statuses"][1] == {"relay_number": 1, "status": False, "powered": False}
    assert ret["relay_statuses"][2] == {"relay_number": 2, "status": False, "powered": False}
    assert ret["relay_statuses"][3] == {"relay_number": 3, "status": False, "powered": False}
    assert ret["relay_statuses"][4] == {"relay_number": 4, "status": False, "powered": False}
    assert ret["relay_statuses"][5] == {"relay_number": 5, "status": False, "powered": False}


def test_relays_status_from_json():
    """Test relays status from json"""
    # GIVEN
    relays_status_json = {
        "timestamp": "2024-10-24T10:12:54.566714",
        "relay_statuses": [
            {"relay_number": 0, "status": False, "powered": False},
            {"relay_number": 1, "status": False, "powered": False},
            {"relay_number": 2, "status": False, "powered": False},
            {"relay_number": 3, "status": False, "powered": False},
            {"relay_number": 4, "status": False, "powered": False},
            {"relay_number": 5, "status": False, "powered": False},
        ],
        "command": True,
    }
    # WHEN
    ret = RelaysStatus.from_json(relays_status_json)

    # THEN
    assert type(ret) == RelaysStatus
    assert ret.relay_statuses == RELAYS_STATUS
    assert ret.timestamp == datetime(2024, 10, 24, 10, 12, 54, 566714)


def test_serialize_dict():
    """Test serialize from dict"""
    # GIVEN
    msg = {
        "field1": 1,
        "field2": 2,
    }

    # WHEN
    ret = serialize(msg)

    # THEN
    assert ret == '{"field1": 1, "field2": 2}'


def test_serialize_instance():
    """Test serialize from obj"""
    # GIVEN
    msg = RelaysStatus(relay_statuses=RELAYS_STATUS, command=True)
    msg.timestamp = datetime(2024, 10, 24, 10, 12, 54, 566714)

    # WHEN
    ret = serialize(msg)

    # THEN
    assert (
        ret
        == '{"relay_statuses": [{"relay_number": 0, "status": false, "powered": false}, {"relay_number": 1, "status": false, "powered": false}, {"relay_number": 2, "status": false, "powered": false}, {"relay_number": 3, "status": false, "powered": false}, {"relay_number": 4, "status": false, "powered": false}, {"relay_number": 5, "status": false, "powered": false}], "timestamp": "2024-10-24T10:12:54.566714", "command": true}'
    )


def test_deserialize_from_str_instance():
    """Test serialize from str RelaysStatus instance"""
    # GIVEN
    msg = '{"relay_statuses": [{"relay_number": 0, "status": false, "powered": false}, {"relay_number": 1, "status": false, "powered": false}, {"relay_number": 2, "status": false, "powered": false}, {"relay_number": 3, "status": false, "powered": false}, {"relay_number": 4, "status": false, "powered": false}, {"relay_number": 5, "status": false, "powered": false}], "timestamp": "2024-10-24T10:12:54.566714", "command": true}'

    # WHEN
    ret = deserialize(msg)

    # THEN
    assert type(ret) == RelaysStatus
    assert ret.relay_statuses == RELAYS_STATUS
    assert ret.timestamp == datetime(2024, 10, 24, 10, 12, 54, 566714)


def test_deserialize_from_str_dict():
    """Test serialize from str"""
    # GIVEN
    msg = '{"field1": 1, "field2": 2}'

    # WHEN
    ret = deserialize(msg)

    # THEN
    assert type(ret) == dict
    assert ret["field1"] == 1
    assert ret["field2"] == 2
