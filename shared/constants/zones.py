from enum import Enum

class OperationalZone(str, Enum):
    ZONE_1 = "Zone 1: High-Intensity / Active Operations"
    ZONE_2 = "Zone 2: Border / Remote / Extreme Environment"
    ZONE_3 = "Zone 3: Critical Incident / Post-Incident Recovery"

ALL_ZONES = [zone.value for zone in OperationalZone]
