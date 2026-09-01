"""3-Zone Operational Intelligence Engine for SEPTERIA.

Evaluates personal state conditioned on authoritative operational zone context.
Zones are operational contexts, NOT risk levels.
"""
from typing import Dict, Any, Optional
from .zone_config import ZONE_FEATURE_CONFIGURATIONS

class ZoneIntelligenceEngine:
    @staticmethod
    def get_zone_config(zone_name: str) -> Dict[str, Any]:
        """Retrieves configuration for a specific zone."""
        for name, config in ZONE_FEATURE_CONFIGURATIONS.items():
            if zone_name in name or config["zone_code"] == zone_name:
                return config
        # Default fallback to Zone 2
        return ZONE_FEATURE_CONFIGURATIONS["Zone 2: Border / Remote / Extreme Environment"]

    @classmethod
    def evaluate_zone_context(
        cls,
        operational_zone: str,
        deviations: Dict[str, Any],
        trajectories: Dict[str, Any],
        recovery_debt: Dict[str, Any],
        motion_context: str = "MODERATE",
    ) -> Dict[str, Any]:
        """Evaluates personal state conditioned on zone context."""
        config = cls.get_zone_config(operational_zone)
        zone_code = config["zone_code"]
        
        # Zone-conditioned contextual evaluation
        insights = []
        if zone_code == "ZONE_1":
            if motion_context in ("HIGH", "EXERTIONAL"):
                insights.append("Tactical active exertion expected in Zone 1; physiological elevation is consistent with mission demands.")
            else:
                insights.append("Zone 1 Active Ops monitoring focus: acute load vs immediate resting opportunity.")
        elif zone_code == "ZONE_2":
            sleep_dev = deviations.get("sleep", {})
            if sleep_dev.get("sleep_deficit_hours", 0) > 1.0:
                insights.append("Zone 2 cumulative sleep debt detected under extended border/environmental deployment.")
            else:
                insights.append("Zone 2 recovery equilibrium stable across extended deployment window.")
        elif zone_code == "ZONE_3":
            insights.append("Zone 3 Post-Incident Monitoring: tracking cardiovascular return toward personal baseline.")

        return {
            "operational_zone": operational_zone,
            "zone_code": zone_code,
            "key_analytical_question": config["key_analytical_question"],
            "primary_features": config["primary_focus_features"],
            "zone_specific_insights": insights,
            "is_risk_level": False,
            "methodology_note": "Operational zones define contextual expectations, not psychological or medical risk levels.",
        }
