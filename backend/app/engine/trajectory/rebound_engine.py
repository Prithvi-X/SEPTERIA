"""Recovery Rebound vs. Persistent Deviation Engine.

Distinguishes expected acute event kinetics from persistent post-event recovery failure.
Example:
- Critical Incident -> Acute HR elevation -> returns to baseline within 6-24h -> "Recovery rebound observed."
- Critical Incident -> Acute HR elevation -> persistent HR elevation & HRV suppression > 24h -> "Persistent post-incident recovery deviation."
"""
from typing import Dict, Any, Optional

class RecoveryReboundEngine:
    @staticmethod
    def evaluate_rebound(
        incident_occurred: bool,
        hours_since_incident: float,
        current_hr: float,
        current_hrv: float,
        baseline_hr: float,
        baseline_hrv: float,
        baseline_hrv_mad: float,
    ) -> Dict[str, Any]:
        """Evaluates recovery rebound kinetics following an operational incident or exertion event."""
        if not incident_occurred:
            return {
                "rebound_status": "NONE",
                "is_rebound": False,
                "is_persistent_deviation": False,
                "explanation": "No recent critical incident or acute overload event recorded.",
            }

        hr_elevation = current_hr - baseline_hr
        hrv_deficit = baseline_hrv - current_hrv
        hrv_mad_floor = max(baseline_hrv_mad, 2.0)

        if hours_since_incident <= 24.0:
            # Within 24 hours: Check if metrics are returning toward baseline
            if hr_elevation <= 8.0 and hrv_deficit <= (1.5 * hrv_mad_floor):
                return {
                    "rebound_status": "REBOUND_OBSERVED",
                    "is_rebound": True,
                    "is_persistent_deviation": False,
                    "explanation": f"Recovery rebound observed: post-event cardiovascular telemetry returned toward baseline within {hours_since_incident:.1f} hours.",
                }
            else:
                return {
                    "rebound_status": "ACUTE_RECOVERY_IN_PROGRESS",
                    "is_rebound": False,
                    "is_persistent_deviation": False,
                    "explanation": f"Acute post-incident recovery in progress ({hours_since_incident:.1f}h post-event).",
                }
        else:
            # Greater than 24 hours post-incident
            if hr_elevation > 10.0 or hrv_deficit > (2.0 * hrv_mad_floor):
                return {
                    "rebound_status": "PERSISTENT_DEVIATION",
                    "is_rebound": False,
                    "is_persistent_deviation": True,
                    "explanation": f"Persistent post-incident recovery deviation: physiological suppression continues {hours_since_incident:.1f} hours post-event.",
                }
            else:
                return {
                    "rebound_status": "REBOUND_RESOLVED",
                    "is_rebound": True,
                    "is_persistent_deviation": False,
                    "explanation": "Post-incident recovery stabilization achieved.",
                }
