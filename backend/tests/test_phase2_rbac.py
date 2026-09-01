import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.security import create_access_token
from backend.app.core.database import SessionLocal
from backend.app.models.user import User

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
def welfare_token():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.role == "welfare_officer").first()
        assert user is not None
        return create_access_token(subject=user.id, role=user.role, extra_claims={"email": user.email})
    finally:
        db.close()

@pytest.fixture
def medical_token():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.role == "medical_officer").first()
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

@pytest.fixture
def personnel_token():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.role == "personnel").first()
        assert user is not None
        return create_access_token(subject=user.id, role=user.role, extra_claims={"email": user.email})
    finally:
        db.close()

def test_rbac_operational_assignment_least_privilege(commander_token, welfare_token, medical_token, personnel_token):
    """
    Least-Privilege Rule:
    Commander CAN create operational assignments.
    Welfare Officer, Medical Officer, and Personnel are FORBIDDEN (403).
    """
    payload = {
        "assignment_name": "QRT Sector Rotation",
        "unit_id": "CRPF-BN-102",
        "zone": "Zone 1",
        "duty_type": "QRT Patrol",
        "shift": "Day",
        "location": "Raipur Central",
        "environment": "Standard",
        "duration_days": 5,
        "auto_revert": True,
    }

    # 1. Commander: ALLOWED (200)
    res_cmd = client.post("/api/v1/operations/bulk-assign", json=payload, headers={"Authorization": f"Bearer {commander_token}"})
    assert res_cmd.status_code == 200

    # 2. Welfare Officer: FORBIDDEN (403)
    res_welfare = client.post("/api/v1/operations/bulk-assign", json=payload, headers={"Authorization": f"Bearer {welfare_token}"})
    assert res_welfare.status_code == 403

    # 3. Medical Officer: FORBIDDEN (403)
    res_medical = client.post("/api/v1/operations/bulk-assign", json=payload, headers={"Authorization": f"Bearer {medical_token}"})
    assert res_medical.status_code == 403

    # 4. Personnel (Jawan): FORBIDDEN (403)
    res_personnel = client.post("/api/v1/operations/bulk-assign", json=payload, headers={"Authorization": f"Bearer {personnel_token}"})
    assert res_personnel.status_code == 403

def test_rbac_personnel_directory_access(commander_token, welfare_token, medical_token, admin_token, personnel_token):
    """
    Least-Privilege Rule:
    Authority roles can view directory.
    Personnel role is FORBIDDEN from the authority directory.
    """
    for token in [commander_token, welfare_token, medical_token, admin_token]:
        res = client.get("/api/v1/personnel/", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200

    res_p = client.get("/api/v1/personnel/", headers={"Authorization": f"Bearer {personnel_token}"})
    assert res_p.status_code == 403

def test_rbac_audit_logs_restricted_to_admin(admin_token, commander_token, welfare_token):
    """
    Least-Privilege Rule:
    Only System Admin can view audit logs.
    Commander & Welfare Officer are FORBIDDEN (403).
    """
    res_admin = client.get("/api/v1/audit-logs/", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_admin.status_code == 200

    res_cmd = client.get("/api/v1/audit-logs/", headers={"Authorization": f"Bearer {commander_token}"})
    assert res_cmd.status_code == 403

    res_welfare = client.get("/api/v1/audit-logs/", headers={"Authorization": f"Bearer {welfare_token}"})
    assert res_welfare.status_code == 403
