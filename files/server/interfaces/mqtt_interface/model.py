"""
MQTT messages model
"""

from datetime import datetime
from typing import Iterable, TypeVar
import json

Msg = TypeVar("Msg")


def serialize(msg: Msg) -> bytes:
    """serialize MQTT message"""
    if type(msg) is dict:
        data_to_send = msg
    else:
        data_to_send = msg.to_json()
    return json.dumps(data_to_send)


def deserialize(payload: bytes) -> Msg:
    """deserialize MQTT message"""
    # TODO: review for other messages
    data = json.loads(payload)
    if "relay_statuses" in data:
        return RelaysStatus.from_json(data)
    else:
        return data


class SingleRelayStatus:
    def __init__(self, relay_number: int, status: bool, powered: bool):
        self.relay_number = relay_number
        self.status = status
        self.powered = powered

    def __str__(self):
        """String representation of the SingleRelayStatus instance"""
        return "{}".format(
            {"relay_number": self.relay_number, "status": self.status, "powered": self.powered}
        )

    def to_json(self):
        """Return json dict that represents the SingleRelayStatus instance"""
        return {"relay_number": self.relay_number, "status": self.status, "powered": self.powered}

    def from_json(dictionary: dict):
        """Return SingleRelayStatus instance from json dict"""
        return SingleRelayStatus(
            relay_number=dictionary["relay_number"],
            status=dictionary["status"],
            powered=dictionary["powered"],
        )


class RelaysStatus:
    def __init__(
        self, relay_statuses: Iterable[SingleRelayStatus], command: bool, timestamp: datetime = None
    ):
        self.relay_statuses = relay_statuses
        self.command = command
        self.timestamp = datetime.now() if timestamp is None else timestamp

    def __str__(self):
        """String representation of the RelaysStatus instance"""
        return "{}".format(
            {
                "relay_statuses": [str(relay_status) for relay_status in self.relay_statuses],
                "timestamp": self.timestamp.isoformat(),
                "command": self.command,
            },
        )

    def to_json(self):
        """Return json dict that represents the RelaysStatus instance"""
        return {
            "relay_statuses": [relay_status.to_json() for relay_status in self.relay_statuses],
            "timestamp": self.timestamp.isoformat(),
            "command": self.command,
        }

    def from_json(dictionary: dict):
        """Return RelaysStatus instance from json dict"""
        return RelaysStatus(
            relay_statuses=[
                SingleRelayStatus.from_json(single_relay_dict)
                for single_relay_dict in dictionary["relay_statuses"]
            ],
            command=dictionary["command"],
            timestamp=datetime.fromisoformat(dictionary["timestamp"]),
        )
