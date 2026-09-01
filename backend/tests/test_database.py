from datetime import datetime
from backend.app.models.unit import Unit
from backend.app.models.personnel import Personnel
from backend.app.models.operational_context import OperationalContext
from backend.app.models.wellness import WellnessRecord
from backend.app.models.physiology import PhysiologicalRecord
from backend.app.models.audit_log import AuditLog
from shared.constants.zones import OperationalZone
from shared.constants.evidence import EvidenceStatus

def test_database_crud_operations(db_session):
    # 1. Insert Unit
    test_unit = Unit(
        code="TEST-BN-99",
        name="99th Test Battalion",
        force="CRPF",
        location="Test Sector",
        zone=OperationalZone.ZONE_1.value,
    )
    db_session.add(test_unit)
    db_session.commit()

    queried_unit = db_session.query(Unit).filter(Unit.code == "TEST-BN-99").first()
    assert queried_unit is not None
    assert queried_unit.name == "99th Test Battalion"

    # 2. Insert Personnel
    test_personnel = Personnel(
        personnel_id="TEST-99001",
        force="CRPF",
        unit_id="TEST-BN-99",
        role="Inspector",
        rank="Inspector",
        posting="Test Sector Headquarters",
        status="ACTIVE",
    )
    db_session.add(test_personnel)
    db_session.commit()

    queried_personnel = db_session.query(Personnel).filter(Personnel.personnel_id == "TEST-99001").first()
    assert queried_personnel is not None
    assert queried_personnel.role == "Inspector"

    # 3. Insert Operational Context
    test_context = OperationalContext(
        unit_id="TEST-BN-99",
        zone=OperationalZone.ZONE_1.value,
        duty_type="Test Duty",
        shift="Morning",
        location="Test Location",
        environment="Standard",
        start_time=datetime.utcnow(),
        temporary=False,
        auto_revert=True,
    )
    db_session.add(test_context)
    db_session.commit()

    queried_context = db_session.query(OperationalContext).filter(OperationalContext.unit_id == "TEST-BN-99").first()
    assert queried_context is not None
    assert queried_context.zone == OperationalZone.ZONE_1.value

    # 4. Insert Wellness Record
    test_wellness = WellnessRecord(
        personnel_id="TEST-99001",
        timestamp=datetime.utcnow(),
        fatigue=2,
        stress=3,
        mood=4,
        sleep_quality=3,
        evidence_status=EvidenceStatus.OBSERVED.value,
    )
    db_session.add(test_wellness)
    db_session.commit()

    queried_wellness = db_session.query(WellnessRecord).filter(WellnessRecord.personnel_id == "TEST-99001").first()
    assert queried_wellness is not None
    assert queried_wellness.stress == 3

    # Clean up test records
    db_session.delete(queried_wellness)
    db_session.delete(queried_context)
    db_session.delete(queried_personnel)
    db_session.delete(queried_unit)
    db_session.commit()
