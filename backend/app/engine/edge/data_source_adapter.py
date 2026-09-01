"""
SEPTERIA Edge Data Adapter Base Architecture (Phase 9)

Pluggable adapter interface for hardware/phone wellness telemetry.
Distinguishes OBSERVED, DERIVED, and INFERRED metrics with strict provenance.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

class EdgeDataSourceAdapter(ABC):
    """
    Abstract base class for all SEPTERIA edge and hardware telemetry adapters.
    Provides uniform ingest, packet validation, normalization, and provenance tracking.
    """
    def __init__(self, adapter_type: str, device_id: str):
        self.adapter_type = adapter_type
        self.device_id = device_id
        self.created_at = datetime.utcnow().isoformat()

    @abstractmethod
    def ingest_raw(self, raw_payload: Any) -> List[Dict[str, Any]]:
        """
        Parses incoming raw edge payload (BLE packet bytes, Health Connect records, or JSON).
        """
        pass

    @abstractmethod
    def validate_packet(self, packet: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validates individual sensor packet integrity, range constraints, and checksums.
        Returns: (is_valid, validation_errors)
        """
        pass

    @abstractmethod
    def normalize_packet(self, packet: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalizes sensor metric units to SEPTERIA standard schema:
        - Heart rate: bpm
        - HRV: rMSSD in milliseconds
        - Temperature: degrees Celsius
        - Activity: normalized motion energy / steps
        - Sleep: hours
        """
        pass

    def get_provenance(self) -> Dict[str, Any]:
        """
        Returns full adapter hardware provenance metadata.
        """
        return {
            "adapter_type": self.adapter_type,
            "device_id": self.device_id,
            "adapter_class": self.__class__.__name__,
            "edge_version": "v1.0.0-PROTOTYPE",
            "timestamp_utc": datetime.utcnow().isoformat(),
        }
