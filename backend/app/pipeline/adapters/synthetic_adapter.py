from typing import Dict, Any, List, Union
from datetime import datetime
from backend.app.pipeline.adapters.base import DataSourceAdapter

class SyntheticAdapter(DataSourceAdapter):
    """
    Adapter for deterministic synthetic physiological data streams.
    Marks all outputs with is_synthetic = True and provenance metadata.
    """

    def __init__(self, scenario_name: str = "normal"):
        super().__init__(source_name="synthetic_generator", device_type="synthetic_wearable_v1")
        self.scenario_name = scenario_name

    def ingest_raw(self, payload: Union[List[Dict[str, Any]], Dict[str, Any]]) -> List[Dict[str, Any]]:
        if isinstance(payload, dict):
            payload = [payload]
        
        normalized_records = []
        for item in payload:
            rec = dict(item)
            rec["is_synthetic"] = True
            rec["source"] = "synthetic_wearable"
            rec["device_type"] = self.device_type
            rec["scenario"] = self.scenario_name
            normalized_records.append(rec)
        return normalized_records

    def validate_record(self, raw_record: Dict[str, Any]) -> Dict[str, Any]:
        # Synthetic data is self-contained; validation handled by PhysiologicalValidator
        return raw_record

    def normalize_record(self, raw_record: Dict[str, Any]) -> Dict[str, Any]:
        return raw_record
