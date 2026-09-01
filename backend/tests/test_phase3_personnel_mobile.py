import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.security import create_access_token
from backend.app.core.database import SessionLocal
from backend.app.models.user import User
from backend.app.models.personnel import Personnel
from backend.app.models.wellness import WellnessRecord
from backend.app.models.support_request import SupportRequest
from backend.app.models.audit_log import AuditLog

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

def test_personnel_me_profile_and_read_only_context(personnel_p1047_token):
    """
    Verify authenticated personnel profile, authoritative operational context (read-only),
    dynamic assignment countdown, and post-leave transition Day 3 / 14.
    """
    headers = {"Authorization": f"Bearer {personnel_p1047_token}"}
    response = client.get("/api/v1/personnel/me", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert data["personnel_id"] == "P-1047"
    assert data["force"] == "BSF"
    assert data["unit_id"] == "BSF-BN-47"
    assert data["status"] in ["ACTIVE", "DEPLOYED"]

    # Authoritative context assertions
    ctx = data["authoritative_context"]
    assert ctx["zone"] in ["Zone 1", "Zone 2"]
    assert ctx["duty_type"] in ["Border Patrol", "Baseline Security"]
    assert any(s in ctx["shift"] for s in ["Day", "Night", "Swing", "Standard"])
    assert ctx["temporary"] in [True, False]
    if ctx.get("remaining_duration_formatted"):
        assert "remaining" in ctx["remaining_duration_formatted"] or "Permanent" in ctx["remaining_duration_formatted"] or "days" in ctx["remaining_duration_formatted"]

    # Post-leave transition assertions
    if data.get("leave_status") == "POST_LEAVE_TRANSITION":
        assert data["post_leave_day_count"] >= 0
        assert data["post_leave_total_days"] == 14

def test_voluntary_wellness_checkin_submission_and_persistence(personnel_p1047_token):
    """
    Verify voluntary wellness check-in with 1-5 scales reaches FastAPI and is stored in PostgreSQL.
    """
    headers = {"Authorization": f"Bearer {personnel_p1047_token}"}
    payload = {
        "stress": 4,
        "fatigue": 4,
        "sleep_quality": 2,
        "mood": 3,
        "workload": 5,
        "notes": "Night border patrol adaptation test.",
    }

    response = client.post("/api/v1/personnel/me/wellness", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["personnel_id"] == "P-1047"
    assert data["stress"] == 4
    assert data["fatigue"] == 4
    assert data["sleep_quality"] == 2
    assert data["mood"] == 3
    assert data["workload"] == 5
    assert data["evidence_status"] == "OBSERVED"

    # Verify PostgreSQL persistence
    db = SessionLocal()
    try:
        record = db.query(WellnessRecord).filter(
            WellnessRecord.id == data["id"],
            WellnessRecord.personnel_id == "P-1047"
        ).first()
        assert record is not None
        assert record.workload == 5

        # Verify audit log
        audit = db.query(AuditLog).filter(
            AuditLog.action == "SUBMIT_VOLUNTARY_WELLNESS",
            AuditLog.object_id == data["id"],
        ).first()
        assert audit is not None
    finally:
        db.close()

def test_wellness_history_retrieval(personnel_p1047_token):
    """Verify authenticated personnel can retrieve private check-in history."""
    headers = {"Authorization": f"Bearer {personnel_p1047_token}"}
    response = client.get("/api/v1/personnel/me/wellness", headers=headers)
    assert response.status_code == 200
    records = response.json()
    assert len(records) >= 1
    assert all(r["personnel_id"] == "P-1047" for r in records)

def test_physiological_trends_retrieval(personnel_p1047_token):
    """Verify authenticated personnel can retrieve physiological recovery trends."""
    headers = {"Authorization": f"Bearer {personnel_p1047_token}"}
    response = client.get("/api/v1/personnel/me/trends", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["personnel_id"] == "P-1047"
    assert len(data["trends"]) >= 5
    assert data["evidence_status"] == "OBSERVED"
    assert data["latest_hr"] > 0
    assert data["latest_hrv"] > 0

def test_support_request_submission_and_status(personnel_p1047_token):
    """Verify confidential support request submission and persistence."""
    headers = {"Authorization": f"Bearer {personnel_p1047_token}"}
    payload = {
        "urgency": "MODERATE",
        "note": "Request confidential welfare check-in regarding family concerns.",
    }

    response = client.post("/api/v1/personnel/me/support", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["personnel_id"] == "P-1047"
    assert data["urgency"] == "MODERATE"
    assert data["status"] == "PENDING"

    # Verify query
    status_res = client.get("/api/v1/personnel/me/support", headers=headers)
    assert status_res.status_code == 200
    req_list = status_res.json()
    assert len(req_list) >= 1
    assert req_list[0]["urgency"] == "MODERATE"

def test_voice_checkin_consent(personnel_p1047_token):
    """Verify voluntary voice check-in flow with explicit consent validation."""
    headers = {"Authorization": f"Bearer {personnel_p1047_token}"}

    # 1. With consent: SUCCESS
    res_ok = client.post(
        "/api/v1/personnel/me/voice-check-in",
        json={"consent_given": True, "duration_seconds": 25},
        headers=headers,
    )
    assert res_ok.status_code == 200
    assert res_ok.json()["consent_verified"] is True

    # 2. Without consent: REJECTED (400)
    res_bad = client.post(
        "/api/v1/personnel/me/voice-check-in",
        json={"consent_given": False},
        headers=headers,
    )
    assert res_bad.status_code == 400

def test_cross_personnel_privacy_enforcement(personnel_p1047_token):
    """
    Critical Security Rule:
    Personnel role is FORBIDDEN from accessing other personnel's data or authority endpoints.
    """
    headers = {"Authorization": f"Bearer {personnel_p1047_token}"}

    # Cannot access authority personnel directory
    res_dir = client.get("/api/v1/personnel/", headers=headers)
    assert res_dir.status_code == 403

    # Cannot query another jawan's profile
    res_other = client.get("/api/v1/personnel/CRPF-88202", headers=headers)
    assert res_other.status_code == 403

    # Cannot query audit logs
    res_audit = client.get("/api/v1/audit-logs/", headers=headers)
    assert res_audit.status_code == 403
