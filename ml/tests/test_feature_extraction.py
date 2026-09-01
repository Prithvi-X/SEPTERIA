import os
import sys
import csv
import json
import numpy as np
import pytest

sys.path.insert(0, r"d:\IITM\SIH\PROTOTYPE\ANTIGRAVITY\ANTI-INFO")
from ml.src.features.feature_lib import (
    extract_cardiovascular_features,
    extract_hrv_features,
    extract_eda_features,
    extract_temperature_features,
    extract_accelerometry_features,
    extract_chest_respiration_features,
    extract_chest_emg_features
)

PROCESSED_DIR = r"d:\IITM\SIH\PROTOTYPE\ANTIGRAVITY\ANTI-INFO\ml\data\processed"

def test_cardiovascular_extraction_and_nan_fallback():
    # Valid HR
    hr = np.array([60.0, 65.0, 70.0, 75.0, 80.0])
    feats = extract_cardiovascular_features(hr, duration_sec=60.0)
    assert feats["hr_mean"] == 70.0
    assert feats["hr_min"] == 60.0
    assert feats["hr_max"] == 80.0
    assert feats["hr_std"] > 0
    assert feats["hr_slope"] > 0

    # Empty / corrupted HR must return np.nan (no synthetic defaults)
    empty_hr = np.array([])
    feats_empty = extract_cardiovascular_features(empty_hr)
    assert np.isnan(feats_empty["hr_mean"])
    assert np.isnan(feats_empty["hr_slope"])

def test_hrv_extraction_and_nan_fallback():
    # Regular 1000ms IBIs (20 beats) -> 0 rMSSD
    regular_ibi = np.full(20, 1000.0)
    feats_reg = extract_hrv_features(regular_ibi)
    assert feats_reg["hrv_rmssd"] == 0.0
    assert feats_reg["hrv_sdnn"] == 0.0
    
    # Alternating IBIs: 800, 900 repeated (20 beats) -> rmssd = 100
    alt_ibi = np.tile([800.0, 900.0], 10)
    feats_alt = extract_hrv_features(alt_ibi)
    assert pytest.approx(feats_alt["hrv_rmssd"], 0.1) == 100.0
    assert feats_alt["hrv_pnn50"] == 100.0

    # Missing / insufficient IBIs (<15 beats) must return np.nan (strict beat count threshold)
    few_ibis = np.array([800.0, 900.0, 850.0])
    feats_few = extract_hrv_features(few_ibis)
    assert np.isnan(feats_few["hrv_rmssd"])
    assert np.isnan(feats_few["hrv_sdnn"])

def test_eda_extraction_and_nan_fallback():
    t = np.linspace(0, 60, 240)
    eda = 2.0 + 0.01 * t + 0.5 * np.sin(2 * np.pi * 0.1 * t)
    feats = extract_eda_features(eda, fs=4.0, duration_sec=60.0)
    assert feats["eda_mean"] > 0.0
    assert feats["eda_tonic_mean"] > 0.0
    assert feats["eda_slope"] > 0.0
    assert isinstance(feats["eda_phasic_peaks"], int)

    # Disconnected sensor (0.0 uS) must return np.nan
    flat_eda = np.zeros(240)
    feats_flat = extract_eda_features(flat_eda, fs=4.0)
    assert np.isnan(feats_flat["eda_mean"])
    assert np.isnan(feats_flat["eda_tonic_mean"])

def test_chest_modality_absent_returns_nan():
    feats_resp = extract_chest_respiration_features(None)
    assert np.isnan(feats_resp["chest_resp_rate"])
    assert np.isnan(feats_resp["chest_resp_std"])

    feats_emg = extract_chest_emg_features(None)
    assert np.isnan(feats_emg["chest_emg_mean"])

def test_processed_files_exist():
    expected_files = [
        "wesad_features.csv",
        "wesad_multimodal_chest_features.csv",
        "physionet_features.csv",
        "catsa_features.csv",
        "train_features.csv",
        "val_features.csv",
        "test_internal_features.csv",
        "test_external_catsa_features.csv",
        "extraction_summary.json"
    ]
    for ef in expected_files:
        fp = os.path.join(PROCESSED_DIR, ef)
        assert os.path.exists(fp), f"Missing processed file: {ef}"
        assert os.path.getsize(fp) > 1000, f"File unexpectedly empty: {ef}"

def test_partitions_and_leakage_audit():
    summary_path = os.path.join(PROCESSED_DIR, "extraction_summary.json")
    with open(summary_path, "r", encoding="utf-8") as f:
        summary = json.load(f)
    
    assert summary["leakage_audit"]["zero_leakage_verified"] is True
    assert summary["partitions"]["train"]["total_windows"] == 6039
    assert summary["partitions"]["train"]["unique_subjects_count"] == 35
    assert summary["partitions"]["validation"]["total_windows"] == 1214
    assert summary["partitions"]["validation"]["unique_subjects_count"] == 8
    assert summary["partitions"]["internal_test"]["total_windows"] == 971
    assert summary["partitions"]["internal_test"]["unique_subjects_count"] == 8
    assert summary["partitions"]["external_catsa"]["total_windows"] == 1244
    assert summary["partitions"]["external_catsa"]["unique_subjects_count"] == 50

def test_feature_columns_and_modality_flags():
    train_csv = os.path.join(PROCESSED_DIR, "train_features.csv")
    with open(train_csv, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        
    assert "has_wrist_modality" in header
    assert "has_chest_modality" in header
    assert "chest_resp_rate" not in header # Wrist partition must not contain chest columns
