import logging
import socket
import http.client
import urllib.parse
import time
import threading
from datetime import datetime
from typing import Iterable
from server.managers.wifi_bands_manager import wifi_bands_manager_service, BANDS
from server.managers.electrical_panel_manager import electrical_panel_manager_service
from server.managers.wifi_bands_manager.model import WifiBandStatus
from server.managers.mqtt_manager import mqtt_manager_service
from server.interfaces.mqtt_interface import RelaysStatus, SingleRelayStatus

logger = logging.getLogger(__name__)

POST_TIMEOUT_IN_SECS = 2


class CloudServerNotifier:
    def __init__(self, cloud_notification_period_in_secs):
        self.period = cloud_notification_period_in_secs
        self._stop_event = threading.Event()

    def post_cloud_notification(self):
        wifi_bands_manager_service.update_wifi_status_attribute()
        while not self._stop_event.is_set():
            # Retreiving values
            wifi_status = wifi_bands_manager_service.get_current_wifi_status()
            try:
                relays_statuses = electrical_panel_manager_service.get_relays_last_received_status()
            except:
                relays_statuses = None
            # Sending cloud notification
            logger.info("Sending cloud notification ...")
            orchestrator_notification_service.notify_cloud_server(
                bands_status=wifi_status.bands_status,
                use_situation="TODO",
                relay_statuses=relays_statuses,
            )
            time.sleep(self.period)

    def start(self):
        self.thread = threading.Thread(
            target=self.post_cloud_notification, name="OrchestratorCloudNotifier"
        )
        self.thread.start()

    def stop(self):
        self._stop_event.set()
        self.thread.join()


class MqttWifiStatusNotifier:
    def __init__(self, mqtt_notification_period_in_secs):
        self.period = mqtt_notification_period_in_secs
        self._stop_event = threading.Event()

    def publish_mqtt_notification(self):
        while not self._stop_event.is_set():
            # Retreiving values
            wifi_status = wifi_bands_manager_service.get_current_wifi_status()
            if wifi_status is not None:
                # Publish MQTT notification
                logger.info("Publish wifi status notification to MQTT ...")
                logger.debug(f"Wifi status: {wifi_status}")
                orchestrator_notification_service.notify_wifi_status_mqtt(
                    bands_status=wifi_status.bands_status
                )
            time.sleep(self.period)

    def start(self):
        self.thread = threading.Thread(
            target=self.publish_mqtt_notification, name="OrchestratorMqttWiFiStatusNotifier"
        )
        self.thread.start()

    def stop(self):
        self._stop_event.set()
        self.thread.join()


