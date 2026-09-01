"""
SEPTERIA Tri-Layer Stress Integration & Gating Engine (Phase 6 / Step 5)
Implements:
  - Layer 1: Prototype ML Physiological Inference (XGBoost on 25 wearable features with native NaN routing)
  - Layer 2: Personal Baseline Robust Modulation, Exertion Disambiguation (No Hard Clamping), 3-Zone Decision Gating
  - Layer 3: Temporal Persistence (Anti-Spike Filter), Data Quality Gating, 4-Tier Welfare State & Advisory Actions
"""

import os
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
import numpy as np
import joblib

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
MODELS_DIR = os.path.join(BASE_DIR, "ml", "models")
DEFAULT_MODEL_PATH = os.path.join(MODELS_DIR, "xgboost_stress_model.joblib")

WRIST_CORE_FEATURES = [
    "hr_mean", "hr_std", "hr_min", "hr_max", "hr_slope",
    "hrv_rmssd", "hrv_sdnn", "hrv_pnn50", "hrv_cv",
    "eda_mean", "eda_std", "eda_min", "eda_max", "eda_slope",
    "eda_tonic_mean", "eda_phasic_peaks", "eda_phasic_max_amplitude", "eda_phasic_auc",
    "temp_mean", "temp_std", "temp_slope",
    "acc_magnitude_mean", "acc_magnitude_std", "acc_motion_energy", "acc_peak_acceleration"
]

@dataclass
class TriLayerConfig:
    """
    Configurable parameters for Tri-Layer Stress & Welfare Gating Engine.
    All values are provisional prototype heuristics requiring field calibration.
    """
    # Layer 2: Kinetic Exertion Disambiguation (Provisional Parameters)
    exertion_motion_energy_threshold: float = 2.0
    exertion_magnitude_std_threshold: float = 1.5
    exertion_attribution_discount: float = 0.40  # Discount on raw P_physio attribution during exertion
    
    # Layer 2: Personal Baseline Modulation (Provisional Parameters)
    baseline_dampening_factor: float = 0.60
    baseline_autonomic_z_normal_cutoff: float = 0.50
    baseline_amplification_slope: float = 0.20
    baseline_autonomic_z_elevated_cutoff: float = 1.50
    
    # Layer 2: 3-Zone Operational Decision Gates (Provisional Gating Parameters)
    zone_1_decision_threshold: float = 0.60      # High-Intensity / Active Operations
    zone_2_decision_threshold: float = 0.50      # Border / Remote / Extreme Environment
    zone_3_base_threshold: float = 0.50          # Critical Incident base threshold
    zone_3_min_threshold: float = 0.30           # Critical Incident sensitivity lower bound
    zone_3_recovery_debt_weight: float = 0.002   # Sensitivity adjustment weight per burden point
    zone_3_sleep_deficit_weight: float = 0.03    # Sensitivity adjustment weight per deficit hour
    
    # Layer 3: Temporal Persistence (Anti-Spike Rule)
    persistence_required_windows: int = 2        # K windows required above decision gate
    persistence_window_history_size: int = 3     # N total recent windows evaluated
    
    # Layer 3: Data Quality & Action Confidence Gating
    min_data_quality_for_action: float = 0.50
    contradiction_penalty_factor: float = 0.50
    cooldown_period_minutes: int = 30
    
    # Model Metadata
    model_version: str = "v1.0.0-PROTOTYPE"
    model_designation: str = "Prototype Stress Model - Robustness Candidate"

