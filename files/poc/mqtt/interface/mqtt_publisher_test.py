import os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

from server.interfaces.mqtt_interface import (
    mqtt_client_interface,
    SingleRelayStatus,
    RelaysStatus,
)
import time

HOST = "localhost"
CLIENT_NAME = "publisher_test"
CLIENT_PASSWORD = "lamp"

# TOPIC = "status/relays"
TOPIC = "command/relays"

STATUS_ALL_OFF = [
    SingleRelayStatus(relay_number=0, status=False, powered=False),
    SingleRelayStatus(relay_number=1, status=False, powered=False),
    SingleRelayStatus(relay_number=2, status=False, powered=False),
    SingleRelayStatus(relay_number=3, status=False, powered=False),
    SingleRelayStatus(relay_number=4, status=False, powered=False),
    SingleRelayStatus(relay_number=5, status=False, powered=False),
]

STATUS_ALL_ON = [
    SingleRelayStatus(relay_number=0, status=True, powered=False),
    SingleRelayStatus(relay_number=1, status=True, powered=False),
    SingleRelayStatus(relay_number=2, status=True, powered=False),
    SingleRelayStatus(relay_number=3, status=True, powered=False),
    SingleRelayStatus(relay_number=4, status=True, powered=False),
    SingleRelayStatus(relay_number=5, status=True, powered=False),
]

STATUS_0 = [
    SingleRelayStatus(relay_number=0, status=False, powered=False),
    SingleRelayStatus(relay_number=1, status=True, powered=False),
    SingleRelayStatus(relay_number=2, status=False, powered=False),
    SingleRelayStatus(relay_number=3, status=True, powered=False),
    SingleRelayStatus(relay_number=4, status=False, powered=False),
    SingleRelayStatus(relay_number=5, status=True, powered=False),
]

STATUS_1 = [
    SingleRelayStatus(relay_number=0, status=False, powered=False),
    SingleRelayStatus(relay_number=1, status=True, powered=False),
    SingleRelayStatus(relay_number=2, status=False, powered=False),
]

STATUS_2 = [
    SingleRelayStatus(relay_number=1, status=False, powered=False),
    SingleRelayStatus(relay_number=2, status=True, powered=False),
]

STATUS_3 = [
    SingleRelayStatus(relay_number=2, status=True, powered=False),
    SingleRelayStatus(relay_number=1, status=False, powered=False),
    SingleRelayStatus(relay_number=3, status=False, powered=False),
]

STATUS_4 = [
    SingleRelayStatus(relay_number=3, status=False, powered=False),
    SingleRelayStatus(relay_number=1, status=False, powered=False),
    SingleRelayStatus(relay_number=4, status=True, powered=False),
]

STATUS_5 = [
    SingleRelayStatus(relay_number=4, status=True, powered=False),
    SingleRelayStatus(relay_number=5, status=True, powered=False),
]

STATUS_LIST = [
    STATUS_ALL_OFF,
    STATUS_ALL_ON,
    STATUS_ALL_OFF,
    STATUS_0,
    STATUS_1,
    STATUS_2,
    STATUS_3,
    STATUS_4,
    STATUS_5,
]


def get_relay_command_message():
    relays_statuses = STATUS_ALL_OFF

    return RelaysStatus(relay_statuses=relays_statuses, command=True)


mqtt_client = mqtt_client_interface(
    broker_address=HOST, username=CLIENT_NAME, password=CLIENT_PASSWORD
)
mqtt_client.connect(5)
mqtt_client.loop_start()

try:
    while True:
        for relays_statuses in STATUS_LIST:
            msg = RelaysStatus(relay_statuses=relays_statuses, command=True)
            print(f"Sending message: {msg}")
            mqtt_client.publish(TOPIC, msg)
            print(f"Msg published \n")
            time.sleep(1)

except KeyboardInterrupt:  # Trap a CTRL+C keyboard interrupt
    mqtt_client.disconnect()
