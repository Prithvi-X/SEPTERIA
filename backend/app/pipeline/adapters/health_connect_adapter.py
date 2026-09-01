from typing import Dict, Any, List, Union
from backend.app.pipeline.adapters.base import DataSourceAdapter

class HealthConnectAdapter(DataSourceAdapter):
    """
    Extensible adapter for Android Health Connect & Apple HealthKit sync pipelines.
    Normalizes OS-aggregated health records into standardized SEPTERIA internal representations.
    """

    def __init__(self, platform_source: str = "android_health_connect"):
        super().__init__(source_name=platform_source, device_type="os_health_aggregator")

    def ingest_raw(self, payload: Union[List[Dict[str, Any]], Dict[str, Any]]) -> List[Dict[str, Any]]:
        if isinstance(payload, dict):
            payload = [payload]
        
        records = []
        for item in payload:
            rec = dict(item)
            rec["source"] = self.source_name
            rec["device_type"] = self.device_type
            rec["is_synthetic"] = False
            rec["raw_data_snapshot"] = dict(item)
            records.append(rec)
        return records

    def validate_record(self, raw_record: Dict[str, Any]) -> Dict[str, Any]:
        return raw_record

    def normalize_record(self, raw_record: Dict[str, Any]) -> Dict[str, Any]:
        return raw_record
