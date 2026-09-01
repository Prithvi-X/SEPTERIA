"""
Unit tests for SEPTERIA Phase 6 Trained Model Artifacts and Inference Pipeline.
"""

import os
import csv
import json
import joblib
import numpy as np
import pytest
import xgboost as xgb

MODELS_DIR = r"d:\IITM\SIH\PROTOTYPE\ANTIGRAVITY\ANTI-INFO\ml\models"
RESULTS_DIR = r"d:\IITM\SIH\PROTOTYPE\ANTIGRAVITY\ANTI-INFO\ml\results"
PROCESSED_DIR = r"d:\IITM\SIH\PROTOTYPE\ANTIGRAVITY\ANTI-INFO\ml\data\processed"

WRIST_CORE_FEATURES = [
    "hr_mean", "hr_std", "hr_min", "hr_max", "hr_slope",
    "hrv_rmssd", "hrv_sdnn", "hrv_pnn50", "hrv_cv",
    "eda_mean", "eda_std", "eda_min", "eda_max", "eda_slope",
    "eda_tonic_mean", "eda_phasic_peaks", "eda_phasic_max_amplitude", "eda_phasic_auc",
    "temp_mean", "temp_std", "temp_slope",
    "acc_magnitude_mean", "acc_magnitude_std", "acc_motion_energy", "acc_peak_acceleration"
]

def test_model_artifacts_exist():
    expected_files = [
        os.path.join(MODELS_DIR, "xgboost_stress_model.json"),
        os.path.join(MODELS_DIR, "xgboost_stress_model.joblib"),
        os.path.join(MODELS_DIR, "feature_preprocessor.joblib"),
        os.path.join(RESULTS_DIR, "evaluation_metrics.json")
    ]
    for fp in expected_files:
        assert os.path.exists(fp), f"Missing artifact: {fp}"
        assert os.path.getsize(fp) > 500, f"Artifact file too small: {fp}"

def test_model_loading_and_empirical_inference():
    model = joblib.load(os.path.join(MODELS_DIR, "xgboost_stress_model.joblib"))
    
    with open(os.path.join(PROCESSED_DIR, "test_internal_features.csv"), "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
        
    def to_feat_vec(r):
        vals = []
        for feat in WRIST_CORE_FEATURES:
            v = r.get(feat, "")
            if v == "" or v is None or v.lower() == "nan":
                vals.append(np.nan)
            else:
                vals.append(float(v))
        return np.array([vals], dtype=np.float64)

    baseline_rows = [r for r in rows if r.get("source_label") in ["1", "4"]]
    stress_rows = [r for r in rows if r.get("source_label") in ["2", "STRESS_TASK"]]
    exercise_rows = [r for r in rows if r.get("source_label") in ["AEROBIC_CYCLE", "ANAEROBIC_SPRINT"]]
    
    assert len(baseline_rows) > 0
    assert len(stress_rows) > 0
    assert len(exercise_rows) > 0
    
    p_base_mean = np.mean([model.predict_proba(to_feat_vec(r))[0, 1] for r in baseline_rows])
    p_stress_mean = np.mean([model.predict_proba(to_feat_vec(r))[0, 1] for r in stress_rows])
    p_ex_mean = np.mean([model.predict_proba(to_feat_vec(r))[0, 1] for r in exercise_rows])
    
    assert 0.0 <= p_base_mean <= 1.0
    assert 0.0 <= p_stress_mean <= 1.0
    assert 0.0 <= p_ex_mean <= 1.0
    
    # Core physiological hypotheses
    assert p_stress_mean > p_base_mean, "Stress protocol windows must show higher mean P(Stress) than resting baseline"
    assert p_ex_mean < 0.30, "Physical exertion windows must maintain low average P(Stress)"

def test_native_nan_handling():
    model = joblib.load(os.path.join(MODELS_DIR, "xgboost_stress_model.joblib"))
    
    # Mock window with NaNs in HRV
    window_with_nan = np.full((1, len(WRIST_CORE_FEATURES)), 1.0)
    window_with_nan[0, 5:9] = np.nan # HRV columns as NaN
    
    probs = model.predict_proba(window_with_nan)
    assert not np.isnan(probs[0, 0])
    assert not np.isnan(probs[0, 1])
    assert 0.0 <= probs[0, 1] <= 1.0

def test_evaluation_metrics_validity():
    results_path = os.path.join(RESULTS_DIR, "evaluation_metrics.json")
    with open(results_path, "r", encoding="utf-8") as f:
        metrics = json.load(f)
        
    xgb_test = metrics["internal_test_set_evaluation"]["xgboost"]
    assert xgb_test["accuracy"] > 0.75
    assert xgb_test["balanced_accuracy"] > 0.75
    assert xgb_test["roc_auc"] > 0.80
    assert xgb_test["specificity"] > 0.75
    assert xgb_test["recall_sensitivity"] > 0.70