class TriLayerStressEngine:
    """
    Modular Engine coordinating Layer 1 ML inference, Layer 2 personal & zone context, and Layer 3 decision gating.
    """
    def __init__(self, model_path: Optional[str] = None, config: Optional[TriLayerConfig] = None):
        self.config = config or TriLayerConfig()
        self.model_path = model_path or DEFAULT_MODEL_PATH
        self.model = None
        self._load_model()
        
    def _load_model(self):
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
            except Exception as e:
                self.model = None
        else:
            self.model = None

    def calculate_data_quality(self, features: Dict[str, Any]) -> Tuple[float, bool]:
        """
        Calculates telemetry data quality score Q_data in [0.0, 1.0] and checks for contradictory evidence.
        """
        total_checks = 5
        passed_checks = 0
        is_contradictory = False
        
        # Check 1: Heart Rate in physiological bounds
        hr = features.get("hr_mean", np.nan)
        if not np.isnan(hr) and 30.0 <= hr <= 220.0:
            passed_checks += 1
            
        # Check 2: Skin temperature in physiological bounds
        temp = features.get("temp_mean", np.nan)
        if not np.isnan(temp) and 20.0 <= temp <= 45.0:
            passed_checks += 1
            
        # Check 3: EDA contact check
        eda = features.get("eda_mean", np.nan)
        if not np.isnan(eda) and eda >= 0.005:
            passed_checks += 1
            
        # Check 4: ACC vector present
        acc_mag = features.get("acc_magnitude_mean", np.nan)
        if not np.isnan(acc_mag) and acc_mag > 0.0:
            passed_checks += 1
            
        # Check 5: HRV / PRV availability
        hrv = features.get("hrv_rmssd", np.nan)
        if not np.isnan(hrv) and hrv > 0.0:
            passed_checks += 1
            
        q_score = round(passed_checks / total_checks, 2)
        
        # Contradiction check: extreme HR elevation with zero EDA conductance and zero motion
        acc_energy = features.get("acc_motion_energy", np.nan)
        if not np.isnan(hr) and not np.isnan(eda) and not np.isnan(acc_energy):
            if hr > 115.0 and eda < 0.02 and acc_energy < 0.05:
                is_contradictory = True
                
        return q_score, is_contradictory

    def extract_feature_vector(self, features: Dict[str, Any]) -> np.ndarray:
        """
        Converts feature dictionary to 1x25 float64 numpy array in canonical order.
        Missing / invalid entries are strictly np.nan.
        """
        vec = []
        for f in WRIST_CORE_FEATURES:
            val = features.get(f, np.nan)
            if val is None or val == "" or str(val).lower() == "nan":
                vec.append(np.nan)
            else:
                try:
                    vec.append(float(val))
                except (ValueError, TypeError):
                    vec.append(np.nan)
        return np.array([vec], dtype=np.float64)

    def evaluate_layer_1_ml(self, features: Dict[str, Any]) -> Tuple[float, float, bool]:
        """
        Layer 1: ML Physiological Inference Core.
        Returns: (raw_p_physio, data_quality_score, is_contradictory)
        """
        q_data, is_contradictory = self.calculate_data_quality(features)
        
        if self.model is None:
            # Fallback heuristic if model file is unavailable
            hr = features.get("hr_mean", 75.0)
            p_fallback = float(np.clip((hr - 60.0) / 60.0, 0.0, 1.0)) if not np.isnan(hr) else 0.50
            return p_fallback, q_data, is_contradictory
            
        feat_vec = self.extract_feature_vector(features)
        try:
            # XGBoost native NaN routing
            probs = self.model.predict_proba(feat_vec)
            p_physio = float(probs[0, 1])
        except Exception:
            p_physio = 0.50
            
        return round(p_physio, 4), q_data, is_contradictory

    def evaluate_layer_2_context(
        self,
        p_physio: float,
        features: Dict[str, Any],
        personal_baseline: Optional[Dict[str, Any]],
        operational_zone: str,
        recovery_burden_score: float = 0.0,
        sleep_deficit_hours: float = 0.0,
        trajectory_direction: str = "STABLE"
    ) -> Dict[str, Any]:
        """
        Layer 2: Personal Baseline & 3-Zone Context Intelligence.
        Performs exertion disambiguation (no hard clamp), personal baseline robust modulation, and zone gating.
        """
        # 1. Kinetic Exertion Disambiguation
        acc_energy = features.get("acc_motion_energy", 0.0)
        acc_std = features.get("acc_magnitude_std", 0.0)
        acc_energy = 0.0 if np.isnan(acc_energy) else acc_energy
        acc_std = 0.0 if np.isnan(acc_std) else acc_std
        
        is_exertion = (
            acc_energy >= self.config.exertion_motion_energy_threshold or
            acc_std >= self.config.exertion_magnitude_std_threshold
        )
        
        if is_exertion:
            # Discount physiological stress attribution without hard-clamping
            p_exertion = p_physio * (1.0 - self.config.exertion_attribution_discount)
            exertion_tag = "PHYSICAL_EXERTION_ACTIVE"
        else:
            p_exertion = p_physio
            exertion_tag = "STATIONARY_SEDENTARY"
            
        # 2. Personal Baseline Robust z-Score Modulation
        baseline = personal_baseline or {}
        med_hr = baseline.get("hr_median", 75.0)
        mad_hr = max(baseline.get("hr_mad", 2.0), 1.0)
        med_rmssd = baseline.get("rmssd_median", 50.0)
        mad_rmssd = max(baseline.get("rmssd_mad", 5.0), 1.0)
        med_eda = max(baseline.get("eda_median", 1.0), 0.05)
        
        hr_val = features.get("hr_mean", med_hr)
        rmssd_val = features.get("hrv_rmssd", med_rmssd)
        eda_val = features.get("eda_tonic_mean", med_eda)
        
        hr_val = med_hr if np.isnan(hr_val) else hr_val
        rmssd_val = med_rmssd if np.isnan(rmssd_val) else rmssd_val
        eda_val = med_eda if np.isnan(eda_val) else eda_val
        
        z_hr = 0.6745 * (hr_val - med_hr) / mad_hr
        z_rmssd = 0.6745 * (rmssd_val - med_rmssd) / mad_rmssd
        r_eda = eda_val / med_eda
        
        # Composite autonomic strain deviation
        z_autonomic = (z_hr - z_rmssd + max(0.0, r_eda - 1.0) * 2.0) / 3.0
        
        if z_autonomic <= self.config.baseline_autonomic_z_normal_cutoff:
            p_baseline = p_exertion * self.config.baseline_dampening_factor
            baseline_status = "WITHIN_NORMAL_BASELINE"
        elif z_autonomic >= self.config.baseline_autonomic_z_elevated_cutoff:
            p_baseline = min(1.0, p_exertion * (1.0 + self.config.baseline_amplification_slope * z_autonomic))
            baseline_status = "ELEVATED_AUTONOMIC_STRAIN"
        else:
            p_baseline = p_exertion
            baseline_status = "MODERATE_BASELINE_DEVIATION"
            
        p_calibrated = round(float(np.clip(p_baseline, 0.0, 1.0)), 4)
        
        # 3. 3-Zone Operational Decision Gates
        zone_str = operational_zone.upper()
        if "ZONE_1" in zone_str or "ACTIVE" in zone_str:
            zone_code = "ZONE_1"
            zone_name = "Zone 1: High-Intensity / Active Operations"
            decision_gate = self.config.zone_1_decision_threshold
            zone_insight = "High-intensity active operational deployment; kinetic exertion is filtered and high specificity is prioritized."
        elif "ZONE_3" in zone_str or "CRITICAL" in zone_str or "INCIDENT" in zone_str:
            zone_code = "ZONE_3"
            zone_name = "Zone 3: Critical Incident / Post-Incident Recovery"
            # Bounded evidence-based dynamic decision gate
            dynamic_t = (
                self.config.zone_3_base_threshold -
                (self.config.zone_3_recovery_debt_weight * recovery_burden_score) -
                (self.config.zone_3_sleep_deficit_weight * sleep_deficit_hours)
            )
            decision_gate = round(float(np.clip(dynamic_t, self.config.zone_3_min_threshold, self.config.zone_3_base_threshold)), 4)
            zone_insight = "Critical incident recovery monitoring; decision sensitivity is dynamically adjusted by cumulative recovery debt and sleep deficit."
        else: # Default Zone 2
            zone_code = "ZONE_2"
            zone_name = "Zone 2: Border / Remote / Extreme Environment"
            decision_gate = self.config.zone_2_decision_threshold
            zone_insight = "Extended border or remote outpost deployment; tracking multi-day trajectory and sleep debt equilibrium."
            
        return {
            "p_calibrated": p_calibrated,
            "is_physical_exertion": is_exertion,
            "exertion_tag": exertion_tag,
            "baseline_status": baseline_status,
            "z_autonomic": round(float(z_autonomic), 4),
            "z_hr": round(float(z_hr), 4),
            "z_rmssd": round(float(z_rmssd), 4),
            "r_eda": round(float(r_eda), 4),
            "operational_zone_code": zone_code,
            "operational_zone_name": zone_name,
            "decision_gate_threshold": decision_gate,
            "zone_insight": zone_insight
        }

    def evaluate_layer_3_decision(
        self,
        p_calibrated: float,
        decision_gate: float,
        data_quality: float,
        is_contradictory: bool,
        is_exertion: bool,
        recent_window_probabilities: List[float],
        recovery_burden_score: float = 0.0,
        trajectory_direction: str = "STABLE"
    ) -> Dict[str, Any]:
        """
        Layer 3: Decision Gating, Temporal Persistence & Human-in-the-Loop Safeguards.
        """
        # 1. Action Confidence Gating
        penalty = self.config.contradiction_penalty_factor if is_contradictory else 0.0
        action_confidence = round(float(np.clip(data_quality * (1.0 - penalty), 0.0, 1.0)), 4)
        
        if action_confidence < self.config.min_data_quality_for_action:
            return {
                "welfare_state": "INCONCLUSIVE_DATA",
                "state_color": "GREY",
                "action_confidence": action_confidence,
                "is_escalated": False,
                "recommended_action": "Telemetry quality insufficient for alert escalation; maintain passive monitoring and check sensor fit.",
                "human_intervention_required": False,
                "temporal_persistence_met": False
            }
            
        # 2. Temporal Persistence Gate (K of N windows)
        all_windows = recent_window_probabilities + [p_calibrated]
        eval_window = all_windows[-self.config.persistence_window_history_size:]
        windows_above_gate = sum(1 for p in eval_window if p >= decision_gate)
        persistence_met = windows_above_gate >= self.config.persistence_required_windows
        
        # 3. Multi-Tier Welfare State Classification
        # Physical Exertion Rule: Pure physiological elevation during exertion cannot trigger AMBER/RED without high recovery debt
        if is_exertion and recovery_burden_score < 50.0:
            welfare_state = "GREEN"
            state_color = "GREEN"
            recommended_action = "Normal physiological elevation consistent with active physical exertion; recovery equilibrium maintained."
            is_escalated = False
            human_req = False
        elif p_calibrated < decision_gate:
            welfare_state = "GREEN"
            state_color = "GREEN"
            recommended_action = "Physiological homeostasis within personal operational limits; routine monitoring."
            is_escalated = False
            human_req = False
        elif not persistence_met:
            # Single transient elevation
            welfare_state = "YELLOW"
            state_color = "YELLOW"
            recommended_action = "Transient physiological elevation observed; continue routine unit monitoring."
            is_escalated = False
            human_req = False
        else:
            # Persistent elevation above decision gate
            if trajectory_direction == "DETERIORATING" and recovery_burden_score >= 70.0:
                welfare_state = "RED"
                state_color = "RED"
                recommended_action = "Recommend authorized welfare/medical review by Unit Medical Officer / Psychologist (Sustained autonomic strain + deteriorating trajectory)."
                is_escalated = True
                human_req = True
            elif recovery_burden_score >= 50.0 or trajectory_direction == "DETERIORATING":
                welfare_state = "AMBER"
                state_color = "AMBER"
                recommended_action = "Recommend authorized unit welfare check by designated peer / section commander (Sustained autonomic elevation + elevated recovery debt)."
                is_escalated = True
                human_req = True
            else:
                welfare_state = "YELLOW"
                state_color = "YELLOW"
                recommended_action = "Sustained physiological elevation within manageable recovery bounds; ensure adequate rest opportunity."
                is_escalated = False
                human_req = False
                
        return {
            "welfare_state": welfare_state,
            "state_color": state_color,
            "action_confidence": action_confidence,
            "is_escalated": is_escalated,
            "recommended_action": recommended_action,
            "human_intervention_required": human_req,
            "temporal_persistence_met": persistence_met,
            "windows_above_gate_count": windows_above_gate,
            "total_windows_evaluated": len(eval_window)
        }

    def evaluate_window(
        self,
        features: Dict[str, Any],
        personnel_id: Optional[str] = None,
        personal_baseline: Optional[Dict[str, Any]] = None,
        operational_zone: str = "ZONE_2",
        recovery_burden_score: float = 0.0,
        sleep_deficit_hours: float = 0.0,
        trajectory_direction: str = "STABLE",
        recent_window_probabilities: Optional[List[float]] = None
    ) -> Dict[str, Any]:
        """
        Complete end-to-end evaluation pipeline coordinating Layer 1, Layer 2, and Layer 3.
        """
        recent_probs = recent_window_probabilities or []
        
        # Layer 1: ML Physiological Inference Core
        p_physio, q_data, is_contradictory = self.evaluate_layer_1_ml(features)
        
        # Layer 2: Personal Baseline & 3-Zone Context Intelligence
        layer_2_res = self.evaluate_layer_2_context(
            p_physio=p_physio,
            features=features,
            personal_baseline=personal_baseline,
            operational_zone=operational_zone,
            recovery_burden_score=recovery_burden_score,
            sleep_deficit_hours=sleep_deficit_hours,
            trajectory_direction=trajectory_direction
        )
        
        # Layer 3: Decision Gating & Human-in-the-Loop Action Protocol
        layer_3_res = self.evaluate_layer_3_decision(
            p_calibrated=layer_2_res["p_calibrated"],
            decision_gate=layer_2_res["decision_gate_threshold"],
            data_quality=q_data,
            is_contradictory=is_contradictory,
            is_exertion=layer_2_res["is_physical_exertion"],
            recent_window_probabilities=recent_probs,
            recovery_burden_score=recovery_burden_score,
            trajectory_direction=trajectory_direction
        )
        
        # Assemble complete explainability payload
        return {
            "personnel_id": personnel_id,
            "engine_metadata": {
                "model_version": self.config.model_version,
                "model_designation": self.config.model_designation,
                "is_capf_field_validated": False,
                "regulatory_note": "Research Prototype Decision Support; Not an autonomous clinical diagnostic tool."
            },
            "layer_1_physiological_ml": {
                "raw_physiological_stress_probability": p_physio,
                "data_quality_score": q_data,
                "contradictory_telemetry_detected": is_contradictory
            },
            "layer_2_context_interpretation": layer_2_res,
            "layer_3_welfare_decision": layer_3_res
        }
