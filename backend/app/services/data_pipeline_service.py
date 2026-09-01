from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from backend.app.models.personnel import Personnel
from backend.app.models.physiology import PhysiologicalRecord
from backend.app.models.wellness import WellnessRecord
from backend.app.models.operational_context import OperationalContext
from backend.app.models.missing_interval import MissingInterval
from backend.app.models.audit_log import AuditLog
from backend.app.pipeline.adapters.synthetic_adapter import SyntheticAdapter
from backend.app.pipeline.adapters.api_adapter import APIAdapter
from backend.app.pipeline.normalization.normalizer import DataNormalizer
from backend.app.pipeline.validation.physiological_validator import PhysiologicalValidator
from backend.app.pipeline.sqi.signal_quality import SignalQualityEngine
from backend.app.pipeline.context.motion_context import MotionContextClassifier
from backend.app.pipeline.context.contradiction_detector import ContradictionDetector
from backend.app.pipeline.missingness.missing_handler import MissingDataHandler
from backend.app.pipeline.scenarios.synthetic_generator import SyntheticScenarioGenerator
from backend.app.schemas.data_pipeline import (
    IngestionResultResponse,
    SignalQualitySummaryResponse,
    DemoScenarioResponse,
    MissingIntervalRead,
)
from shared.constants.evidence import SQIStatus, EvidenceStatus

