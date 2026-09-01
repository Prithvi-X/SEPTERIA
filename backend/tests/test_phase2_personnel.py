from datetime import datetime, timedelta
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.security import create_access_token
from backend.app.core.database import SessionLocal
from backend.app.models.user import User
from backend.app.models.personnel import Personnel
from backend.app.models.leave_event import LeaveEvent

client = TestClient(app)

@pytest.fixture
def welfare_token():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.role == "welfare_officer").first()
        assert user is not None
        return create_access_token(subject=user.id, role=user.role, extra_claims={"email": user.email})
    finally:
        db.close()

def test_personnel_directory_filtering(welfare_token):
    """Verify personnel listing, search and multi-criteria filters."""
    headers = {"Authorization": f"Bearer {welfare_token}"}

    # 1. Fetch all personnel
    response = client.get("/api/v1/personnel/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0

    # 2. Filter by force BSF
    response_bsf = client.get("/api/v1/personnel/?force=BSF", headers=headers)
    assert response_bsf.status_code == 200
    data_bsf = response_bsf.json()
    assert all(p["force"] == "BSF" for p in data_bsf)

    # 3. Filter by unit BSF-BN-47
    response_unit = client.get("/api/v1/personnel/?unit_id=BSF-BN-47", headers=headers)
    assert response_unit.status_code == 200
    data_unit = response_unit.json()
    assert len(data_unit) >= 147

def test_personnel_profile_and_leave_return_event(welfare_token):
    """Verify recording leave return event and calculating Day X / 14 transition tracking."""
    db = SessionLocal()
    try:
        p = db.query(Personnel).filter(Personnel.unit_id == "CRPF-BN-102").first()
        assert p is not None

        headers = {"Authorization": f"Bearer {welfare_token}"}
        
        now = datetime.utcnow()
        payload = {
            "leave_type": "ANNUAL_LEAVE",
            "leave_end_date": (now - timedelta(days=2)).isoformat(),
            "return_date": (now - timedelta(days=1)).isoformat(),
        }

        # Record leave return
        res = client.post(f"/api/v1/personnel/{p.personnel_id}/leave-return", json=payload, headers=headers)
        assert res.status_code == 200
        res_data = res.json()
        assert res_data["status"] == "success"
        assert res_data["post_leave_day_count"] >= 1
        assert res_data["post_leave_total_days"] == 14

        # Fetch detail profile
        profile_res = client.get(f"/api/v1/personnel/{p.personnel_id}", headers=headers)
        assert profile_res.status_code == 200
        profile_data = profile_res.json()
        assert profile_data["leave_status"] == "POST_LEAVE_TRANSITION"
        assert profile_data["post_leave_day_count"] is not None
        assert len(profile_data["leave_events"]) > 0
    finally:
        db.close()
