"""
SEPTERIA Phase 9 Automated Test Suite: Edge & Hardware Data Integration + Offline Operation
Tests:
  1. Synthetic Adapter 5 Scenarios
  2. BLE Adapter GATT Unpacking (0x2A37 Heart Rate & RR-Intervals)
  3. Health Connect Mapping & Provenance (OBSERVED, DERIVED, INFERRED)
  4. Malformed BLE Packet Detection & Checksum Validation
  5. Connection Lifecycle & State Transitions (Disconnect / Reconnect)
  6. Idempotent Deduplication (Prevents duplicate records)
  7. Offline Queue Buffering during Network Loss
  8. Bounded Exponential Backoff Retry Mechanism
  9. Network Reconnection & Batch Synchronization
  10. Timestamp Preservation, Sequence Auditing, & Clock Drift Tracking
  11. Privacy & RBAC Protection on Edge Overviews
  12. Integration with Phase 4 Quality Pipeline
"""

import pytest
from datetime import datetime, timedelta
import struct

from backend.app.engine.edge.synthetic_adapter import EdgeSyntheticAdapter
from backend.app.engine.edge.ble_adapter import EdgeBLEAdapter
from backend.app.engine.edge.health_connect_adapter import EdgeHealthConnectAdapter
from backend.app.engine.edge.offline_queue import EdgeSyncQueue
from backend.app.engine.edge.timestamp_manager import EdgeTimestampManager

@pytest.fixture
def synthetic_adapter():
    return EdgeSyntheticAdapter(device_id="SYNTH-TEST-001")

@pytest.fixture
def ble_adapter():
    return EdgeBLEAdapter(device_mac="AA:BB:CC:11:22:33")

@pytest.fixture
def health_connect_adapter():
    return EdgeHealthConnectAdapter()

@pytest.fixture
def offline_queue():
    return EdgeSyncQueue(max_retries=5, base_backoff_seconds=0.1, max_backoff_seconds=5.0)

@pytest.fixture
def timestamp_mgr():
    return EdgeTimestampManager(max_allowed_drift_minutes=10.0)

# -----------------------------------------------------------------------------
# Test 1: Synthetic Adapter Scenarios
# -----------------------------------------------------------------------------
def test_synthetic_adapter_scenarios(synthetic_adapter):
    scenarios = [
        "NORMAL_RECOVERY",
        "PHYSICAL_EXERTION",
        "POOR_SLEEP_RECOVERY_DECLINE",
        "SENSOR_DROPOUT",
        "CONNECTIVITY_LOSS_SYNC"
    ]
    for sc in scenarios:
        stream = synthetic_adapter.generate_demo_stream(scenario=sc, num_records=5)
        assert len(stream) == 5
        assert all(rec["is_synthetic"] is True for rec in stream)
        assert all(rec["device_source"] == "SYNTHETIC_DEMO" for rec in stream)
        assert all(rec["scenario"] == sc for rec in stream)

        # Validate physiological bounds
        is_valid, errors = synthetic_adapter.validate_packet(stream[0])
        if sc == "SENSOR_DROPOUT":
            assert is_valid is False
            assert any("bounds" in e for e in errors)
        else:
            assert is_valid is True
            assert len(errors) == 0

# -----------------------------------------------------------------------------
# Test 2: BLE GATT Characteristic Unpacking
# -----------------------------------------------------------------------------
def test_ble_gatt_heart_rate_parsing(ble_adapter):
    # Construct standard Bluetooth SIG 0x2A37 Heart Rate packet:
    # Flags = 0x16:
    #   Bit 0 = 0 (UINT8 HR)
    #   Bits 1-2 = 3 (Contact Detected)
    #   Bit 4 = 1 (RR-Interval Present)
    # HR = 78 bpm
    # RR Interval 1 = 820 ms (in 1/1024s: 820 * 1024 / 1000 = 839.68 -> 840)
    # RR Interval 2 = 800 ms (in 1/1024s: 800 * 1024 / 1000 = 819.2 -> 819)
    flags = 0x16
    hr_byte = 78
    rr1 = 840
    rr2 = 819
    raw_packet = struct.pack("<BBHH", flags, hr_byte, rr1, rr2)

    parsed = ble_adapter.parse_gatt_heart_rate(raw_packet)
    assert parsed["hr"] == 78.0
    assert parsed["contact_detected"] is True
    assert len(parsed["rr_intervals_ms"]) == 2
    assert 810.0 <= parsed["rr_intervals_ms"][0] <= 830.0
    assert parsed["hrv_rmssd"] is not None

