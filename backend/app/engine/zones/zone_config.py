"""Configuration-Driven Feature Focus for 3-Zone Operational Intelligence.

Defines analytical feature emphasis and priorities for each operational zone.
IMPORTANT: Operational zones are operational contexts, NOT risk rankings.
"""
from typing import Dict, Any

ZONE_FEATURE_CONFIGURATIONS: Dict[str, Dict[str, Any]] = {
    "Zone 1: High-Intensity / Active Operations": {
        "zone_code": "ZONE_1",
        "description": "High-intensity active operational deployment.",
        "primary_focus_features": [
            "acute_cardiovascular_load",
            "physical_activity_index",
            "immediate_recovery_opportunity",
            "shift_workload_manageability"
        ],
        "key_analytical_question": "Can the individual maintain operational readiness under acute tactical demands?",
        "feature_weights": {
            "activity_load": 0.35,
            "acute_hr_elevation": 0.30,
            "short_term_hrv": 0.20,
            "immediate_sleep": 0.15,
        },
        "exertion_rule_active": True,
    },
    "Zone 2: Border / Remote / Extreme Environment": {
        "zone_code": "ZONE_2",
        "description": "Extended border outpost or extreme environmental deployment (heat/altitude).",
        "primary_focus_features": [
            "cumulative_sleep_regularity",
            "multi_day_hrv_trend",
            "nocturnal_resting_hr",
            "deployment_duration_countdown",
            "environmental_thermal_altitude_strain"
        ],
        "key_analytical_question": "Is physiological recovery progressively deteriorating over extended deployment?",
        "feature_weights": {
            "sleep_regularity": 0.30,
            "multi_day_hrv_trend": 0.25,
            "resting_hr_elevation": 0.25,
            "environmental_friction": 0.20,
        },
        "exertion_rule_active": True,
    },
    "Zone 3: Critical Incident / Post-Incident Recovery": {
        "zone_code": "ZONE_3",
        "description": "Post-incident monitoring and autonomic stabilization window.",
        "primary_focus_features": [
            "incident_exposure_kinetics",
            "acute_physiological_response",
            "post_event_sleep_restoration",
            "post_event_hrv_recovery",
            "recovery_rebound_status"
        ],
        "key_analytical_question": "Did the individual return toward baseline equilibrium after critical incident exposure?",
        "feature_weights": {
            "recovery_rebound": 0.35,
            "post_event_hrv": 0.25,
            "post_event_sleep": 0.25,
            "resting_hr_stabilization": 0.15,
        },
        "exertion_rule_active": True,
    }
}
