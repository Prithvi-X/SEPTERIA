from datetime import datetime, timedelta
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from backend.app.models.operational_context import OperationalContext
from backend.app.models.personnel import Personnel
from backend.app.models.audit_log import AuditLog
from backend.app.models.user import User
from backend.app.schemas.operational_context import (
    OperationalContextCreate,
    BulkContextAssignmentRequest,
    BulkAssignmentResponse,
    OperationalContextRead,
)

def format_remaining_duration(end_time: Optional[datetime]) -> Tuple[Optional[str], Optional[int]]:
    """
    Derives dynamic countdown from current timestamp and end timestamp.
    DOES NOT hardcode remaining days.
    """
    if not end_time:
        return None, None
    
    now = datetime.utcnow()
    diff = end_time - now
    total_seconds = int(diff.total_seconds())
    
    if total_seconds <= 0:
        return "Expired", 0
    
    days = diff.days
    hours = (total_seconds % 86400) // 3600
    minutes = (total_seconds % 3600) // 60
    
    if days > 0:
        formatted = f"{days}d {hours}h remaining"
    elif hours > 0:
        formatted = f"{hours}h {minutes}m remaining"
    else:
        formatted = f"{minutes}m remaining"
    
    return formatted, total_seconds

class OperationsService:
    @staticmethod
    def get_operations(
        db: Session,
        unit_id: Optional[str] = None,
        personnel_id: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        # Trigger automatic reversion check first
        OperationsService.evaluate_and_revert_expired(db)
        
        query = db.query(OperationalContext)
        if unit_id:
            query = query.filter(OperationalContext.unit_id == unit_id)
        if personnel_id:
            query = query.filter(OperationalContext.personnel_id == personnel_id)
        if status:
            query = query.filter(OperationalContext.status == status)
        
        contexts = query.order_by(OperationalContext.created_at.desc()).offset(skip).limit(limit).all()
        
        result = []
        for ctx in contexts:
            formatted, seconds = format_remaining_duration(ctx.end_time)
            data = {
                "id": ctx.id,
                "name": ctx.name,
                "personnel_id": ctx.personnel_id,
                "unit_id": ctx.unit_id,
                "zone": ctx.zone,
                "duty_type": ctx.duty_type,
                "shift": ctx.shift,
                "location": ctx.location,
                "environment": ctx.environment,
                "start_time": ctx.start_time,
                "end_time": ctx.end_time,
                "temporary": ctx.temporary,
                "auto_revert": ctx.auto_revert,
                "status": ctx.status,
                "previous_context_snapshot": ctx.previous_context_snapshot,
                "notes": ctx.notes,
                "source": ctx.source,
                "created_at": ctx.created_at,
                "remaining_duration_formatted": formatted,
                "remaining_seconds": seconds,
                "is_active": ctx.status == "ACTIVE" and (seconds is None or seconds > 0),
            }
            result.append(data)
        
        return result

    @staticmethod
    def create_assignment(
        db: Session,
        data: OperationalContextCreate,
        actor: User,
    ) -> OperationalContext:
        now = datetime.utcnow()
        
        # Calculate snapshot of previous context if personnel_id is provided
        previous_snapshot = None
        if data.personnel_id:
            personnel = db.query(Personnel).filter(Personnel.personnel_id == data.personnel_id).first()
            if personnel and personnel.active_context_id:
                prev_ctx = db.query(OperationalContext).filter(OperationalContext.id == personnel.active_context_id).first()
                if prev_ctx:
                    previous_snapshot = {
                        "id": prev_ctx.id,
                        "zone": prev_ctx.zone,
                        "duty_type": prev_ctx.duty_type,
                        "shift": prev_ctx.shift,
                        "location": prev_ctx.location,
                        "environment": prev_ctx.environment,
                    }

        context = OperationalContext(
            name=data.name or "Tactical Operational Context",
            personnel_id=data.personnel_id,
            unit_id=data.unit_id,
            zone=data.zone,
            duty_type=data.duty_type,
            shift=data.shift,
            location=data.location,
            environment=data.environment,
            start_time=data.start_time or now,
            end_time=data.end_time,
            temporary=data.temporary,
            auto_revert=data.auto_revert,
            status="ACTIVE",
            previous_context_snapshot=previous_snapshot,
            notes=data.notes,
            source="AUTHORITY",
            created_at=now,
        )
        db.add(context)
        db.flush()

        # Update personnel's active context pointer
        if data.personnel_id:
            personnel = db.query(Personnel).filter(Personnel.personnel_id == data.personnel_id).first()
            if personnel:
                personnel.active_context_id = context.id
                personnel.posting = data.location

        # Audit logging
        audit = AuditLog(
            actor_id=actor.email,
            actor_role=actor.role,
            action="CREATE_OPERATIONAL_ASSIGNMENT",
            object_type="OperationalContext",
            object_id=context.id,
            details={
                "name": context.name,
                "unit_id": context.unit_id,
                "personnel_id": context.personnel_id,
                "zone": context.zone,
                "duty_type": context.duty_type,
                "shift": context.shift,
                "temporary": context.temporary,
                "auto_revert": context.auto_revert,
                "end_time": context.end_time.isoformat() if context.end_time else None,
            },
            outcome="SUCCESS",
        )
        db.add(audit)
        db.commit()
        db.refresh(context)
        return context

    @staticmethod
    def bulk_assign_context(
        db: Session,
        req: BulkContextAssignmentRequest,
        actor: User,
    ) -> BulkAssignmentResponse:
        now = datetime.utcnow()
        start_time = req.start_time or now
        end_time = req.end_time or (start_time + timedelta(days=req.duration_days))

        # 1. Fetch targeted personnel records from PostgreSQL
        if req.personnel_ids and len(req.personnel_ids) > 0:
            personnel_list = db.query(Personnel).filter(Personnel.personnel_id.in_(req.personnel_ids)).all()
        elif req.unit_id:
            personnel_list = db.query(Personnel).filter(Personnel.unit_id == req.unit_id).all()
        else:
            personnel_list = []

        total_affected = len(personnel_list)
        if total_affected == 0:
            return BulkAssignmentResponse(
                status="warning",
                updated_count=0,
                message="No personnel matched the specified unit or criteria.",
                affected_unit=req.unit_id,
                assignment_name=req.assignment_name,
                zone=req.zone,
                auto_revert=req.auto_revert,
                end_time=end_time,
            )

        # 2. Apply operational assignment in batch
        for p in personnel_list:
            # Snapshot previous context for auto-reversion
            prev_snapshot = None
            if p.active_context_id:
                prev_ctx = db.query(OperationalContext).filter(OperationalContext.id == p.active_context_id).first()
                if prev_ctx:
                    prev_snapshot = {
                        "id": prev_ctx.id,
                        "zone": prev_ctx.zone,
                        "duty_type": prev_ctx.duty_type,
                        "shift": prev_ctx.shift,
                        "location": prev_ctx.location,
                        "environment": prev_ctx.environment,
                    }
            elif p.posting:
                prev_snapshot = {
                    "zone": "Zone 1",
                    "duty_type": "Standard Duty",
                    "shift": "Day",
                    "location": p.posting,
                    "environment": "Standard",
                }

            new_ctx = OperationalContext(
                name=req.assignment_name,
                personnel_id=p.personnel_id,
                unit_id=p.unit_id,
                zone=req.zone,
                duty_type=req.duty_type,
                shift=req.shift,
                location=req.location,
                environment=req.environment,
                start_time=start_time,
                end_time=end_time,
                temporary=True,
                auto_revert=req.auto_revert,
                status="ACTIVE",
                previous_context_snapshot=prev_snapshot,
                notes=req.notes,
                source="AUTHORITY",
                created_at=now,
            )
            db.add(new_ctx)
            db.flush()

            # Update personnel active pointer
            p.active_context_id = new_ctx.id
            p.status = "DEPLOYED"

        # 3. Create Audit Record
        audit = AuditLog(
            actor_id=actor.email,
            actor_role=actor.role,
            action="BULK_ASSIGN_CONTEXT",
            object_type="Unit/PersonnelBatch",
            object_id=req.unit_id or "CUSTOM_BATCH",
            details={
                "assignment_name": req.assignment_name,
                "unit_id": req.unit_id,
                "personnel_count": total_affected,
                "zone": req.zone,
                "duty_type": req.duty_type,
                "shift": req.shift,
                "location": req.location,
                "environment": req.environment,
                "duration_days": req.duration_days,
                "auto_revert": req.auto_revert,
                "end_time": end_time.isoformat(),
            },
            outcome="SUCCESS",
        )
        db.add(audit)
        db.commit()

        return BulkAssignmentResponse(
            status="success",
            updated_count=total_affected,
            message=f"{total_affected} personnel updated.",
            affected_unit=req.unit_id,
            assignment_name=req.assignment_name,
            zone=req.zone,
            auto_revert=req.auto_revert,
            end_time=end_time,
        )

    @staticmethod
    def evaluate_and_revert_expired(db: Session, force_actor_email: Optional[str] = None) -> int:
        """
        Automatic Reversion Logic:
        When current_time >= end_time and auto_revert=True and status='ACTIVE':
        Restores previous operational context snapshot, updates status to 'REVERTED',
        and logs an audit record.
        """
        now = datetime.utcnow()
        expired_contexts = (
            db.query(OperationalContext)
            .filter(
                OperationalContext.status == "ACTIVE",
                OperationalContext.auto_revert == True,
                OperationalContext.end_time != None,
                OperationalContext.end_time <= now,
            )
            .all()
        )

        reverted_count = 0
        for ctx in expired_contexts:
            ctx.status = "REVERTED"
            
            # If associated with personnel, restore previous snapshot
            if ctx.personnel_id:
                personnel = db.query(Personnel).filter(Personnel.personnel_id == ctx.personnel_id).first()
                if personnel and ctx.previous_context_snapshot:
                    prev = ctx.previous_context_snapshot
                    # Create restored context record
                    restored_ctx = OperationalContext(
                        name="Restored Baseline Context",
                        personnel_id=ctx.personnel_id,
                        unit_id=ctx.unit_id,
                        zone=prev.get("zone", "Zone 1"),
                        duty_type=prev.get("duty_type", "Standard Duty"),
                        shift=prev.get("shift", "Day"),
                        location=prev.get("location", personnel.posting),
                        environment=prev.get("environment", "Standard"),
                        start_time=now,
                        end_time=None,
                        temporary=False,
                        auto_revert=False,
                        status="ACTIVE",
                        source="SYSTEM_AUTO_REVERT",
                        created_at=now,
                    )
                    db.add(restored_ctx)
                    db.flush()
                    personnel.active_context_id = restored_ctx.id
                    personnel.status = "ACTIVE"

            # Create Audit Log for auto-reversion
            audit = AuditLog(
                actor_id=force_actor_email or "system@septeria.gov.in",
                actor_role="system",
                action="AUTO_REVERT_CONTEXT",
                object_type="OperationalContext",
                object_id=ctx.id,
                details={
                    "assignment_name": ctx.name,
                    "personnel_id": ctx.personnel_id,
                    "unit_id": ctx.unit_id,
                    "expired_at": ctx.end_time.isoformat() if ctx.end_time else None,
                    "restored_snapshot": ctx.previous_context_snapshot,
                },
                outcome="SUCCESS",
            )
            db.add(audit)
            reverted_count += 1

        if reverted_count > 0:
            db.commit()

        return reverted_count