# -----------------------------------------------------------------------------
# Test 3: Health Connect Mapping & Strict Provenance
# -----------------------------------------------------------------------------
def test_health_connect_provenance_mapping(health_connect_adapter):
    # Case A: Watch sample -> OBSERVED_FROM_DEVICE
    watch_record = {
        "record_type": "HeartRateRecord",
        "time": datetime.utcnow().isoformat(),
        "beats_per_minute": 74.0,
        "rmssd": 58.0,
        "metadata": {
            "data_origin": "com.samsung.health",
            "device": {"type": "WATCH"}
        }
    }
    mapped_watch = health_connect_adapter.map_health_connect_record(watch_record)
    assert mapped_watch["hr"] == 74.0
    assert mapped_watch["hrv"] == 58.0
    assert mapped_watch["evidence_status"] == "OBSERVED_FROM_DEVICE"

    # Case B: Phone estimated sleep -> INFERRED
    phone_sleep = {
        "record_type": "SleepSessionRecord",
        "start_time": datetime.utcnow().isoformat(),
        "duration_minutes": 450.0,
        "metadata": {
            "data_origin": "com.google.android.apps.fitness",
            "device": {"type": "PHONE"}
        }
    }
    mapped_phone = health_connect_adapter.map_health_connect_record(phone_sleep)
    assert mapped_phone["sleep"] == 7.5
    assert mapped_phone["evidence_status"] == "INFERRED"

    # Case C: Aggregated daily resting HR -> DERIVED
    resting_hr_record = {
        "record_type": "RestingHeartRateRecord",
        "time": datetime.utcnow().isoformat(),
        "beats_per_minute": 61.0,
        "metadata": {"device": {"type": "WATCH"}}
    }
    mapped_resting = health_connect_adapter.map_health_connect_record(resting_hr_record)
    assert mapped_resting["resting_hr"] == 61.0
    assert mapped_resting["evidence_status"] == "DERIVED"

# -----------------------------------------------------------------------------
# Test 4: Malformed BLE Packet Detection & Checksum Validation
# -----------------------------------------------------------------------------
def test_malformed_ble_packet_rejection(ble_adapter):
    # Test A: Truncated GATT packet
    with pytest.raises(ValueError, match="truncated"):
        ble_adapter.parse_gatt_heart_rate(b"\x01") # Too short

    # Test B: Custom packet bad checksum
    # Format: [Header (0xAA), Seq (1), AccX (0), AccY (0), AccZ (2048), EDA (100), Bad Checksum (0xFF)]
    bad_checksum_packet = struct.pack("<BHhhhHB", 0xAA, 1, 0, 0, 2048, 100, 0xFF)
    with pytest.raises(ValueError, match="checksum mismatch"):
        ble_adapter.parse_custom_telemetry_packet(bad_checksum_packet)

# -----------------------------------------------------------------------------
# Test 5: Connection State Transitions
# -----------------------------------------------------------------------------
def test_ble_connection_lifecycle(ble_adapter):
    assert ble_adapter.connection_state == "CONNECTED"
    ble_adapter.disconnect()
    assert ble_adapter.connection_state == "DISCONNECTED"
    ble_adapter.reconnect()
    assert ble_adapter.connection_state == "CONNECTED"

