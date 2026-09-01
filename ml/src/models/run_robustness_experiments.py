"""
SEPTERIA Controlled Robustness Experiments (Models A, B, C)
Model A: Physiological-Only Baseline (25 wearable features)
Model B: Physiological + Personal-Baseline / Subject-Normalized Deviation Features (32 features)
Model C: Physiological + Personal-Baseline + SEPTERIA Contextual Features (38 features)

Strict Protocol:
- Train strictly on 35 training subjects (11 WESAD + 24 PhysioNet)
- Early stopping & hyperparameter tuning on 8 validation subjects (2 WESAD + 6 PhysioNet)
- Evaluate on 8 unchanged internal test subjects (2 WESAD + 6 PhysioNet)
- Evaluate CATSA (50 subjects) strictly as an untouched external benchmark (Zero CATSA tuning)
"""

import os
import sys
import json
import csv
from collections import defaultdict
import numpy as np
import scipy.stats as stats
import joblib
import xgboost as xgb
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
    brier_score_loss
)
from sklearn.calibration import calibration_curve

PROCESSED_DIR = r"d:\IITM\SIH\PROTOTYPE\ANTIGRAVITY\ANTI-INFO\ml\data\processed"
RESULTS_DIR = r"d:\IITM\SIH\PROTOTYPE\ANTIGRAVITY\ANTI-INFO\ml\results"
MODELS_DIR = r"d:\IITM\SIH\PROTOTYPE\ANTIGRAVITY\ANTI-INFO\ml\models"

WRIST_CORE_FEATURES = [
    "hr_mean", "hr_std", "hr_min", "hr_max", "hr_slope",
    "hrv_rmssd", "hrv_sdnn", "hrv_pnn50", "hrv_cv",
    "eda_mean", "eda_std", "eda_min", "eda_max", "eda_slope",
    "eda_tonic_mean", "eda_phasic_peaks", "eda_phasic_max_amplitude", "eda_phasic_auc",
    "temp_mean", "temp_std", "temp_slope",
    "acc_magnitude_mean", "acc_magnitude_std", "acc_motion_energy", "acc_peak_acceleration"
]

PERSONAL_BASELINE_FEATURES = [
    "dev_hr_abs",
    "dev_hr_robust_z",
    "dev_hrv_rmssd_abs",
    "dev_hrv_rmssd_robust_z",
    "dev_eda_tonic_ratio",
    "dev_eda_tonic_diff",
    "dev_temp_diff"
]

SEPTERIA_CONTEXT_FEATURES = [
    "context_zone_active_ops",
    "context_is_night_shift",
    "context_post_leave_day",
    "recovery_burden_score",
    "sleep_deficit_hours",
    "trajectory_direction_hrv"
]