class OrchestratorNotification:
    """OrchestratorNotification service"""

    server_cloud_notify_status_path: str
    rpi_cloud_ip_addr: str
    server_cloud_port: int
    cloud_notification_period_in_secs: int

    def init_notification_module(
        self,
        rpi_cloud_ip_addr: str,
        server_cloud_notify_status_path: str,
        server_cloud_port: int,
        cloud_notification_period_in_secs: int,
        mqtt_wifi_status_relays_topic: str,
        mqtt_wifi_status_notification_period_in_secs: int,
    ):
        """Initialize the polling service for the orchestrator"""
        logger.info("initializing Orchestrator polling module")

        self.rpi_cloud_ip_addr = rpi_cloud_ip_addr
        self.server_cloud_notify_status_path = server_cloud_notify_status_path
        self.server_cloud_port = server_cloud_port
        self.cloud_notification_period_in_secs = cloud_notification_period_in_secs
        self.mqtt_wifi_status_relays_topic = mqtt_wifi_status_relays_topic
        self.mqtt_wifi_status_notification_period_in_secs = (
            mqtt_wifi_status_notification_period_in_secs
        )

        # Schedule notifications
        self.schedule_notifications()

    def schedule_notifications(self):
        """Schedule the notifications"""

        # Declare notifiers
        cloud_notifier = CloudServerNotifier(
            cloud_notification_period_in_secs=self.cloud_notification_period_in_secs
        )
        mqtt_wifi_status_notifier = MqttWifiStatusNotifier(
            mqtt_notification_period_in_secs=self.mqtt_wifi_status_notification_period_in_secs
        )
        # Start notifiers
        cloud_notifier.start()
        mqtt_wifi_status_notifier.start()

    def notify_cloud_server(
        self,
        bands_status: Iterable[WifiBandStatus],
        use_situation: str,
        relay_statuses: RelaysStatus,
    ):
        """Notify current wifi status and use situation to cloud server"""

        logger.info("Posting HTTP to notify current wifi status and use situation to RPI cloud")

        # connected_to_internet = wifi_bands_manager_service.is_connected_to_internet()
        # if connected_to_internet:
        # TODO: Reactivate
        if True:
            logger.info("Connected to internet!!")
            # Get wifi status from bands status
            wifi_status = False
            band_status_2GHz = False
            band_status_5GHz = False
            band_status_6GHz = False

            for band_status in bands_status:
                if band_status.band == "2.4GHz":
                    band_status_2GHz = True if band_status.status == "Up" else False
                elif band_status.band == "5GHz":
                    band_status_5GHz = True if band_status.status == "Up" else False
                elif band_status.band == "6GHz":
                    band_status_6GHz = True if band_status.status == "Up" else False
                if band_status.status:
                    wifi_status = True

            # Get electrical panel power outlet status
            po0_status = False
            po1_status = False
            po2_status = False
            po0_powered = False
            po1_powered = False
            po2_powered = False
            if relay_statuses is not None:
                for relay_status in relay_statuses.relay_statuses:
                    if relay_status.relay_number == 0:
                        po0_status = relay_status.status
                        po0_powered = relay_status.powered
                    if relay_status.relay_number == 1:
                        po1_status = relay_status.status
                        po1_powered = relay_status.powered
                    if relay_status.relay_number == 2:
                        po2_status = relay_status.status
                        po2_powered = relay_status.powered

            # Get Orchestrator ip address
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("192.168.1.122", 80))
                orchestrator_ip_addr = s.getsockname()[0]
                orquestrator_base_url = f"http://{orchestrator_ip_addr}:5000/"
                s.close()
            except:
                logger.error("Error retreiving orchestrator IP")
                orquestrator_base_url = ""

            # TODO: update data with data modules
            data = {
                "orquestrator_base_url": orquestrator_base_url,
                "wifi_status": wifi_status,
                "band_2GHz_status": band_status_2GHz,
                "band_5GHz_status": band_status_5GHz,
                "band_6GHz_status": band_status_6GHz,
                "use_situation": use_situation,
                "energy_limitations": "100%",
                "alimelo_busvoltage": "0",
                "alimelo_shuntvoltage": "0",
                "alimelo_loadvoltage": "0",
                "alimelo_current_mA": "0",
                "alimelo_power_mW": "0",
                "alimelo_battery_level": "0",
                "alimelo_power_supplied": "0",
                "alimelo_is_powered_by_battery": "0",
                "alimelo_is_charging": "0",
                "po0_status": po0_status,
                "po0_powered": po0_powered,
                "po1_status": po1_status,
                "po1_powered": po1_powered,
                "po2_status": po2_status,
                "po2_powered": po2_powered,
                "power_strip_relay1_status": True,
                "power_strip_relay2_status": True,
                "power_strip_relay3_status": True,
                "power_strip_relay4_status": True,
            }

            self.http_post_in_dedicated_thread(
                url=self.rpi_cloud_ip_addr,
                port=self.server_cloud_port,
                endpoint=self.server_cloud_notify_status_path,
                data=data,
            )
        else:
            logger.error(f"Imposible to post notification, box is disconnected from internet")

    def http_post(
        self, url: str, port: int, endpoint: str, data: dict, timeout: int = POST_TIMEOUT_IN_SECS
    ):
        """HTTP Post"""
        try:
            # Encode the data
            encoded_data = urllib.parse.urlencode(data)
            # Create a connection
            logger.info(f"Connecting to url:{url} port:{port}")
            conn = http.client.HTTPConnection(url, port, timeout=timeout)
            # Make the headers
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            # Make the post request
            conn.request("POST", endpoint, body=encoded_data, headers=headers)
            # Get the response
            response = conn.getresponse()
            logger.info(f"Server response status: {response.status}")
            if response.status != 200:
                logger.error(
                    f"Error when posting to rpi cloud: {response.status} - {response.reason}"
                )
        except Exception:
            logger.error(f"Error when posting to rpi cloud")

    def http_post_in_dedicated_thread(
        self, url: str, port: int, endpoint: str, data: dict, timeout: int = POST_TIMEOUT_IN_SECS
    ):
        """HTTP Post in dedicated thread"""

        post_thread = threading.Thread(
            target=self.http_post,
            args=[url, port, endpoint, data, timeout],
            name="NotificationHttpPost",
        )
        post_thread.start()

    def notify_wifi_status_mqtt(self, bands_status: Iterable[WifiBandStatus]):
        """Send MQTT command to electrical pannel to represent the wifi bands status"""

        logger.info("Sending MQTT message to notify wifi status")

        # Build relays command
        relays_statuses_in_command = []
        for i in range(6):
            relays_statuses_in_command.append(
                SingleRelayStatus(relay_number=i, status=False, powered=False)
            )

        for i, band in enumerate(BANDS):
            for band_status in bands_status:
                if band_status.band == band:
                    relays_statuses_in_command[i].status = band_status.status
                    relays_statuses_in_command[i].powered = band_status.status
                    break

        relays_statuses = RelaysStatus(
            relay_statuses=relays_statuses_in_command,
            command=True,
            timestamp=datetime.now(),
        )

        # Call MQTT manager service to publish relays status command
        try:
            mqtt_manager_service.publish_message(
                topic=self.mqtt_wifi_status_relays_topic, message=relays_statuses
            )

        except Exception as e:
            logger.error("Error publishing wifi status")
            logger.error(e)


orchestrator_notification_service: OrchestratorNotification = OrchestratorNotification()
""" OrchestratorNotification service singleton"""