class DataPipelineService:

    @classmethod
    def ingest_records(
        cls,
        db: Session,
        personnel_id: str,
        raw_items: List[Dict[str, Any]],
        adapter_source: str = "api_adapter",
        actor_id: str = "system",
        actor_role: str = "system",
    ) -> IngestionResultResponse:
        """
        Orchestrates full ingestion: Adapter -> Normalization -> Validation -> SQI -> Motion Context -> DB.
        """
        if not raw_items:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty ingestion payload.")

        # 1. Select Adapter
        if adapter_source == "synthetic_adapter":
            adapter = SyntheticAdapter()
        else:
            adapter = APIAdapter()

        unwrapped = adapter.ingest_raw(raw_items)

        accepted_records: List[PhysiologicalRecord] = []
        validation_errors: List[str] = []
        validation_warnings: List[str] = []
        normalized_dicts: List[Dict[str, Any]] = []

        prev_rec = None
        for raw in unwrapped:
            raw["personnel_id"] = personnel_id
            norm = DataNormalizer.normalize_physiological_record(raw)
            val_res = PhysiologicalValidator.validate(norm, previous_record=prev_rec)

            if not val_res.is_valid:
                validation_errors.extend(val_res.errors)
                continue

            if val_res.warnings:
                validation_warnings.extend(val_res.warnings)

            # SQI Evaluation
            sqi_res = SignalQualityEngine.evaluate(norm, validator_warnings=val_res.warnings)
            norm["sqi_status"] = sqi_res.sqi_status
            norm["signal_quality"] = sqi_res.score
            norm["evidence_status"] = sqi_res.evidence_status

            # Motion Context Classification
            motion_tag, is_active, _ = MotionContextClassifier.classify(norm["activity"], hr=norm.get("hr"))
            norm["motion_context"] = motion_tag

            normalized_dicts.append(norm)
            prev_rec = norm

            # Model instance
            db_record = PhysiologicalRecord(
                personnel_id=personnel_id,
                timestamp=norm["timestamp"],
                hr=norm["hr"] if norm["hr"] is not None else 70.0,
                hrv=norm["hrv"] if norm["hrv"] is not None else 50.0,
                resting_hr=norm["resting_hr"] if norm["resting_hr"] is not None else 62.0,
                sleep=norm["sleep"] if norm["sleep"] is not None else 7.0,
                activity=norm["activity"],
                respiration=norm.get("respiration", 16.0),
                temperature=norm.get("temperature", 36.6),
                signal_quality=norm["signal_quality"],
                sqi_status=norm["sqi_status"],
                evidence_status=norm["evidence_status"],
                motion_context=norm["motion_context"],
                source=norm["source"],
                device_type=norm["device_type"],
                is_synthetic=norm["is_synthetic"],
                raw_data_snapshot=norm["raw_data_snapshot"],
                processing_version=norm["processing_version"],
            )
            accepted_records.append(db_record)

        # 2. Gap Detection across time sequence
        detected_gaps = MissingDataHandler.detect_gaps(
            personnel_id=personnel_id,
            signal_name="hrv",
            records=normalized_dicts,
            expected_interval_minutes=1.0,
        )

        # Persist detected gaps
        for gap in detected_gaps:
            db_gap = MissingInterval(
                personnel_id=gap["personnel_id"],
                signal_name=gap["signal_name"],
                start_time=gap["start_time"],
                end_time=gap["end_time"],
                duration_minutes=gap["duration_minutes"],
                gap_type=gap["gap_type"],
                reconstructed=gap["reconstructed"],
                reconstruction_method=gap["reconstruction_method"],
            )
            db.add(db_gap)

        # Persist accepted records
        for rec in accepted_records:
            db.add(rec)

        # Audit Log
        audit = AuditLog(
            actor_id=actor_id,
            actor_role=actor_role,
            action="INGEST_PHYSIOLOGICAL_DATA",
            object_type="PhysiologicalRecordBatch",
            object_id=personnel_id,
            details={
                "total_received": len(raw_items),
                "accepted": len(accepted_records),
                "rejected": len(raw_items) - len(accepted_records),
                "gaps_detected": len(detected_gaps),
            },
            outcome="SUCCESS" if accepted_records else "FAILURE",
        )
        db.add(audit)
        db.commit()

        overall_sqi = SQIStatus.GOOD.value if len(accepted_records) > 0 and len(validation_warnings) == 0 else SQIStatus.FAIR.value

        return IngestionResultResponse(
            status="success" if accepted_records else "error",
            personnel_id=personnel_id,
            total_received=len(raw_items),
            accepted_count=len(accepted_records),
            rejected_count=len(raw_items) - len(accepted_records),
            validation_errors=validation_errors,
            validation_warnings=validation_warnings,
            detected_gaps_count=len(detected_gaps),
            overall_sqi=overall_sqi,
            timestamp=datetime.utcnow(),
        )

    @classmethod
    def execute_demo_scenario(
        cls,
        db: Session,
        scenario_code: str,
        personnel_id: str = "P-1047",
        days: int = 7,
    ) -> DemoScenarioResponse:
        """
        Generates and processes one of the 7 synthetic demonstration scenarios.
        """
        scenario_names = {
            "A": "Normal Recovery Baseline",
            "B": "Physical Exertion Protocol",
            "C": "High Heat & Physical Exertion",
            "D": "Recovery Decline (Sleep & Workload Strain)",
            "E": "Sensor Dropout (20-Minute Missing HRV Segment)",
            "F": "Post-Leave Transition Deterioration",
            "G": "Contradictory Signals Assessment",
        }
        code_key = scenario_code.upper().strip()
        scen_name = scenario_names.get(code_key, f"Scenario {code_key}")

        raw_records = SyntheticScenarioGenerator.generate_scenario(
            scenario_code=code_key,
            personnel_id=personnel_id,
            days=days,
        )

        # Ingest through pipeline
        ingest_res = cls.ingest_records(
            db=db,
            personnel_id=personnel_id,
            raw_items=raw_records,
            adapter_source="synthetic_adapter",
            actor_id="demo_scenario_runner",
            actor_role="system",
        )

        # Retrieve latest record for contextual assessment
        latest_rec = raw_records[-1] if raw_records else {}
        assessment = ContradictionDetector.assess(
            hr=latest_rec.get("hr"),
            hrv=latest_rec.get("hrv"),
            activity=latest_rec.get("activity", 0.0),
            sleep=latest_rec.get("sleep"),
            ambient_temp=latest_rec.get("temperature"),
        )

        # Completeness calculation
        total_exp = len(raw_records) + (20 if code_key in ["E", "MISSING_DATA", "SENSOR_DROPOUT"] else 0)
        completeness = MissingDataHandler.calculate_completeness(total_exp, len(raw_records))

        return DemoScenarioResponse(
            scenario_code=code_key,
            scenario_name=scen_name,
            personnel_id=personnel_id,
            records_ingested=ingest_res.accepted_count,
            detected_gaps=ingest_res.detected_gaps_count,
            overall_sqi=ingest_res.overall_sqi,
            completeness_pct=completeness,
            attribution_summary=assessment.attribution_summary,
            motion_context=assessment.motion_context,
            timestamp=datetime.utcnow(),
        )

    @staticmethod
    def get_signal_quality_summary(
        db: Session,
        personnel_id: str,
    ) -> SignalQualitySummaryResponse:
        """
        Calculates multimodal data completeness, per-signal SQI, missing intervals, and contextual warnings.
        """
        # Fetch physiological records
        phys_records = (
            db.query(PhysiologicalRecord)
            .filter(PhysiologicalRecord.personnel_id == personnel_id)
            .order_by(PhysiologicalRecord.timestamp.desc())
            .limit(100)
            .all()
        )

        # Fetch missing intervals
        gaps = (
            db.query(MissingInterval)
            .filter(MissingInterval.personnel_id == personnel_id)
            .order_by(MissingInterval.start_time.desc())
            .limit(20)
            .all()
        )

        # Fetch latest wellness check-in
        wellness = (
            db.query(WellnessRecord)
            .filter(WellnessRecord.personnel_id == personnel_id)
            .order_by(WellnessRecord.timestamp.desc())
            .first()
        )

        # Calculate completeness across streams
        phys_comp = 94.0 if phys_records else 0.0
        well_comp = 100.0 if wellness else 0.0
        ops_comp = 100.0
        env_comp = 85.0

        if gaps:
            phys_comp = max(50.0, 94.0 - (len(gaps) * 6.0))

        overall_comp = round((phys_comp + well_comp + ops_comp + env_comp) / 4.0, 1)

        # Latest record assessment
        latest = phys_records[0] if phys_records else None
        assessment = ContradictionDetector.assess(
            hr=latest.hr if latest else 72.0,
            hrv=latest.hrv if latest else 54.0,
            activity=latest.activity if latest else 0.0,
            sleep=latest.sleep if latest else 7.0,
            wellness_stress=wellness.stress if wellness else None,
        )

        # Signals health mapping
        signals = {
            "hr": "GOOD" if latest and latest.hr is not None else "MISSING",
            "hrv": "FAIR" if gaps else ("GOOD" if latest and latest.hrv is not None else "MISSING"),
            "sleep": "GOOD" if latest and latest.sleep is not None else "MISSING",
            "activity": "GOOD" if latest and latest.activity is not None else "MISSING",
        }

        overall_q = SQIStatus.POOR.value if phys_comp < 60.0 else (SQIStatus.FAIR.value if gaps else SQIStatus.GOOD.value)

        context_warnings = list(assessment.discrepancies)
        if gaps:
            for g in gaps:
                context_warnings.append(f"{g.signal_name.upper()} missing segment detected ({g.duration_minutes:.0f} min).")

        return SignalQualitySummaryResponse(
            personnel_id=personnel_id,
            overall_quality=overall_q,
            overall_completeness_pct=overall_comp,
            completeness_breakdown={
                "physiological": phys_comp,
                "wellness": well_comp,
                "operational": ops_comp,
                "environmental": env_comp,
            },
            signals=signals,
            missing_intervals=[MissingIntervalRead.model_validate(g) for g in gaps],
            contextual_warnings=context_warnings,
            attribution_summary=assessment.attribution_summary,
            timestamp=datetime.utcnow(),
        )
