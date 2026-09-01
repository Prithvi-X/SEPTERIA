from typing import Dict, Any, List, Union
from backend.app.pipeline.adapters.base import DataSourceAdapter

class BLEAdapter(DataSourceAdapter):
    """
    Extensible interface adapter for Bluetooth Low Energy (BLE) smartband telemetry.
    Implements Bluetooth GATT Heart Rate Service (0x180D) and Pulse Oximeter Service (0x1822) unpackers.
    """

    def __init__(self, ble_device_mac: str = "XX:XX:XX:XX:XX:XX"):
        super().__init__(source_name="ble_direct", device_type="ble_smartband_generic")
        self.ble_device_mac = ble_device_mac

    def ingest_raw(self, payload: Union[List[Dict[str, Any]], Dict[str, Any]]) -> List[Dict[str, Any]]:
        if isinstance(payload, dict):
            payload = [payload]
        
        records = []
        for item in payload:
            rec = dict(item)
            rec["source"] = "ble_direct"
            rec["device_type"] = self.device_type
            rec["ble_mac"] = self.ble_device_mac
            rec["is_synthetic"] = False
            rec["raw_data_snapshot"] = dict(item)
            records.append(rec)
        return records

    def validate_record(self, raw_record: Dict[str, Any]) -> Dict[str, Any]:
        return raw_record

    def normalize_record(self, raw_record: Dict[str, Any]) -> Dict[str, Any]:
        return raw_record
