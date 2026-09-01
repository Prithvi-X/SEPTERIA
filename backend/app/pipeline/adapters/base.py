from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime

class DataSourceAdapter(ABC):
    """
    Abstract Base Class for Data Source Adapters in the SEPTERIA Pipeline.
    Encapsulates ingestion, validation, normalization, and source metadata extraction.
    """

    def __init__(self, source_name: str, device_type: str = "generic"):
        self.source_name = source_name
        self.device_type = device_type

    @abstractmethod
    def ingest_raw(self, payload: Any) -> List[Dict[str, Any]]:
        """
        Parses incoming raw payload (JSON, CSV, sensor packet) into a list of raw record dictionaries.
        """
        pass

    @abstractmethod
    def validate_record(self, raw_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates individual field constraints and flags suspicious or corrupt elements.
        """
        pass

    @abstractmethod
    def normalize_record(self, raw_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalizes timestamps to UTC ISO and standardizes metric units.
        """
        pass

    def get_source_metadata(self) -> Dict[str, Any]:
        """
        Returns adapter provenance metadata.
        """
        return {
            "source_name": self.source_name,
            "device_type": self.device_type,
            "adapter_class": self.__class__.__name__,
            "timestamp_utc": datetime.utcnow().isoformat(),
        }
