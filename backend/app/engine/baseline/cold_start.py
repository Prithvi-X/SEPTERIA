"""Contextual Cohort Prior Initialization Engine (Cold-Start).

Provides temporary contextual cohort priors when an individual has insufficient historical data.
Configurable minimum history threshold (default: 3 observations).
Transitions smoothly to pure personal baseline as observations accumulate.
"""
from typing import Dict, Any, Optional

DEFAULT_MIN_OBSERVATIONS_THRESHOLD = 3

# Prototype cohort reference profiles across CAPF operational dimensions
# NOTE: These are heuristic prototype values for initialization only, not rigid clinical standards.
COHORT_PROFILES = {
    "BSF": {
        "hr": {"median": 72.0, "mad": 6.0, "p10": 60.0, "p90": 85.0},
        "hrv_rmssd": {"median": 52.0, "mad": 8.0, "p10": 38.0, "p90": 70.0},
        "resting_hr": {"median": 62.0, "mad": 4.0, "p10": 54.0, "p90": 72.0},
        "sleep_hours": {"median": 6.8, "mad": 0.8, "p10": 5.2, "p90": 8.0},
        "activity": {"median": 7500.0, "mad": 1500.0, "p10": 4500.0, "p90": 11000.0},
    },
    "CRPF": {
        "hr": {"median": 74.0, "mad": 6.5, "p10": 62.0, "p90": 88.0},
        "hrv_rmssd": {"median": 50.0, "mad": 7.5, "p10": 36.0, "p90": 68.0},
        "resting_hr": {"median": 64.0, "mad": 4.5, "p10": 56.0, "p90": 74.0},
        "sleep_hours": {"median": 6.5, "mad": 0.7, "p10": 5.0, "p90": 7.8},
        "activity": {"median": 8200.0, "mad": 1600.0, "p10": 5000.0, "p90": 12000.0},
    },
    "ITBP": {
        "hr": {"median": 76.0, "mad": 7.0, "p10": 64.0, "p90": 90.0},
        "hrv_rmssd": {"median": 48.0, "mad": 7.0, "p10": 34.0, "p90": 65.0},
        "resting_hr": {"median": 65.0, "mad": 5.0, "p10": 58.0, "p90": 76.0},
        "sleep_hours": {"median": 6.6, "mad": 0.8, "p10": 5.0, "p90": 7.9},
        "activity": {"median": 7800.0, "mad": 1800.0, "p10": 4200.0, "p90": 11500.0},
    },
    "DEFAULT": {
        "hr": {"median": 72.0, "mad": 6.0, "p10": 60.0, "p90": 85.0},
        "hrv_rmssd": {"median": 52.0, "mad": 8.0, "p10": 38.0, "p90": 70.0},
        "resting_hr": {"median": 62.0, "mad": 4.0, "p10": 54.0, "p90": 72.0},
        "sleep_hours": {"median": 7.0, "mad": 0.8, "p10": 5.5, "p90": 8.2},
        "activity": {"median": 7000.0, "mad": 1500.0, "p10": 4000.0, "p90": 10500.0},
    }
}

class ColdStartEngine:
    def __init__(self, min_observations: int = DEFAULT_MIN_OBSERVATIONS_THRESHOLD):
        self.min_observations = min_observations

    def is_cold_start(self, observation_count: int) -> bool:
        """Determines if the personnel member is in cold-start mode."""
        return observation_count < self.min_observations

    def get_cohort_prior(
        self,
        metric: str,
        force: Optional[str] = None,
        role: Optional[str] = None,
        zone: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Resolves contextual cohort prior metrics."""
        force_key = (force or "DEFAULT").upper()
        force_profile = COHORT_PROFILES.get(force_key, COHORT_PROFILES["DEFAULT"])
        
        metric_profile = force_profile.get(metric, COHORT_PROFILES["DEFAULT"].get(metric, {
            "median": 50.0,
            "mad": 5.0,
            "p10": 35.0,
            "p90": 70.0,
        }))
        
        # Environmental / Operational Zone Modifiers
        med_val = metric_profile["median"]
        mad_val = metric_profile["mad"]
        
        if zone and "Zone 1" in zone and metric == "hr":
            med_val += 4.0 # Slightly elevated operational pulse expectation
        elif zone and "Zone 2" in zone and metric == "sleep_hours":
            med_val -= 0.3 # Remote border environmental adaptation
            
        return {
            "median": round(med_val, 2),
            "mad": round(mad_val, 2),
            "p10": metric_profile["p10"],
            "p90": metric_profile["p90"],
            "mean": round(med_val, 2),
            "std": round(mad_val * 1.4826, 2),
            "observation_count": 0,
            "coverage_pct": 50.0,
            "quality_rating": "LOW",
            "is_cohort_prior": True,
            "provenance_note": f"Temporary contextual cohort prior for {force_key} under {zone or 'General Context'}. Will adapt as personal data accumulates.",
        }
