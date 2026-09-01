from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from backend.app.models.personnel import Personnel
from backend.app.models.operational_context import OperationalContext
from backend.app.models.leave_event import LeaveEvent
from backend.app.models.audit_log import AuditLog
from backend.app.models.user import User
from backend.app.schemas.personnel import LeaveReturnRequest
from backend.app.services.operations_service import OperationsService, format_remaining_duration

class PersonnelService:
    @staticmethod
    def list_personnel(
        db: Session,
        search: Optional[str] = None,
        force: Optional[str] = None,
        unit_id: Optional[str] = None,
        zone: Optional[str] = None,
        duty: Optional[str] = None,
        shift: Optional[str] = None,
        status: Optional[str] = None,
        leave_status: Optional[str] = None,
        skip: int = 0,
        limit: int = 200,
    ) -> Tuple[List[Dict[str, Any]], int]:
        # Run automatic reversion evaluation first
        OperationsService.evaluate_and_revert_expired(db)

        query = db.query(Personnel)

        if search:
            s = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Personnel.personnel_id.ilike(s),
                    Personnel.role.ilike(s),
                    Personnel.rank.ilike(s),
                    Personnel.posting.ilike(s),
                    Personnel.force.ilike(s),
                    Personnel.unit_id.ilike(s),
                )
            )

        if force:
            query = query.filter(Personnel.force == force)
        if unit_id:
            query = query.filter(Personnel.unit_id == unit_id)
        if status:
            query = query.filter(Personnel.status == status)
        if leave_status:
            query = query.filter(Personnel.leave_status == leave_status)

        total_count = query.count()
        personnel_records = query.order_by(Personnel.personnel_id.asc()).offset(skip).limit(limit).all()

        now = datetime.utcnow()
        result = []
        for p in personnel_records:
            # Active context details
            ctx = None
            if p.active_context_id:
                ctx = db.query(OperationalContext).filter(OperationalContext.id == p.active_context_id).first()
            
            # Post-leave calculation
            post_leave_day = None
            if p.leave_status == "POST_LEAVE_TRANSITION" and p.return_date:
                days_since_return = (now.date() - p.return_date.date()).days + 1
                post_leave_day = max(1, min(14, days_since_return))

            countdown_str, remaining_sec = format_remaining_duration(ctx.end_time if ctx else None)

            # Filter by zone / shift / duty if applied
            if zone and (not ctx or ctx.zone != zone):
                continue
            if shift and (not ctx or ctx.shift != shift):
                continue
            if duty and (not ctx or duty.lower() not in ctx.duty_type.lower()):
                continue

            item = {
                "id": p.id,
                "personnel_id": p.personnel_id,
                "user_id": p.user_id,
                "force": p.force,
                "unit_id": p.unit_id,
                "role": p.role,
                "rank": p.rank or p.role,
                "posting": p.posting,
                "status": p.status,
                "active_context_id": p.active_context_id,
                "current_zone": ctx.zone if ctx else "Zone 1",
                "current_duty": ctx.duty_type if ctx else "Standard Guard / Administrative",
                "current_shift": ctx.shift if ctx else "Day (08:00 - 16:00)",
                "current_location": ctx.location if ctx else p.posting,
                "current_environment": ctx.environment if ctx else "Standard",
                "is_temporary_deployment": bool(ctx and ctx.temporary),
                "remaining_duration_formatted": countdown_str,
                "remaining_seconds": remaining_sec,
                "assignment_end_time": ctx.end_time if ctx else None,
                "leave_status": p.leave_status,
                "post_leave_day_count": post_leave_day,
                "post_leave_total_days": 14,
                "return_date": p.return_date,
                "created_at": p.created_at,
                "updated_at": p.updated_at,
            }
            result.append(item)

        return result, total_count

    @staticmethod
    def get_personnel_profile(db: Session, personnel_id: str) -> Optional[Dict[str, Any]]:
        # Run automatic reversion evaluation first
        OperationsService.evaluate_and_revert_expired(db)

        p = db.query(Personnel).filter(
            or_(Personnel.personnel_id == personnel_id, Personnel.id == personnel_id)
        ).first()

        if not p:
            return None

        now = datetime.utcnow()
        active_ctx = None
        if p.active_context_id:
            active_ctx = db.query(OperationalContext).filter(OperationalContext.id == p.active_context_id).first()

        countdown_str, remaining_sec = format_remaining_duration(active_ctx.end_time if active_ctx else None)

        post_leave_day = None
        if p.leave_status == "POST_LEAVE_TRANSITION" and p.return_date:
            days_since_return = (now.date() - p.return_date.date()).days + 1
            post_leave_day = max(1, min(14, days_since_return))

        # Recent operational assignments
        recent_contexts = (
            db.query(OperationalContext)
            .filter(
                or_(
                    OperationalContext.personnel_id == p.personnel_id,
                    and_(OperationalContext.unit_id == p.unit_id, OperationalContext.personnel_id == None),
                )
            )
            .order_by(OperationalContext.created_at.desc())
            .limit(5)
            .all()
        )

        formatted_recent = []
        for c in recent_contexts:
            c_str, c_sec = format_remaining_duration(c.end_time)
            formatted_recent.append({
                "id": c.id,
                "name": c.name,
                "personnel_id": c.personnel_id,
                "unit_id": c.unit_id,
                "zone": c.zone,
                "duty_type": c.duty_type,
                "shift": c.shift,
                "location": c.location,
                "environment": c.environment,
                "start_time": c.start_time,
                "end_time": c.end_time,
                "temporary": c.temporary,
                "auto_revert": c.auto_revert,
                "status": c.status,
                "previous_context_snapshot": c.previous_context_snapshot,
                "notes": c.notes,
                "source": c.source,
                "created_at": c.created_at,
                "remaining_duration_formatted": c_str,
                "remaining_seconds": c_sec,
                "is_active": c.status == "ACTIVE" and (c_sec is None or c_sec > 0),
            })

        # Recent leave events
        leave_events = (
            db.query(LeaveEvent)
            .filter(LeaveEvent.personnel_id == p.personnel_id)
            .order_by(LeaveEvent.created_at.desc())
            .limit(5)
            .all()
        )

        return {
            "id": p.id,
            "personnel_id": p.personnel_id,
            "user_id": p.user_id,
            "force": p.force,
            "unit_id": p.unit_id,
            "role": p.role,
            "rank": p.rank or p.role,
            "posting": p.posting,
            "status": p.status,
            "active_context_id": p.active_context_id,
            "current_zone": active_ctx.zone if active_ctx else "Zone 1",
            "current_duty": active_ctx.duty_type if active_ctx else "Standard Guard / Administrative",
            "current_shift": active_ctx.shift if active_ctx else "Day (08:00 - 16:00)",
            "current_location": active_ctx.location if active_ctx else p.posting,
            "current_environment": active_ctx.environment if active_ctx else "Standard",
            "is_temporary_deployment": bool(active_ctx and active_ctx.temporary),
            "remaining_duration_formatted": countdown_str,
            "remaining_seconds": remaining_sec,
            "assignment_end_time": active_ctx.end_time if active_ctx else None,
            "leave_status": p.leave_status,
            "post_leave_day_count": post_leave_day,
            "post_leave_total_days": 14,
            "return_date": p.return_date,
            "created_at": p.created_at,
            "updated_at": p.updated_at,
            "active_context": formatted_recent[0] if formatted_recent else None,
            "recent_assignments": formatted_recent,
            "leave_events": leave_events,
        }

    @staticmethod
    def record_leave_return(
        db: Session,
        personnel_id: str,
        req: LeaveReturnRequest,
        actor: User,
    ) -> Dict[str, Any]:
        p = db.query(Personnel).filter(
            or_(Personnel.personnel_id == personnel_id, Personnel.id == personnel_id)
        ).first()

        if not p:
            raise ValueError(f"Personnel record with ID '{personnel_id}' not found.")

        now = datetime.utcnow()
        
        # 1. Create structured LeaveEvent record
        leave_event = LeaveEvent(
            personnel_id=p.personnel_id,
            leave_type=req.leave_type,
            leave_start_date=req.leave_end_date - timedelta(days=15),
            leave_end_date=req.leave_end_date,
            return_date=req.return_date,
            transition_days_total=14,
            status="ACTIVE_TRANSITION",
            recorded_by=actor.email,
            created_at=now,
        )
        db.add(leave_event)

        # 2. Update Personnel state
        p.leave_status = "POST_LEAVE_TRANSITION"
        p.leave_end_date = req.leave_end_date
        p.return_date = req.return_date
        p.transition_start_date = req.return_date
        p.status = "TRANSITION"

        # Calculate current transition day
        days_since = (now.date() - req.return_date.date()).days + 1
        current_day = max(1, min(14, days_since))

        # 3. Create Audit Record
        audit = AuditLog(
            actor_id=actor.email,
            actor_role=actor.role,
            action="RECORD_LEAVE_RETURN",
            object_type="Personnel",
            object_id=p.personnel_id,
            details={
                "personnel_id": p.personnel_id,
                "unit_id": p.unit_id,
                "leave_type": req.leave_type,
                "leave_end_date": req.leave_end_date.isoformat(),
                "return_date": req.return_date.isoformat(),
                "post_leave_day_count": current_day,
                "transition_window": "14 Days",
            },
            outcome="SUCCESS",
        )
        db.add(audit)
        db.commit()

        return {
            "status": "success",
            "message": f"Recorded return from leave for {p.personnel_id}. Post-leave transition activated (Day {current_day} / 14).",
            "personnel_id": p.personnel_id,
            "post_leave_day_count": current_day,
            "post_leave_total_days": 14,
            "leave_status": p.leave_status,
            "return_date": p.return_date,
        }
