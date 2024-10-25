import logging
import threading
import time
from server.managers.wifi_bands_manager import wifi_bands_manager_service

logger = logging.getLogger(__name__)


class WifiStatusPoller:
    def __init__(self, wifi_status_polling_period_in_secs):
        self.period = wifi_status_polling_period_in_secs
        self._stop_event = threading.Event()

    def poll_wifi_status(self):
        while not self._stop_event.is_set():
            # Retrieve wifi status
            logger.info("Polling wifi status")
            wifi_bands_manager_service.update_wifi_status_attribute()
            logger.info(f"Polling wifi done")

            time.sleep(self.period)

    def start(self):
        self.thread = threading.Thread(target=self.poll_wifi_status, name="OrchestratorPoller-WiFi")
        self.thread.start()

    def stop(self):
        self._stop_event.set()
        self.thread.join()


class OrchestratorPolling:
    """OrchestratorPolling service"""

    # Attributes
    wifi_status_polling_period_in_secs: int

    def init_polling_module(
        self,
        wifi_status_polling_period_in_secs: int,
    ):
        """Initialize the polling service for the orchestrator"""
        logger.info("initializing Orchestrator polling module")

        self.wifi_status_polling_period_in_secs = wifi_status_polling_period_in_secs

        # Schedule ressources polling
        self.schedule_resources_status_polling()

    def schedule_resources_status_polling(self):
        """Schedule the resources polling"""

        # Declare pollers
        wifi_status_poller = WifiStatusPoller(
            wifi_status_polling_period_in_secs=self.wifi_status_polling_period_in_secs
        )
        wifi_status_poller.start()


orchestrator_polling_service: OrchestratorPolling = OrchestratorPolling()
""" OrchestratorPolling service singleton"""
