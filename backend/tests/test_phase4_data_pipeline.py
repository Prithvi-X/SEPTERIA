import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.security import create_access_token
from backend.app.core.database import SessionLocal
from backend.app.models.user import User
from backend.app.models.personnel import Personnel
from backend.app.models.physiology import PhysiologicalRecord
from backend.app.models.missing_interval import MissingInterval
from backend.app.pipeline.normalization.normalizer import DataNormalizer
from backend.app.pipeline.validation.physiological_validator import PhysiologicalValidator
from backend.app.pipeline.sqi.signal_quality import SignalQualityEngine
from backend.app.pipeline.context.motion_context import MotionContextClassifier
from backend.app.pipeline.context.contradiction_detector import ContradictionDetector
from backend.app.pipeline.missingness.missing_handler import MissingDataHandler
from backend.app.pipeline.features.windowing import FeatureWindowEngine
from backend.app.pipeline.features.multimodal_alignment import MultimodalAlignmentEngine
from backend.app.pipeline.scenarios.synthetic_generator import SyntheticScenarioGenerator
from backend.app.services.data_pipeline_service import DataPipelineService
from shared.constants.evidence import EvidenceStatus, SQIStatus, MotionContext, GapType

client = TestClient(app)

@pytest.fixture
def personnel_p1047_token():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "personnel.p1047@septeria.gov.in").first()
        assert user is not None, "Demo user personnel.p1047@septeria.gov.in must exist"
        return create_access_token(subject=user.id, role=user.role, extra_claims={"email": user.email})
    finally:
        db.close()

def test_valid_hr_accepted_and_normalized(personnel_p1047_token):
    """Test Case 1 & 5: Valid physiological record is accepted, normalized, and marked OBSERVED."""
    raw = {
        "timestamp": datetime.utcnow().isoformat(),
        "hr": 72.4,
        "hrv": 54.2,
        "resting_hr": 61.0,
        "sleep": 7.5,
        "activity": 4200.0,
        "signal_quality": 0.95,
    }
    norm = DataNormalizer.normalize_physiological_record(raw)
    val = PhysiologicalValidator.validate(norm)
    assert val.is_valid is True
    assert len(val.errors) == 0

    sqi = SignalQualityEngine.evaluate(norm)
    assert sqi.sqi_status == SQIStatus.GOOD.value
    assert sqi.evidence_status == EvidenceStatus.OBSERVED.value

    motion, is_active, _ = MotionContextClassifier.classify(norm["activity"], hr=norm["hr"])
    assert motion == MotionContext.MODERATE.value
    assert is_active is True

def test_invalid_hr_and_hrv_rejected():
    """Test Case 2: Biologically impossible values are rejected by the validator."""
    bad_record = {
        "hr": 290.0,  # Impossible human heart rate
        "hrv": -15.0, # Impossible negative HRV
        "sleep": -3.0,
        "activity": -50.0,
    }
    val = PhysiologicalValidator.validate(bad_record)
    assert val.is_valid is False
    assert len(val.errors) >= 3

def test_missing_hrv_segment_detected():
    """Test Case 3: A 20-minute gap in minute-level stream is detected as LONG_GAP."""
    now = datetime.utcnow()
    records = [
        {"personnel_id": "P-1047", "timestamp": now - timedelta(minutes=60), "hr": 70, "hrv": 55, "activity": 500},
        {"personnel_id": "P-1047", "timestamp": now - timedelta(minutes=40), "hr": 72, "hrv": 52, "activity": 600},
    ]
    gaps = MissingDataHandler.detect_gaps("P-1047", "hrv", records, expected_interval_minutes=1.0)
    assert len(gaps) == 1
    assert gaps[0]["duration_minutes"] == 19.0
    assert gaps[0]["gap_type"] == GapType.LONG_GAP.value
    assert gaps[0]["reconstructed"] is False

def test_short_gap_conservative_interpolation_marked_inferred():
    """Test Case 4: Short gaps (<15m) interpolated for visualization are strictly marked INFERRED."""
    now = datetime.utcnow()
    records = [
        {"personnel_id": "P-1047", "timestamp": now - timedelta(minutes=10), "hr": 70.0, "hrv": 50.0, "activity": 100.0, "evidence_status": "OBSERVED"},
        {"personnel_id": "P-1047", "timestamp": now, "hr": 80.0, "hrv": 60.0, "activity": 200.0, "evidence_status": "OBSERVED"},
    ]
    augmented, recon_gaps = MissingDataHandler.interpolate_short_gaps(records, expected_interval_minutes=1.0)
    assert len(augmented) > 2
    assert len(recon_gaps) == 1
    assert recon_gaps[0]["reconstructed"] is True

    # Check intermediate inferred records
    inferred = [r for r in augmented if r.get("evidence_status") == EvidenceStatus.INFERRED.value]
    assert len(inferred) == 9
    assert all(r["evidence_status"] == EvidenceStatus.INFERRED.value for r in inferred)
    assert all(r["sqi_status"] == SQIStatus.FAIR.value for r in inferred)

def test_rolling_features_marked_derived():
    """Test Case 6: Rolling aggregations are computed and marked DERIVED."""
    daily_records = [
        {"timestamp": datetime.utcnow() - timedelta(days=i), "hrv": 50.0 + i, "sleep": 7.0}
        for i in range(7)
    ]
    features = FeatureWindowEngine.calculate_rolling_features(daily_records)
    assert features["rolling_7d_hrv"] is not None
    assert features["rolling_7d_sleep"] == 7.0
    assert features["evidence_status"] == "DERIVED"