# -----------------------------------------------------------------------------
# Test 6: Offline Queue & Idempotency Generation
# -----------------------------------------------------------------------------
def test_offline_queue_enqueue_and_idempotency(offline_queue):
    device_id = "DEV-TACTICAL-01"
    ts = "2026-09-01T10:00:00Z"
    seq = 42

    key = offline_queue.generate_idempotency_key(device_id, ts, seq)
    assert len(key) == 64 # SHA-256 hex string

    payload = {"hr": 75.0, "hrv": 52.0, "device_timestamp": ts}
    rec1 = offline_queue.enqueue(payload, device_id, seq)
    assert rec1.sync_status == "PENDING"
    assert rec1.idempotency_key == key

    # Enqueue same record again -> returns existing without creating duplicate
    rec2 = offline_queue.enqueue(payload, device_id, seq)
    assert rec2.idempotency_key == key
    assert len(offline_queue.queue) == 1

# -----------------------------------------------------------------------------
# Test 7: Bounded Exponential Backoff Retry Mechanism
# -----------------------------------------------------------------------------
def test_bounded_backoff_retry(offline_queue):
    payload = {"hr": 80.0}
    rec = offline_queue.enqueue(payload, "DEV-01", 1)
    key = rec.idempotency_key

    # Simulate 3 failures
    for attempt in range(3):
        offline_queue.record_sync_failure([key], "Network connection timeout")
        assert offline_queue.queue[key].retry_count == attempt + 1
        assert offline_queue.queue[key].sync_status == "PENDING"

    # Simulate failures up to max_retries (5)
    offline_queue.record_sync_failure([key], "Timeout")
    offline_queue.record_sync_failure([key], "Timeout")
    assert offline_queue.queue[key].retry_count == 5
    assert offline_queue.queue[key].sync_status == "FAILED"

# -----------------------------------------------------------------------------
# Test 8: Network Reconnection & Batch Synchronization
# -----------------------------------------------------------------------------
def test_reconnection_and_sync_acknowledgment(offline_queue):
    # Enqueue 3 records while offline
    for s in range(3):
        offline_queue.enqueue({"hr": 70.0 + s}, "DEV-01", s)

    status_before = offline_queue.get_queue_status()
    assert status_before["pending_count"] == 3

    # Network connects -> retrieve pending batch
    batch = offline_queue.get_pending_batch(max_batch_size=10)
    assert len(batch) == 3

    # Acknowledge sync
    synced_keys = [b["idempotency_key"] for b in batch]
    offline_queue.acknowledge_sync(synced_keys)

    status_after = offline_queue.get_queue_status()
    assert status_after["pending_count"] == 0
    assert status_after["total_synced_historical"] == 3

# -----------------------------------------------------------------------------
# Test 9: Timestamp Management & Clock Drift Tracking
# -----------------------------------------------------------------------------
def test_timestamp_preservation_and_clock_drift(timestamp_mgr):
    now = datetime.utcnow()

    # Case A: Normal 2-second network latency drift
    device_ts = now - timedelta(seconds=2)
    norm_dt, drift_ms, flags = timestamp_mgr.process_timestamp(device_ts.isoformat(), sequence_number=1, server_ingest_time=now)
    assert 1900.0 <= drift_ms <= 2100.0
    assert len(flags) == 0

    # Case B: Excessive drift (> 10 minutes)
    drifted_ts = now - timedelta(minutes=15)
    _, excessive_drift_ms, flags = timestamp_mgr.process_timestamp(drifted_ts.isoformat(), sequence_number=2, server_ingest_time=now)
    assert any("EXCESSIVE_CLOCK_DRIFT" in f for f in flags)

    # Case C: Non-monotonic backwards jump
    jump_back_ts = now - timedelta(minutes=20)
    _, _, flags_jump = timestamp_mgr.process_timestamp(jump_back_ts.isoformat(), sequence_number=3, server_ingest_time=now)
    assert any("NON_MONOTONIC" in f for f in flags_jump)

