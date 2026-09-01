"""
SEPTERIA Development Database Seeder (Phase 4)
Populates synthetic demonstration accounts, units, personnel records,
operational contexts, physiological trends, wellness records, missing intervals,
environmental context records, and audit logs.
"""

import os
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from datetime import datetime, timedelta
import random
from backend.app.core.database import SessionLocal, engine, Base
from backend.app.core.security import get_password_hash
from backend.app.models import (
    User,
    Unit,
    Personnel,
    OperationalContext,
    Assignment,
    LeaveEvent,
    WellnessRecord,
    PhysiologicalRecord,
    Baseline,
    Prediction,
    Recommendation,
    AuditLog,
    SupportRequest,
    MissingInterval,
    EnvironmentalRecord,
)
from shared.constants.roles import UserRole
from shared.constants.zones import OperationalZone
from shared.constants.evidence import EvidenceStatus, SQIStatus, MotionContext, GapType

def seed_synthetic_dev_data():
    print("Re-creating Database Schema on PostgreSQL 16 with Phase 4 Data Pipeline columns...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        print("Seeding synthetic users and demo accounts...")

        # 1. Demo Users (Least-Privilege Roles & Synthetic Demo Accounts)
        users_data = [
            {
                "email": "admin@septeria.gov.in",
                "password": "SepteriaAdmin2026!",
                "role": UserRole.ADMIN.value,
                "force": "MHA_HQ",
                "unit_id": "HQ-ADMIN",
            },
            {
                "email": "commander.bsf47@septeria.gov.in",
                "password": "Commander2026!",
                "role": UserRole.COMMANDER.value,
                "force": "BSF",
                "unit_id": "BSF-BN-47",
            },
            {
                "email": "welfare.crpf@septeria.gov.in",
                "password": "Welfare2026!",
                "role": UserRole.WELFARE_OFFICER.value,
                "force": "CRPF",
                "unit_id": "CRPF-BN-102",
            },
            {
                "email": "medical.itbp@septeria.gov.in",
                "password": "Medical2026!",
                "role": UserRole.MEDICAL_OFFICER.value,
                "force": "ITBP",
                "unit_id": "ITBP-BN-18",
            },
            {
                "email": "personnel.p1047@septeria.gov.in",
                "password": "Personnel2026!",
                "role": UserRole.PERSONNEL.value,
                "force": "BSF",
                "unit_id": "BSF-BN-47",
            },
            {
                "email": "personnel.crpf88219@septeria.gov.in",
                "password": "Personnel2026!",
                "role": UserRole.PERSONNEL.value,
                "force": "CRPF",
                "unit_id": "CRPF-BN-102",
            },
            # Convenience Demo Logins
            {
                "email": "admin@septeria.mil",
                "password": "admin123",
                "role": UserRole.ADMIN.value,
                "force": "MHA_HQ",
                "unit_id": "HQ-ADMIN",
            },
            {
                "email": "commander@septeria.mil",
                "password": "commander123",
                "role": UserRole.COMMANDER.value,
                "force": "BSF",
                "unit_id": "BSF-BN-47",
            },
            {
                "email": "medical@septeria.mil",
                "password": "medical123",
                "role": UserRole.MEDICAL_OFFICER.value,
                "force": "ITBP",
                "unit_id": "ITBP-BN-18",
            },
            {
                "email": "welfare@septeria.mil",
                "password": "welfare123",
                "role": UserRole.WELFARE_OFFICER.value,
                "force": "CRPF",
                "unit_id": "CRPF-BN-102",
            },
            {
                "email": "soldier@septeria.mil",
                "password": "soldier123",
                "role": UserRole.PERSONNEL.value,
                "force": "BSF",
                "unit_id": "BSF-BN-47",
            },
        ]

        created_users = {}
        for u in users_data:
            user = User(
                email=u["email"],
                hashed_password=get_password_hash(u["password"]),
                role=u["role"],
                force=u["force"],
                unit_id=u["unit_id"],
                is_active=True,
            )
            db.add(user)
            db.flush()
            created_users[u["email"]] = user

        # 2. Synthetic Units
        print("Seeding synthetic units...")
        units_data = [
            {
                "code": "BSF-BN-47",
                "name": "47th Battalion BSF (Synthetic Demo)",
                "force": "BSF",
                "location": "Jaisalmer Sector, Rajasthan",
                "zone": OperationalZone.ZONE_2.value,
            },
            {
                "code": "CRPF-BN-102",
                "name": "102 Rapid Action Battalion CRPF (Synthetic Demo)",
                "force": "CRPF",
                "location": "Central Operating Base, Raipur Sector",
                "zone": OperationalZone.ZONE_1.value,
            },
            {
                "code": "ITBP-BN-18",
                "name": "18th Mountain Battalion ITBP (Synthetic Demo)",
                "force": "ITBP",
                "location": "High Altitude Base, Ladakh Sector",
                "zone": OperationalZone.ZONE_2.value,
            },
            {
                "code": "CISF-SEC-HQ",
                "name": "Central Industrial Security Force HQ (Synthetic Demo)",
                "force": "CISF",
                "location": "CGO Complex, New Delhi",
                "zone": OperationalZone.ZONE_1.value,
            },
        ]

        for unit in units_data:
            db_unit = Unit(
                code=unit["code"],
                name=unit["name"],
                force=unit["force"],
                location=unit["location"],
                zone=unit["zone"],
            )
            db.add(db_unit)
        db.flush()

        # 3. Environmental Records
        print("Seeding environmental context records...")
        now = datetime.utcnow()
        env_bsf = EnvironmentalRecord(
            location="Tanot Forward Line B",
            unit_id="BSF-BN-47",
            ambient_temp=42.5,
            altitude=210.0,
            humidity=18.0,
            environment_category="High Heat & Desert Arid",
            incident_phase="ROUTINE",
            timestamp=now,
        )
        env_crpf = EnvironmentalRecord(
            location="Raipur Operating Hub",
            unit_id="CRPF-BN-102",
            ambient_temp=31.0,
            altitude=298.0,
            humidity=72.0,
            environment_category="Standard Humid",
            incident_phase="ROUTINE",
            timestamp=now,
        )
        env_itbp = EnvironmentalRecord(
            location="Forward Post Khardung",
            unit_id="ITBP-BN-18",
            ambient_temp=-4.5,
            altitude=4250.0,
            humidity=40.0,
            environment_category="Extreme Cold / High Altitude",
            incident_phase="ROUTINE",
            timestamp=now,
        )
        db.add(env_bsf)
        db.add(env_crpf)
        db.add(env_itbp)
        db.flush()

        # 4. Baseline Operational Contexts
        print("Seeding baseline operational contexts...")
        bsf_baseline = OperationalContext(
            name="Baseline Border Vigilance",
            unit_id="BSF-BN-47",
            zone="Zone 2",
            duty_type="Border Surveillance / Static Observation",
            shift="Day (08:00 - 16:00)",
            location="Tanot Base, Jaisalmer",
            environment="Arid / High Heat",
            start_time=now - timedelta(days=30),
            end_time=None,
            temporary=False,
            auto_revert=False,
            status="ACTIVE",
            source="AUTHORITY",
            created_at=now - timedelta(days=30),
        )
        crpf_baseline = OperationalContext(
            name="Standard Area Security",
            unit_id="CRPF-BN-102",
            zone="Zone 1",
            duty_type="Quick Reaction Team / Area Domination",
            shift="Rotational (12-hr)",
            location="Raipur Operating Hub",
            environment="Standard Humid",
            start_time=now - timedelta(days=30),
            end_time=None,
            temporary=False,
            auto_revert=False,
            status="ACTIVE",
            source="AUTHORITY",
            created_at=now - timedelta(days=30),
        )
        itbp_baseline = OperationalContext(
            name="Mountain Post Patrol",
            unit_id="ITBP-BN-18",
            zone="Zone 2",
            duty_type="High-Altitude Reconnaissance",
            shift="Day Patrol (06:00 - 14:00)",
            location="Forward Post Khardung",
            environment="Extreme Cold / Low Oxygen",
            start_time=now - timedelta(days=30),
            end_time=None,
            temporary=False,
            auto_revert=False,
            status="ACTIVE",
            source="AUTHORITY",
            created_at=now - timedelta(days=30),
        )
        db.add(bsf_baseline)
        db.add(crpf_baseline)
        db.add(itbp_baseline)
        db.flush()

        # 5. Active Temporary Deployment for Demo Countdown (~5 days 14 hours)
        print("Seeding active temporary deployment with dynamic countdown...")
        demo_temp_assignment = OperationalContext(
            name="Border Deployment Alpha",
            unit_id="BSF-BN-47",
            zone="Zone 2",
            duty_type="Border Patrol",
            shift="Night (20:00 - 04:00)",
            location="Tanot Forward Line B",
            environment="High Heat & Desert Arid",
            start_time=now - timedelta(days=1, hours=10),
            end_time=now + timedelta(days=5, hours=14), # Real timestamp: 5d 14h remaining
            temporary=True,
            auto_revert=True,
            status="ACTIVE",
            previous_context_snapshot={
                "zone": "Zone 2",
                "duty_type": "Border Surveillance / Static Observation",
                "shift": "Day (08:00 - 16:00)",
                "location": "Tanot Base, Jaisalmer",
                "environment": "Arid / High Heat",
            },
            notes="Authoritative 7-day tactical rotation ordered by Unit Commander.",
            source="AUTHORITY",
            created_at=now - timedelta(days=1, hours=10),
        )
        db.add(demo_temp_assignment)
        db.flush()

        # 6. Seeding Synthetic Personnel Records
        print("Seeding synthetic personnel records (147 for BSF Unit 47 including P-1047, 30 for CRPF, 15 for ITBP)...")
        
        # Personnel P-1047 (Primary Demo Jawan)
        p1047_user = created_users["personnel.p1047@septeria.gov.in"]
        leave_ret_p1047 = now - timedelta(days=2) # 2 days ago -> Day 3 / 14
        
        p1047 = Personnel(
            personnel_id="P-1047",
            user_id=p1047_user.id,
            force="BSF",
            unit_id="BSF-BN-47",
            role="Constable / GD (Synthetic Demo)",
            rank="Constable / GD",
            posting="Border Outpost Tanot",
            status="DEPLOYED",
            active_context_id=demo_temp_assignment.id,
            leave_status="POST_LEAVE_TRANSITION",
            leave_end_date=leave_ret_p1047 - timedelta(days=1),
            return_date=leave_ret_p1047,
            transition_start_date=leave_ret_p1047,
            created_at=now - timedelta(days=180),
        )
        db.add(p1047)

        # Historical leave event for P-1047
        leave_ev_p1047 = LeaveEvent(
            personnel_id="P-1047",
            leave_type="ANNUAL_LEAVE",
            leave_start_date=leave_ret_p1047 - timedelta(days=15),
            leave_end_date=leave_ret_p1047 - timedelta(days=1),
            return_date=leave_ret_p1047,
            transition_days_total=14,
            status="ACTIVE_TRANSITION",
            recorded_by="commander.bsf47@septeria.gov.in",
            created_at=leave_ret_p1047,
        )
        db.add(leave_ev_p1047)

        # Seed 7 days of historical PhysiologicalRecords for P-1047 with SQI & Provenance
        for day_offset in range(7, 0, -1):
            ts = now - timedelta(days=day_offset, hours=random.randint(1, 4))
            act_val = float(6800 + random.randint(-800, 1500))
            physio = PhysiologicalRecord(
                personnel_id="P-1047",
                timestamp=ts,
                hr=float(72 + random.randint(-4, 6)),
                hrv=float(52 + random.randint(-6, 8)),
                resting_hr=float(61 + random.randint(-2, 4)),
                sleep=float(6.5 + random.uniform(-0.8, 0.9)),
                activity=act_val,
                respiration=16.0,
                temperature=36.7,
                signal_quality=0.96,
                sqi_status=SQIStatus.GOOD.value,
                evidence_status=EvidenceStatus.OBSERVED.value,
                motion_context=MotionContext.MODERATE.value if act_val >= 3000 else MotionContext.LOW.value,
                source="synthetic_wearable",
                device_type="synthetic_smartband_v1",
                is_synthetic=True,
                raw_data_snapshot={"raw_hr": 72, "raw_hrv": 52, "raw_activity": act_val},
                processing_version="v1.0",
                created_at=ts,
            )
            db.add(physio)

        # Seed Baseline records for P-1047 (Robust Stats: median, MAD)
        p1047_baselines = [
            Baseline(
                personnel_id="P-1047",
                metric="hr",
                median=72.0,
                mad=4.0,
                p10=62.0,
                p90=82.0,
                mean=72.0,
                std=5.5,
                observation_count=7,
                coverage_pct=100.0,
                quality_rating="GOOD",
                is_cohort_prior=False,
                baseline_statistics={"median": 72.0, "mad": 4.0, "p10": 62.0, "p90": 82.0},
                confidence=1.0,
                update_timestamp=now,
            ),
            Baseline(
                personnel_id="P-1047",
                metric="hrv_rmssd",
                median=52.0,
                mad=6.0,
                p10=40.0,
                p90=68.0,
                mean=52.0,
                std=8.0,
                observation_count=7,
                coverage_pct=100.0,
                quality_rating="GOOD",
                is_cohort_prior=False,
                baseline_statistics={"median": 52.0, "mad": 6.0, "p10": 40.0, "p90": 68.0},
                confidence=1.0,
                update_timestamp=now,
            ),
            Baseline(
                personnel_id="P-1047",
                metric="resting_hr",
                median=61.0,
                mad=3.0,
                p10=56.0,
                p90=66.0,
                mean=61.0,
                std=3.8,
                observation_count=7,
                coverage_pct=100.0,
                quality_rating="GOOD",
                is_cohort_prior=False,
                baseline_statistics={"median": 61.0, "mad": 3.0, "p10": 56.0, "p90": 66.0},
                confidence=1.0,
                update_timestamp=now,
            ),
            Baseline(
                personnel_id="P-1047",
                metric="sleep_hours",
                median=7.0,
                mad=0.7,
                p10=5.8,
                p90=8.0,
                mean=7.0,
                std=0.9,
                observation_count=7,
                coverage_pct=100.0,
                quality_rating="GOOD",
                is_cohort_prior=False,
                baseline_statistics={"median": 7.0, "mad": 0.7, "p10": 5.8, "p90": 8.0},
                confidence=1.0,
                update_timestamp=now,
            ),
            Baseline(
                personnel_id="P-1047",
                metric="activity",
                median=6800.0,
                mad=900.0,
                p10=4500.0,
                p90=9500.0,
                mean=6800.0,
                std=1200.0,
                observation_count=7,
                coverage_pct=100.0,
                quality_rating="GOOD",
                is_cohort_prior=False,
                baseline_statistics={"median": 6800.0, "mad": 900.0, "p10": 4500.0, "p90": 9500.0},
                confidence=1.0,
                update_timestamp=now,
            ),
        ]
        for b in p1047_baselines:
            db.add(b)

        # Seed 1 detected MissingInterval for P-1047 (20-minute gap demonstration)
        gap_p1047 = MissingInterval(
            personnel_id="P-1047",
            signal_name="hrv",
            start_time=now - timedelta(days=1, hours=3),
            end_time=now - timedelta(days=1, hours=2, minutes=40),
            duration_minutes=20.0,
            gap_type=GapType.LONG_GAP.value,
            reconstructed=False,
            reconstruction_method=None,
        )
        db.add(gap_p1047)

        # Seed 2 historical WellnessRecords for P-1047
        w1 = WellnessRecord(
            personnel_id="P-1047",
            timestamp=now - timedelta(days=2, hours=3),
            stress=3,
            fatigue=3,
            sleep_quality=3,
            mood=3,
            workload=3,
            notes="Routine patrol shift completed.",
            evidence_status=EvidenceStatus.OBSERVED.value,
            created_at=now - timedelta(days=2, hours=3),
        )
        w2 = WellnessRecord(
            personnel_id="P-1047",
            timestamp=now - timedelta(days=1, hours=4),
            stress=4,
            fatigue=3,
            sleep_quality=2,
            mood=3,
            workload=4,
            notes="Night shift adaptation in progress.",
            evidence_status=EvidenceStatus.OBSERVED.value,
            created_at=now - timedelta(days=1, hours=4),
        )
        db.add(w1)
        db.add(w2)

        # Remaining 146 Jawans in BSF-BN-47
        for i in range(2, 148):
            pid = f"BSF-47{i:03d}"
            rank = "Constable / GD" if i > 15 else "Head Constable" if i > 5 else "Sub-Inspector"
            is_deployed = (i <= 10)
            p = Personnel(
                personnel_id=pid,
                user_id=None,
                force="BSF",
                unit_id="BSF-BN-47",
                role=f"{rank} (Synthetic)",
                rank=rank,
                posting="Border Outpost Tanot",
                status="DEPLOYED" if is_deployed else "ACTIVE",
                active_context_id=demo_temp_assignment.id if is_deployed else bsf_baseline.id,
                leave_status="NONE",
                created_at=now - timedelta(days=random.randint(60, 365)),
            )
            db.add(p)

        # CRPF Unit 102: 30 Personnel
        for i in range(1, 31):
            pid = f"CRPF-88{200+i:03d}"
            user_link = created_users["personnel.crpf88219@septeria.gov.in"].id if pid == "CRPF-88219" else None
            rank = "Head Constable" if i % 3 == 0 else "Constable / GD"
            is_post_leave = (i in [3, 5, 8])
            leave_ret = now - timedelta(days=random.randint(1, 6)) if is_post_leave else None

            p = Personnel(
                personnel_id=pid,
                user_id=user_link,
                force="CRPF",
                unit_id="CRPF-BN-102",
                role=f"{rank} (Synthetic)",
                rank=rank,
                posting="Raipur Operating Base",
                status="TRANSITION" if is_post_leave else "ACTIVE",
                active_context_id=crpf_baseline.id,
                leave_status="POST_LEAVE_TRANSITION" if is_post_leave else "NONE",
                leave_end_date=leave_ret - timedelta(days=1) if is_post_leave else None,
                return_date=leave_ret,
                transition_start_date=leave_ret,
                created_at=now - timedelta(days=random.randint(60, 365)),
            )
            db.add(p)

            if is_post_leave:
                leave_ev = LeaveEvent(
                    personnel_id=pid,
                    leave_type="ANNUAL_LEAVE",
                    leave_start_date=leave_ret - timedelta(days=16),
                    leave_end_date=leave_ret - timedelta(days=1),
                    return_date=leave_ret,
                    transition_days_total=14,
                    status="ACTIVE_TRANSITION",
                    recorded_by="welfare.crpf@septeria.gov.in",
                    created_at=leave_ret,
                )
                db.add(leave_ev)

        # ITBP Unit 18: 15 Personnel
        for i in range(1, 16):
            pid = f"ITBP-18{i:03d}"
            rank = "Sub-Inspector" if i == 1 else "Constable / GD"
            p = Personnel(
                personnel_id=pid,
                user_id=None,
                force="ITBP",
                unit_id="ITBP-BN-18",
                role=f"{rank} (Synthetic)",
                rank=rank,
                posting="Forward High-Altitude Post",
                status="ACTIVE",
                active_context_id=itbp_baseline.id,
                leave_status="NONE",
                created_at=now - timedelta(days=random.randint(60, 365)),
            )
            db.add(p)

        db.flush()

        # 7. Audit Log Records
        audit1 = AuditLog(
            actor_id="admin@septeria.gov.in",
            actor_role=UserRole.ADMIN.value,
            action="SYSTEM_INIT_SEED",
            object_type="System",
            object_id="PHASE_4_SEED",
            details={"environment": "development", "data_type": "SYNTHETIC_DEMO_PHASE_4", "personnel_count": 192},
            outcome="SUCCESS",
        )
        db.add(audit1)

        db.commit()
        print("Successfully seeded Phase 4 synthetic development data with SQI, missing intervals, and environmental context!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_synthetic_dev_data()
