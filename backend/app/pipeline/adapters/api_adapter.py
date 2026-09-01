from typing import Dict, Any, List, Union
from datetime import datetime
from backend.app.pipeline.adapters.base import DataSourceAdapter

class APIAdapter(DataSourceAdapter):
    """
    Adapter for REST API ingested physiological telemetry and self-reports.
    Handles payload unwrapping, device header capture, and raw snapshot preservation.
    """

    def __init__(self, client_device: str = "mobile_client_v1"):
        super().__init__(source_name="api_ingestion", device_type=client_device)

    def ingest_raw(self, payload: Union[List[Dict[str, Any]], Dict[str, Any]]) -> List[Dict[str, Any]]:
        if isinstance(payload, dict):
            payload = [payload]
        
        records = []
        for item in payload:
            rec = dict(item)
            rec["source"] = "api_ingestion"
            rec["device_type"] = rec.get("device_type", self.device_type)
            rec["is_synthetic"] = rec.get("is_synthetic", False)
            # Retain raw snapshot for provenance
            rec["raw_data_snapshot"] = dict(item)
            records.append(rec)
        return records

    def validate_record(self, raw_record: Dict[str, Any]) -> Dict[str, Any]:
        return raw_record

    def normalize_record(self, raw_record: Dict[str, Any]) -> Dict[str, Any]:
        return raw_record