def load_csv(fname):
    with open(os.path.join(PROCESSED_DIR, fname), "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def compute_subject_baselines(rows):
    """
    Computes personal baseline statistics (median, MAD) for each subject strictly from their own baseline/resting windows.
    Zero cross-subject leakage.
    """
    subject_windows = defaultdict(list)
    for r in rows:
        s = f"{r.get('dataset', '')}_{r.get('subject_id', '').split('_')[0]}"
        subject_windows[s].append(r)
        
    baselines = {}
    for s, s_rows in subject_windows.items():
        # Identify resting baseline windows
        base_rows = []
        for r in s_rows:
            label = str(r.get("source_label", r.get("condition", "")))
            if label in ["1", "Baseline", "STRESS_BASELINE", "4"]:
                base_rows.append(r)
                
        # If no explicit label match, use the first 2 windows (initial rest)
        if len(base_rows) == 0:
            base_rows = s_rows[:min(2, len(s_rows))]
            
        def extract_vals(f_name):
            vals = []
            for r in base_rows:
                v = r.get(f_name, "")
                if v != "" and v is not None and v.lower() != "nan":
                    try:
                        vals.append(float(v))
                    except ValueError:
                        pass
            return np.array(vals) if len(vals) > 0 else np.array([np.nan])
            
        hr_b = extract_vals("hr_mean")
        rmssd_b = extract_vals("hrv_rmssd")
        eda_b = extract_vals("eda_tonic_mean")
        temp_b = extract_vals("temp_mean")
        
        def med_mad(arr, default_med=75.0, min_mad=1.0):
            valid = arr[~np.isnan(arr)]
            if len(valid) == 0:
                return default_med, min_mad
            med = float(np.median(valid))
            mad = float(np.median(np.abs(valid - med)))
            return med, max(mad, min_mad)
            
        med_hr, mad_hr = med_mad(hr_b, 75.0, 2.0)
        med_rmssd, mad_rmssd = med_mad(rmssd_b, 50.0, 5.0)
        med_eda, mad_eda = med_mad(eda_b, 1.0, 0.1)
        med_temp, mad_temp = med_mad(temp_b, 33.0, 0.2)
        
        baselines[s] = {
            "hr": (med_hr, mad_hr),
            "rmssd": (med_rmssd, mad_rmssd),
            "eda": (med_eda, mad_eda),
            "temp": (med_temp, mad_temp)
        }
    return baselines

def enrich_rows_with_features(rows, baselines):
    """
    Computes Personal Baseline Deviations (Model B) and SEPTERIA Operational Context (Model C).
    """
    enriched = []
    # Track sequential windows per subject for trajectory calculation
    subject_history = defaultdict(list)
    
    for r in rows:
        s = f"{r.get('dataset', '')}_{r.get('subject_id', '').split('_')[0]}"
        b_info = baselines.get(s, {
            "hr": (75.0, 2.0),
            "rmssd": (50.0, 5.0),
            "eda": (1.0, 0.1),
            "temp": (33.0, 0.2)
        })
        
        row_dict = dict(r)
        
        # 1. Base physiological values
        def get_val(f_name, default=np.nan):
            v = r.get(f_name, "")
            if v == "" or v is None or v.lower() == "nan":
                return np.nan
            try:
                return float(v)
            except ValueError:
                return default
                
        hr_val = get_val("hr_mean")
        rmssd_val = get_val("hrv_rmssd")
        eda_val = get_val("eda_tonic_mean")
        temp_val = get_val("temp_mean")
        
        # 2. Personal Baseline Deviations (Model B)
        med_hr, mad_hr = b_info["hr"]
        med_rmssd, mad_rmssd = b_info["rmssd"]
        med_eda, mad_eda = b_info["eda"]
        med_temp, mad_temp = b_info["temp"]
        
        dev_hr_abs = hr_val - med_hr if not np.isnan(hr_val) else np.nan
        dev_hr_z = (0.6745 * (hr_val - med_hr) / mad_hr) if not np.isnan(hr_val) else np.nan
        
        dev_rmssd_abs = rmssd_val - med_rmssd if not np.isnan(rmssd_val) else np.nan
        dev_rmssd_z = (0.6745 * (rmssd_val - med_rmssd) / mad_rmssd) if not np.isnan(rmssd_val) else np.nan
        
        dev_eda_ratio = (eda_val / max(0.05, med_eda)) if not np.isnan(eda_val) else np.nan
        dev_eda_diff = (eda_val - med_eda) if not np.isnan(eda_val) else np.nan
        
        dev_temp_diff = (temp_val - med_temp) if not np.isnan(temp_val) else np.nan
        
        row_dict["dev_hr_abs"] = dev_hr_abs
        row_dict["dev_hr_robust_z"] = dev_hr_z
        row_dict["dev_hrv_rmssd_abs"] = dev_rmssd_abs
        row_dict["dev_hrv_rmssd_robust_z"] = dev_rmssd_z
        row_dict["dev_eda_tonic_ratio"] = dev_eda_ratio
        row_dict["dev_eda_tonic_diff"] = dev_eda_diff
        row_dict["dev_temp_diff"] = dev_temp_diff
        
        # 3. SEPTERIA Contextual Features (Model C)
        # In laboratory datasets, protocol context is controlled:
        # Zone = 0 (Base / Testing Room), Night Shift = 0, Post-Leave Day = 0, Sleep Deficit = 0.0
        # Cumulative Recovery Burden = weighted cumulative deviation of recent windows
        prev_rmssds = subject_history[s]
        if len(prev_rmssds) >= 3:
            slope = float(np.polyfit(range(len(prev_rmssds[-5:])), prev_rmssds[-5:], 1)[0])
            traj_dir = 1.0 if slope > 0.5 else (-1.0 if slope < -0.5 else 0.0)
        else:
            traj_dir = 0.0
            
        if not np.isnan(rmssd_val):
            subject_history[s].append(rmssd_val)
            
        # Recovery burden proxy: cumulative sympathetic elevation above personal baseline
        rec_burden = float(np.clip((dev_hr_z if not np.isnan(dev_hr_z) else 0.0) * 10.0 + 
                                  (dev_eda_ratio if not np.isnan(dev_eda_ratio) else 1.0) * 15.0, 0.0, 100.0))
                                  
        row_dict["context_zone_active_ops"] = 0.0
        row_dict["context_is_night_shift"] = 0.0
        row_dict["context_post_leave_day"] = 0.0
        row_dict["recovery_burden_score"] = rec_burden
        row_dict["sleep_deficit_hours"] = 0.0
        row_dict["trajectory_direction_hrv"] = traj_dir
        
        enriched.append(row_dict)
    return enriched

def extract_feature_matrix(enriched_rows, feature_list, has_target=True):
    X = []
    y = []
    for r in enriched_rows:
        vec = []
        for f in feature_list:
            v = r.get(f, "")
            if v == "" or v is None or str(v).lower() == "nan":
                vec.append(np.nan)
            else:
                try:
                    vec.append(float(v))
                except ValueError:
                    vec.append(np.nan)
        X.append(vec)
        if has_target and "target_binary" in r:
            y.append(int(r["target_binary"]))
    return np.array(X, dtype=np.float64), (np.array(y, dtype=np.int64) if has_target else None)

def evaluate_model_on_partition(model, X, y, threshold=0.5):
    y_prob = model.predict_proba(X)[:, 1]
    y_pred = (y_prob >= threshold).astype(int)
    
    acc = accuracy_score(y, y_pred)
    bal_acc = balanced_accuracy_score(y, y_pred)
    prec = precision_score(y, y_pred, zero_division=0)
    rec = recall_score(y, y_pred, zero_division=0)
    f1 = f1_score(y, y_pred, zero_division=0)
    
    cm = confusion_matrix(y, y_pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()
    spec = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0
    
    try:
        roc_auc = roc_auc_score(y, y_prob)
    except Exception:
        roc_auc = 0.5
        
    try:
        pr_auc = average_precision_score(y, y_prob)
    except Exception:
        pr_auc = 0.0
        
    brier = brier_score_loss(y, y_prob)
    
    # ECE
    bin_edges = np.linspace(0, 1, 11)
    bin_assignments = np.digitize(y_prob, bin_edges) - 1
    bin_assignments = np.clip(bin_assignments, 0, 9)
    ece = 0.0
    for b in range(10):
        mask = (bin_assignments == b)
        if np.sum(mask) > 0:
            acc_b = float(np.mean(y[mask]))
            conf_b = float(np.mean(y_prob[mask]))
            ece += (np.sum(mask) / len(y)) * abs(acc_b - conf_b)
            
    return {
        "accuracy": round(float(acc), 4),
        "balanced_accuracy": round(float(bal_acc), 4),
        "precision": round(float(prec), 4),
        "recall_sensitivity": round(float(rec), 4),
        "specificity": round(float(spec), 4),
        "f1_score": round(float(f1), 4),
        "roc_auc": round(float(roc_auc), 4),
        "pr_auc": round(float(pr_auc), 4),
        "brier_score": round(float(brier), 4),
        "ece": round(float(ece), 4),
        "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)}
    }

def run_experiments():
    print("=" * 110)
    print("SEPTERIA CONTROLLED ROBUSTNESS EXPERIMENTS (MODELS A, B, C)")
    print("=" * 110)
    
    # 1. Load Raw Partitions
    raw_train = load_csv("train_features.csv")
    raw_val = load_csv("val_features.csv")
    raw_test = load_csv("test_internal_features.csv")
    raw_catsa = load_csv("test_external_catsa_features.csv")
    
    # 2. Compute Subject Baselines strictly within each subject's partition
    train_baselines = compute_subject_baselines(raw_train)
    val_baselines = compute_subject_baselines(raw_val)
    test_baselines = compute_subject_baselines(raw_test)
    catsa_baselines = compute_subject_baselines(raw_catsa)
    
    # 3. Enrich Rows
    train_enriched = enrich_rows_with_features(raw_train, train_baselines)
    val_enriched = enrich_rows_with_features(raw_val, val_baselines)
    test_enriched = enrich_rows_with_features(raw_test, test_baselines)
    catsa_enriched = enrich_rows_with_features(raw_catsa, catsa_baselines)
    
    # 4. Define Feature Sets
    features_A = WRIST_CORE_FEATURES # 25 features
    features_B = WRIST_CORE_FEATURES + PERSONAL_BASELINE_FEATURES # 32 features
    features_C = WRIST_CORE_FEATURES + PERSONAL_BASELINE_FEATURES + SEPTERIA_CONTEXT_FEATURES # 38 features
    
    models_config = [
        ("Model A: Physiological-Only", features_A),
        ("Model B: Physiological + Personal Baseline", features_B),
        ("Model C: Full SEPTERIA Fusion (Physio + Baseline + Context)", features_C)
    ]
    
    experiment_results = {}
    
    for model_name, feat_set in models_config:
        print(f"\n---> Training & Evaluating [{model_name}] ({len(feat_set)} features)...")
        
        X_tr, y_tr = extract_feature_matrix(train_enriched, feat_set, has_target=True)
        X_va, y_va = extract_feature_matrix(val_enriched, feat_set, has_target=True)
        X_te, y_te = extract_feature_matrix(test_enriched, feat_set, has_target=True)
        X_cat, _ = extract_feature_matrix(catsa_enriched, feat_set, has_target=False)
        
        spw = float(np.sum(y_tr == 0) / np.sum(y_tr == 1))
        
        # Fit XGBoost strictly with early stopping on validation partition
        clf = xgb.XGBClassifier(
            n_estimators=300,
            max_depth=6,
            learning_rate=0.03,
            scale_pos_weight=spw,
            subsample=0.85,
            colsample_bytree=0.85,
            reg_alpha=0.1,
            reg_lambda=1.0,
            random_state=42,
            eval_metric="logloss",
            early_stopping_rounds=30,
            n_jobs=-1
        )
        clf.fit(X_tr, y_tr, eval_set=[(X_va, y_va)], verbose=False)
        
        # Evaluate on Validation & Internal Test Partitions
        metrics_val = evaluate_model_on_partition(clf, X_va, y_va, threshold=0.5)
        metrics_test = evaluate_model_on_partition(clf, X_te, y_te, threshold=0.5)
        
        # Evaluate on External CATSA Benchmark
        y_prob_catsa = clf.predict_proba(X_cat)[:, 1]
        catsa_by_task = defaultdict(list)
        for i, r in enumerate(raw_catsa):
            cond = r.get("condition", "")
            catsa_by_task[cond].append(y_prob_catsa[i])
            
        catsa_task_metrics = {}
        for cond, probs in sorted(catsa_by_task.items()):
            probs_arr = np.array(probs)
            catsa_task_metrics[cond] = {
                "windows_count": len(probs_arr),
                "mean_p_stress": round(float(np.mean(probs_arr)), 4),
                "median_p_stress": round(float(np.median(probs_arr)), 4),
                "high_stress_pct": round(float(np.mean(probs_arr >= 0.5) * 100), 2)
            }
            
        # Top 5 Features by Gain
        booster = clf.get_booster()
        score_gain = booster.get_score(importance_type="gain")
        top_gains = []
        for idx, f_name in enumerate(feat_set):
            g = score_gain.get(f"f{idx}", 0.0)
            top_gains.append((f_name, g))
        top_gains.sort(key=lambda x: x[1], reverse=True)
        
        experiment_results[model_name] = {
            "features_count": len(feat_set),
            "validation_metrics": metrics_val,
            "internal_test_metrics": metrics_test,
            "catsa_benchmark": catsa_task_metrics,
            "top_features_by_gain": [{"feature": f, "gain": round(float(g), 2)} for f, g in top_gains[:7]]
        }
        
        print(f"  [Validation]    Acc: {metrics_val['accuracy']:.4f} | BalAcc: {metrics_val['balanced_accuracy']:.4f} | F1: {metrics_val['f1_score']:.4f} | ROC-AUC: {metrics_val['roc_auc']:.4f} | ECE: {metrics_val['ece']:.4f}")
        print(f"  [Internal Test] Acc: {metrics_test['accuracy']:.4f} | BalAcc: {metrics_test['balanced_accuracy']:.4f} | F1: {metrics_test['f1_score']:.4f} | ROC-AUC: {metrics_test['roc_auc']:.4f} | Spec: {metrics_test['specificity']:.4f} | Sens: {metrics_test['recall_sensitivity']:.4f}")
        print(f"  [CATSA Baseline] Mean P(Stress): {catsa_task_metrics['Baseline']['mean_p_stress']:.4f} | High P(>=0.5): {catsa_task_metrics['Baseline']['high_stress_pct']:.1f}%")
        print(f"  [CATSA Tasks]    Logic: {catsa_task_metrics['Logic']['mean_p_stress']:.4f} | Stroop: {catsa_task_metrics['Stroop']['mean_p_stress']:.4f} | Sudoku: {catsa_task_metrics['Sudoku']['mean_p_stress']:.4f}")
        print(f"  [Top 3 Gain Feats] {top_gains[0][0]} ({top_gains[0][1]:.1f}), {top_gains[1][0]} ({top_gains[1][1]:.1f}), {top_gains[2][0]} ({top_gains[2][1]:.1f})")

    # Save summary manifest
    manifest_path = os.path.join(RESULTS_DIR, "robustness_experiments_summary.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(experiment_results, f, indent=2)
        
    print(f"\n[OK] Robustness Experiments Summary saved to: {manifest_path}")
    return experiment_results

if __name__ == "__main__":
    run_experiments()
