"""Data model for Wifi manager package"""
from dataclasses import dataclass
from typing import Iterable


@dataclass
class WifiBandStatus:
    """Model for wifi band status"""

    band: str
    status: bool


@dataclass
class WifiStatus:
    """Model for wifi status"""

    status: bool
    bands_status: Iterable[WifiBandStatus]
