from datetime import datetime, timedelta
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.security import create_access_token
from backend.app.core.database import SessionLocal
from backend.app.models.user import User
from backend.app.models.personnel import Personnel
from backend.app.models.operational_context import OperationalContext
from backend.app.models.audit_log import AuditLog
from backend.app.services.operations_service import OperationsService, format_remaining_duration

client = TestClient(app)

@pytest.fixture
def commander_token():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.role == "commander").first()
        assert user is not None
        return create_access_token(subject=user.id, role=user.role, extra_claims={"email": user.email})
    finally:
        db.close()

@pytest.fixture
def admin_token():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.role == "admin").first()
        assert user is not None
        return create_access_token(subject=user.id, role=user.role, extra_claims={"email": user.email})
    finally:
        db.close()

def test_dynamic_countdown_calculation():
    """Verify that countdown is dynamically derived from timestamps and never hardcoded."""
    now = datetime.utcnow()
    
    # 5 days in future
    future_5d = now + timedelta(days=5, hours=6)
    formatted, seconds = format_remaining_duration(future_5d)
    assert "5d" in formatted
    assert "remaining" in formatted
    assert seconds > 0

    # 2 hours in future
    future_2h = now + timedelta(hours=2, minutes=30)
    formatted, seconds = format_remaining_duration(future_2h)
    assert "remaining" in formatted
    assert seconds > 0

    # Past time (expired)
    past_1d = now - timedelta(days=1)
    formatted, seconds = format_remaining_duration(past_1d)
    assert formatted == "Expired"
    assert seconds == 0

def test_bulk_assignment_and_database_persistence(commander_token):
    """Verify that bulk assignment persists in database and affects exact personnel count."""
    db = SessionLocal()
    try:
        count_bsf = db.query(Personnel).filter(Personnel.unit_id == "BSF-BN-47").count()
        assert count_bsf >= 147, f"Expected >= 147 seeded BSF personnel, found {count_bsf}"

        headers = {"Authorization": f"Bearer {commander_token}"}
        payload = {
            "assignment_name": "Border Sector Alpha Deployment",
            "unit_id": "BSF-BN-47",
            "zone": "Zone 2",
            "duty_type": "Border Patrol",
            "shift": "Night (20:00 - 04:00)",
            "location": "Tanot Forward Post",
            "environment": "High Heat & Arid",
            "duration_days": 7,
            "auto_revert": True,
        }

        response = client.post("/api/v1/operations/bulk-assign", json=payload, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["updated_count"] >= 147
        assert f"{data['updated_count']} personnel updated" in data["message"]

        # Verify audit log exists
        audit = db.query(AuditLog).filter(
            AuditLog.action == "BULK_ASSIGN_CONTEXT",
            AuditLog.object_id == "BSF-BN-47"
        ).first()
        assert audit is not None
        assert audit.actor_role == "commander"
    finally:
        db.close()

def test_auto_reversion_execution_and_snapshot_restoration(admin_token):
    """
    Core Test: Create temporary assignment, simulate expiration by backdating end_time,
    trigger evaluate_and_revert_expired, and verify previous context is restored,
    status is REVERTED, and audit log is written.
    """
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        p = db.query(Personnel).first()
        assert p is not None

        # Assign temporary context that expired 1 hour ago
        expired_ctx = OperationalContext(
            name="Expired Rotation Alpha",
            personnel_id=p.personnel_id,
            unit_id=p.unit_id,
            zone="Zone 2",
            duty_type="Extreme Night Patrol",
            shift="Night",
            location="Remote Sector 9",
            environment="Extreme Cold",
            start_time=now - timedelta(days=7),
            end_time=now - timedelta(hours=1), # Expired!
            temporary=True,
            auto_revert=True,
            status="ACTIVE",
            previous_context_snapshot={
                "zone": "Zone 1",
                "duty_type": "Baseline Security",
                "shift": "Day",
                "location": p.posting,
                "environment": "Standard",
            },
            source="AUTHORITY",
            created_at=now - timedelta(days=7),
        )
        db.add(expired_ctx)
        db.flush()
        p.active_context_id = expired_ctx.id
        db.commit()

        # Trigger auto-reversion check
        reverted_count = OperationsService.evaluate_and_revert_expired(db)
        assert reverted_count >= 1

        # Verify context status is now REVERTED
        db.refresh(expired_ctx)
        assert expired_ctx.status == "REVERTED"

        # Verify personnel's active context is restored to baseline snapshot
        db.refresh(p)
        new_active = db.query(OperationalContext).filter(OperationalContext.id == p.active_context_id).first()
        assert new_active is not None
        assert new_active.zone == "Zone 1"
        assert new_active.duty_type == "Baseline Security"
        assert new_active.source == "SYSTEM_AUTO_REVERT"

        # Verify audit log entry
        audit = db.query(AuditLog).filter(
            AuditLog.action == "AUTO_REVERT_CONTEXT",
            AuditLog.object_id == expired_ctx.id,
        ).first()
        assert audit is not None
    finally:
        db.close()
