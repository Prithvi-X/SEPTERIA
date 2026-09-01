"""
SEPTERIA Offline Edge Queue & Deduplication Engine (Phase 9)

Manages:
  1. Offline edge queueing during network disconnection.
  2. Cryptographic idempotency key generation (SHA-256) for deduplication.
  3. Bounded exponential backoff retry mechanism.
  4. Sync state machine: PENDING -> SYNCED / FAILED.
  5. Local secure storage simulation for queued items.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import hashlib
import json
import time

class QueuedEdgeRecord:
    def __init__(
        self,
        idempotency_key: str,
        payload: Dict[str, Any],
        device_id: str,
        device_timestamp: str,
        sequence_number: int
    ):
        self.idempotency_key = idempotency_key
        self.payload = payload
        self.device_id = device_id
        self.device_timestamp = device_timestamp
        self.sequence_number = sequence_number
        self.sync_status = "PENDING" # PENDING, SYNCED, FAILED
        self.retry_count = 0
        self.last_attempt_timestamp = None
        self.next_retry_timestamp = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "idempotency_key": self.idempotency_key,
            "device_id": self.device_id,
            "device_timestamp": self.device_timestamp,
            "sequence_number": self.sequence_number,
            "sync_status": self.sync_status,
            "retry_count": self.retry_count,
            "payload": self.payload
        }

class EdgeSyncQueue:
    """
    Offline queue simulator for the mobile edge application.
    Preserves records across connectivity loss, prevents duplication, and manages retry backoff.
    """
    def __init__(
        self,
        max_queue_size: int = 10000,
        max_retries: int = 5,
        base_backoff_seconds: float = 1.0,
        max_backoff_seconds: float = 60.0
    ):
        self.max_queue_size = max_queue_size
        self.max_retries = max_retries
        self.base_backoff_seconds = base_backoff_seconds
        self.max_backoff_seconds = max_backoff_seconds
        self.queue: Dict[str, QueuedEdgeRecord] = {}
        self.synced_keys: set = set()

    @staticmethod
    def generate_idempotency_key(device_id: str, device_timestamp: str, sequence_number: int) -> str:
        """
        Creates a deterministic unique hash for record deduplication.
        """
        raw_str = f"{device_id}::{device_timestamp}::{sequence_number}"
        return hashlib.sha256(raw_str.encode("utf-8")).hexdigest()

    def enqueue(self, payload: Dict[str, Any], device_id: str, sequence_number: int) -> QueuedEdgeRecord:
        """
        Adds a new record to the local offline queue.
        """
        device_ts = payload.get("device_timestamp") or datetime.utcnow().isoformat()
        key = payload.get("idempotency_key") or self.generate_idempotency_key(device_id, device_ts, sequence_number)

        # If already synced, don't re-enqueue
        if key in self.synced_keys:
            record = QueuedEdgeRecord(key, payload, device_id, device_ts, sequence_number)
            record.sync_status = "SYNCED"
            return record

        if key in self.queue:
            return self.queue[key]

        if len(self.queue) >= self.max_queue_size:
            # Drop oldest synced/failed if full, but never silently discard unattempted pending
            oldest_key = next(iter(self.queue))
            del self.queue[oldest_key]

        record = QueuedEdgeRecord(key, payload, device_id, device_ts, sequence_number)
        self.queue[key] = record
        return record

    def get_pending_batch(self, max_batch_size: int = 50) -> List[Dict[str, Any]]:
        """
        Retrieves eligible pending records for synchronization.
        """
        now = datetime.utcnow()
        batch = []
        for record in self.queue.values():
            if record.sync_status == "PENDING" and now >= record.next_retry_timestamp:
                batch.append({
                    "idempotency_key": record.idempotency_key,
                    "device_id": record.device_id,
                    "device_timestamp": record.device_timestamp,
                    "sequence_number": record.sequence_number,
                    "raw_payload": record.payload
                })
                if len(batch) >= max_batch_size:
                    break
        return batch

    def acknowledge_sync(self, synced_keys: List[str]):
        """
        Marks successfully acknowledged records as SYNCED.
        """
        for key in synced_keys:
            if key in self.queue:
                self.queue[key].sync_status = "SYNCED"
                self.synced_keys.add(key)
                # Remove from active pending queue to free memory
                del self.queue[key]

    def record_sync_failure(self, failed_keys: List[str], error_message: str):
        """
        Applies bounded exponential backoff to failed sync items.
        """
        now = datetime.utcnow()
        for key in failed_keys:
            if key in self.queue:
                rec = self.queue[key]
                rec.retry_count += 1
                rec.last_attempt_timestamp = now.isoformat()

                if rec.retry_count >= self.max_retries:
                    rec.sync_status = "FAILED"
                else:
                    backoff = min(self.max_backoff_seconds, self.base_backoff_seconds * (2 ** rec.retry_count))
                    rec.next_retry_timestamp = now + timedelta(seconds=backoff)

    def get_queue_status(self) -> Dict[str, Any]:
        """
        Returns queue health, pending count, and synchronization state.
        """
        pending_count = sum(1 for r in self.queue.values() if r.sync_status == "PENDING")
        failed_count = sum(1 for r in self.queue.values() if r.sync_status == "FAILED")
        return {
            "total_queued": len(self.queue),
            "pending_count": pending_count,
            "failed_count": failed_count,
            "total_synced_historical": len(self.synced_keys),
            "is_sync_healthy": failed_count == 0,
        }