def test_multimodal_alignment_contextual_tagging():
    """Test Case 7: Multimodal alignment tags operational and environmental data as CONTEXTUAL."""
    phys = {"timestamp": datetime.utcnow(), "personnel_id": "P-1047", "hr": 72.0, "hrv": 54.0, "evidence_status": "OBSERVED"}
    ops = {"zone": "Zone 2", "duty_type": "Border Patrol", "shift": "Night", "temporary": True}
    env = {"ambient_temp": 42.0, "altitude": 210.0, "humidity": 18.0}
    aligned = MultimodalAlignmentEngine.align(phys, operational_context=ops, environmental_record=env, post_leave_day_count=3)

    assert aligned["operational_zone"] == "Zone 2"
    assert aligned["ops_evidence_status"] == "CONTEXTUAL"
    assert aligned["ambient_temperature"] == 42.0
    assert aligned["env_evidence_status"] == "CONTEXTUAL"
    assert aligned["post_leave_transition_day"] == 3

def test_poor_quality_produces_uncertain_sqi():
    """Test Case 8: Degraded sensor hardware quality yields POOR SQI and UNCERTAIN evidence status."""
    record = {
        "hr": 75.0,
        "hrv": 45.0,
        "signal_quality": 0.20, # Poor contact
        "activity": 500.0,
    }
    sqi = SignalQualityEngine.evaluate(record)
    assert sqi.sqi_status == SQIStatus.POOR.value
    assert sqi.evidence_status == EvidenceStatus.UNCERTAIN.value

def test_high_hr_plus_high_activity_attribution():
    """Test Case 9: High HR + High Activity attribution matches user-approved scientific phrasing."""
    assessment = ContradictionDetector.assess(
        hr=145.0,
        hrv=38.0,
        activity=14000.0,
        sleep=7.0,
    )
    assert "Physiological elevation is consistent with physical exertion; psychological attribution reduced." in assessment.attribution_summary
    assert assessment.motion_context == "EXERTIONAL"
    assert assessment.confidence_adjustment < 1.0

def test_high_hr_plus_low_activity_attribution():
    """Test Case 10: High HR without physical motion flagged as potential unexplained physiological deviation."""
    assessment = ContradictionDetector.assess(
        hr=112.0,
        hrv=32.0,
        activity=1200.0,
        sleep=5.0,
    )
    assert "Physiological elevation without physical exertion; potential unexplained physiological deviation." in assessment.attribution_summary
    assert len(assessment.discrepancies) >= 1

def test_completeness_calculation_across_modalities():
    """Test Case 11: Data completeness score calculation."""
    comp = MissingDataHandler.calculate_completeness(total_expected_intervals=100, observed_intervals=88)
    assert comp == 88.0

def test_synthetic_scenarios_generation():
    """Test Case 12: All 7 synthetic scenarios (A through G) generate valid records."""
    for code in ["A", "B", "C", "D", "E", "F", "G"]:
        recs = SyntheticScenarioGenerator.generate_scenario(code, personnel_id="P-1047", days=7)
        assert len(recs) >= 7
        assert all(r["is_synthetic"] is True for r in recs)
        assert all(r["personnel_id"] == "P-1047" for r in recs)

def test_end_to_end_p1047_scenario_with_missing_gap(personnel_p1047_token):
    """
    Test Case 13 (End-to-End Scenario):
    Executes Scenario E (20-minute missing HRV gap) for P-1047 in BSF-BN-47 (Zone 2, Night Duty),
    verifies gap detection, completeness score calculation, and retrieval via self-service APIs.
    """
    headers = {"Authorization": f"Bearer {personnel_p1047_token}"}

    # 1. Trigger Scenario E (Sensor Dropout 20min) via API
    resp_scen = client.post(
        "/api/v1/physiology/demo/scenario",
        json={"scenario_code": "E", "personnel_id": "P-1047", "days": 7},
        headers=headers,
    )
    assert resp_scen.status_code == 200
    scen_data = resp_scen.json()
    assert scen_data["scenario_code"] == "E"
    assert scen_data["detected_gaps"] >= 1
    assert scen_data["records_ingested"] >= 40

    # 2. Query Personnel Quality Summary Endpoint
    resp_qual = client.get("/api/v1/personnel/me/quality", headers=headers)
    assert resp_qual.status_code == 200
    qual_data = resp_qual.json()
    assert qual_data["personnel_id"] == "P-1047"
    assert len(qual_data["missing_intervals"]) >= 1
    assert qual_data["overall_completeness_pct"] > 0.0
    assert "hr" in qual_data["signals"]

    # 3. Query Enriched Trends Endpoint
    resp_trends = client.get("/api/v1/personnel/me/trends?days=7", headers=headers)
    assert resp_trends.status_code == 200
    trends_data = resp_trends.json()
    assert trends_data["personnel_id"] == "P-1047"
    assert len(trends_data["trends"]) >= 5
    assert trends_data["trends"][0]["sqi_status"] in ["GOOD", "FAIR", "POOR", "MISSING"]
    assert trends_data["trends"][0]["evidence_status"] in ["OBSERVED", "DERIVED", "INFERRED", "UNCERTAIN"]

def test_cross_personnel_privacy_enforcement(personnel_p1047_token):
    """
    Security Rule: Personnel token cannot access another person's quality summary or authority directory.
    """
    headers = {"Authorization": f"Bearer {personnel_p1047_token}"}
    res_dir = client.get("/api/v1/personnel/", headers=headers)
    assert res_dir.status_code == 403