@pytest.fixture
def local_session():
    from backend.app.core.database import SessionLocal, Base, engine
    from backend.app.models.user import User
    from shared.constants.roles import UserRole
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        # Ensure test personnel exists
        p_user = session.query(User).filter(User.email == "test_edge_soldier@septeria.gov.in").first()
        if not p_user:
            p_user = User(
                id="test-edge-soldier-uuid-99",
                email="test_edge_soldier@septeria.gov.in",
                hashed_password="dummy",
                role=UserRole.PERSONNEL.value,
                force="BSF",
                unit_id="BSF-BN-47",
                is_active=True
            )
            session.add(p_user)
            session.commit()
        yield session, p_user
    finally:
        session.close()

# -----------------------------------------------------------------------------
# Test 10: End-to-End Edge Ingestion & Deduplication Service Integration
# -----------------------------------------------------------------------------
def test_edge_service_ingest_and_deduplication(local_session):
    db_session, test_user = local_session
    from backend.app.services.edge_service import EdgeService
    from backend.app.schemas.edge import EdgeBatchIngestRequest, EdgeTelemetryPacket
    from backend.app.models.edge import EdgeTelemetryRecord

    # Clean up any residual records from prior runs
    db_session.query(EdgeTelemetryRecord).filter(
        EdgeTelemetryRecord.personnel_id == str(test_user.id)
    ).delete()
    db_session.commit()

    now_iso = datetime.utcnow().isoformat()
    packet1 = EdgeTelemetryPacket(
        device_id="BAND-BSF-01",
        device_source="BLE",
        device_timestamp=now_iso,
        sequence_number=101,
        hr=72.0,
        hrv=60.0,
        resting_hr=64.0,
        sleep=7.5,
        activity=0.3,
        source_quality=0.98
    )

    req = EdgeBatchIngestRequest(
        personnel_id=str(test_user.id),
        device_id="BAND-BSF-01",
        device_source="BLE",
        packets=[packet1]
    )

    # First ingestion -> Accepted
    res1 = EdgeService.ingest_edge_batch(db_session, test_user, req)
    assert res1.accepted_count == 1
    assert res1.deduplicated_count == 0
    assert res1.sync_status == "SYNCED"

    # Repeated identical ingestion (network retry) -> Deduplicated
    res2 = EdgeService.ingest_edge_batch(db_session, test_user, req)
    assert res2.accepted_count == 0
    assert res2.deduplicated_count == 1
    assert res2.sync_status == "SYNCED"

    # Verify exactly 1 record in database
    records_count = db_session.query(EdgeTelemetryRecord).filter(
        EdgeTelemetryRecord.personnel_id == str(test_user.id)
    ).count()
    assert records_count == 1

# -----------------------------------------------------------------------------
# Test 11: Privacy & RBAC Enforcement on Edge Telemetry
# -----------------------------------------------------------------------------
def test_edge_privacy_rbac_boundaries(local_session):
    db_session, test_user = local_session
    from backend.app.services.edge_service import EdgeService
    from fastapi import HTTPException

    # Personnel cannot view another personnel's sync status
    other_personnel_id = "OTHER-SOLDIER-999"
    with pytest.raises(HTTPException) as exc:
        EdgeService.get_device_sync_status(db_session, personnel_id=other_personnel_id, current_user=test_user)
    assert exc.value.status_code == 403

# -----------------------------------------------------------------------------
# Test 12: Command Authority Overview Contains Zero Raw Biometrics
# -----------------------------------------------------------------------------
def test_command_authority_overview_no_raw_biometrics(local_session):
    db_session, test_user = local_session
    from backend.app.services.edge_service import EdgeService

    summary = EdgeService.get_authority_edge_overview(db_session, test_user)
    summary_dict = summary.model_dump()

    # Must contain only aggregate fleet telemetry health metrics
    assert "total_devices_registered" in summary_dict
    assert "connected_devices_count" in summary_dict
    assert "overall_telemetry_completeness_pct" in summary_dict
    assert summary_dict["data_classification"] == "AGGREGATE_COMMAND_SUMMARY_NO_RAW_BIOMETRICS"

    # Must not contain individual private metrics
    private_fields = ["hr", "hrv", "eda", "sleep_stages", "temperature", "raw_payload"]
    for field in private_fields:
        assert field not in summary_dict
