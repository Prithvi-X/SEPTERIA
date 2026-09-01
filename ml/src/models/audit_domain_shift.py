"""
SEPTERIA Feature Distribution & Domain Shift Audit (Train vs CATSA)
Analyzes:
1. Feature statistics (mean, std, median, 10th, 25th, 75th, 90th percentiles, missingness)
2. Distribution divergence metrics (Kolmogorov-Smirnov D_KS, Wasserstein Earth Mover's Distance)
3. Sensor unit / scale disparities between datasets
4. Probability calibration diagnostics on held-out validation data (ECE, MCE, Brier Score, Reliability Curves)
5. Controlled feature ablation sensitivity tests
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
from sklearn.metrics import brier_score_loss, accuracy_score, balanced_accuracy_score, roc_auc_score, f1_score
from sklearn.calibration import calibration_curve

PROCESSED_DIR = r"d:\IITM\SIH\PROTOTYPE\ANTIGRAVITY\ANTI-INFO\ml\data\processed"
MODELS_DIR = r"d:\IITM\SIH\PROTOTYPE\ANTIGRAVITY\ANTI-INFO\ml\models"
RESULTS_DIR = r"d:\IITM\SIH\PROTOTYPE\ANTIGRAVITY\ANTI-INFO\ml\results"

WRIST_CORE_FEATURES = [
    "hr_mean", "hr_std", "hr_min", "hr_max", "hr_slope",
    "hrv_rmssd", "hrv_sdnn", "hrv_pnn50", "hrv_cv",
    "eda_mean", "eda_std", "eda_min", "eda_max", "eda_slope",
    "eda_tonic_mean", "eda_phasic_peaks", "eda_phasic_max_amplitude", "eda_phasic_auc",
    "temp_mean", "temp_std", "temp_slope",
    "acc_magnitude_mean", "acc_magnitude_std", "acc_motion_energy", "acc_peak_acceleration"
]

def load_rows(fname):
    with open(os.path.join(PROCESSED_DIR, fname), "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def get_feature_vector(row):
    vec = []
    for f in WRIST_CORE_FEATURES:
        v = row.get(f, "")
        if v == "" or v is None or v.lower() == "nan":
            vec.append(np.nan)
        else:
            try:
                vec.append(float(v))
            except ValueError:
                vec.append(np.nan)
    return vec

def run_audit():
    train_rows = load_rows("train_features.csv")
    val_rows = load_rows("val_features.csv")
    test_rows = load_rows("test_internal_features.csv")
    catsa_rows = load_rows("test_external_catsa_features.csv")
    
    catsa_base_rows = [r for r in catsa_rows if r.get("condition") == "Baseline"]
    train_nonstress_rows = [r for r in train_rows if r.get("target_binary") == "0"]
    train_stress_rows = [r for r in train_rows if r.get("target_binary") == "1"]
    
    print("=" * 110)
    print("FEATURE DISTRIBUTION & DOMAIN SHIFT AUDIT: TRAINING vs CATSA BASELINE")
    print("=" * 110)
    
    audit_table = []
    
    for f in WRIST_CORE_FEATURES:
        v_tr_all = np.array([float(r[f]) for r in train_rows if r.get(f, "") not in ["", "nan", "NaN", None]])
        v_tr_ns = np.array([float(r[f]) for r in train_nonstress_rows if r.get(f, "") not in ["", "nan", "NaN", None]])
        v_tr_s = np.array([float(r[f]) for r in train_stress_rows if r.get(f, "") not in ["", "nan", "NaN", None]])
        v_cat_base = np.array([float(r[f]) for r in catsa_base_rows if r.get(f, "") not in ["", "nan", "NaN", None]])
        v_cat_all = np.array([float(r[f]) for r in catsa_rows if r.get(f, "") not in ["", "nan", "NaN", None]])
        
        # KS-Test between Train Non-Stress and CATSA Baseline
        if len(v_tr_ns) > 5 and len(v_cat_base) > 5:
            ks_stat, ks_pval = stats.ks_2samp(v_tr_ns, v_cat_base)
            w_dist = stats.wasserstein_distance(v_tr_ns, v_cat_base)
        else:
            ks_stat, ks_pval, w_dist = np.nan, np.nan, np.nan
            
        def get_stats(arr):
            if len(arr) == 0:
                return {"mean": np.nan, "std": np.nan, "median": np.nan, "p10": np.nan, "p25": np.nan, "p75": np.nan, "p90": np.nan, "missing_pct": 100.0}
            return {
                "mean": round(float(np.mean(arr)), 4),
                "std": round(float(np.std(arr, ddof=1)), 4) if len(arr) > 1 else 0.0,
                "median": round(float(np.median(arr)), 4),
                "p10": round(float(np.percentile(arr, 10)), 4),
                "p25": round(float(np.percentile(arr, 25)), 4),
                "p75": round(float(np.percentile(arr, 75)), 4),
                "p90": round(float(np.percentile(arr, 90)), 4),
                "count": len(arr)
            }
            
        f_entry = {
            "feature": f,
            "train_nonstress": get_stats(v_tr_ns),
            "train_stress": get_stats(v_tr_s),
            "catsa_baseline": get_stats(v_cat_base),
            "catsa_all": get_stats(v_cat_all),
            "ks_statistic": round(float(ks_stat), 4),
            "ks_pvalue": float(ks_pval),
            "wasserstein_distance": round(float(w_dist), 4)
        }
        audit_table.append(f_entry)
        
    # Print formatted table
    print(f"{'Feature':<24} | {'Train NonStress Med (Q1-Q3)':<28} | {'CATSA Baseline Med (Q1-Q3)':<28} | {'KS Stat (D)':<11} | {'Wasserstein':<11}")
    print("-" * 110)
    for entry in audit_table:
        f = entry["feature"]
        t_m = entry["train_nonstress"]
        c_m = entry["catsa_baseline"]
        t_str = f"{t_m['median']:.2f} ({t_m['p25']:.2f}-{t_m['p75']:.2f})" if not np.isnan(t_m['median']) else "N/A"
        c_str = f"{c_m['median']:.2f} ({c_m['p25']:.2f}-{c_m['p75']:.2f})" if not np.isnan(c_m['median']) else "N/A"
        print(f"{f:<24} | {t_str:<28} | {c_str:<28} | {entry['ks_statistic']:<11.3f} | {entry['wasserstein_distance']:<11.3f}")
        
    # Calibration Diagnostics on Validation Set (8 Subjects, 1,214 Windows)
    print("\n" + "=" * 110)
    print("PROBABILITY CALIBRATION DIAGNOSTICS (Held-Out Validation Set — 8 Subjects)")
    print("=" * 110)
    
    model = joblib.load(os.path.join(MODELS_DIR, "xgboost_stress_model.joblib"))
    
    X_val = np.array([get_feature_vector(r) for r in val_rows], dtype=np.float64)
    y_val = np.array([int(r["target_binary"]) for r in val_rows], dtype=np.int64)
    
    y_prob_val = model.predict_proba(X_val)[:, 1]
    
    # Brier score
    brier = brier_score_loss(y_val, y_prob_val)
    
    # Reliability curve (10 bins)
    prob_true, prob_pred = calibration_curve(y_val, y_prob_val, n_bins=10, strategy="uniform")
    
    # Expected Calibration Error (ECE) & Maximum Calibration Error (MCE)
    bin_edges = np.linspace(0, 1, 11)
    bin_assignments = np.digitize(y_prob_val, bin_edges) - 1
    bin_assignments = np.clip(bin_assignments, 0, 9)
    
    ece = 0.0
    mce = 0.0
    bin_details = []
    
    for b in range(10):
        mask = (bin_assignments == b)
        n_b = np.sum(mask)
        if n_b > 0:
            acc_b = float(np.mean(y_val[mask]))
            conf_b = float(np.mean(y_prob_val[mask]))
            diff = abs(acc_b - conf_b)
            ece += (n_b / len(y_val)) * diff
            mce = max(mce, diff)
            bin_details.append({
                "bin": b + 1,
                "range": f"[{bin_edges[b]:.1f}, {bin_edges[b+1]:.1f})",
                "count": int(n_b),
                "empirical_stress_fraction": round(acc_b, 4),
                "mean_predicted_confidence": round(conf_b, 4),
                "calibration_gap": round(diff, 4)
            })
            
    print(f"  * Brier Score:                    {brier:.4f} (Optimal: 0.0, Baseline Dummy: 0.2464)")
    print(f"  * Expected Calibration Error (ECE): {ece:.4f} ({ece*100:.2f}%)")
    print(f"  * Maximum Calibration Error (MCE):  {mce:.4f} ({mce*100:.2f}%)")
    print("\nReliability Diagram Bins (10 Bins):")
    for bd in bin_details:
        print(f"    Bin {bd['bin']:>2} {bd['range']:<12}: N = {bd['count']:>4} | Empirical True Rate = {bd['empirical_stress_fraction']:>6.3f} | Predicted Conf = {bd['mean_predicted_confidence']:>6.3f} | Gap = {bd['calibration_gap']:>6.3f}")
        
    # Threshold Tuning Diagnostics (on Validation Set)
    thresholds = np.linspace(0.1, 0.9, 17)
    thresh_table = []
    for t in thresholds:
        y_pred_t = (y_prob_val >= t).astype(int)
        acc_t = accuracy_score(y_val, y_pred_t)
        bal_acc_t = balanced_accuracy_score(y_val, y_pred_t)
        f1_t = f1_score(y_val, y_pred_t, zero_division=0)
        thresh_table.append({
            "threshold": round(float(t), 2),
            "accuracy": round(float(acc_t), 4),
            "balanced_accuracy": round(float(bal_acc_t), 4),
            "f1_score": round(float(f1_t), 4)
        })
        
    best_bal = max(thresh_table, key=lambda x: x["balanced_accuracy"])
    best_f1 = max(thresh_table, key=lambda x: x["f1_score"])
    print(f"\nOptimal Validation Thresholds:")
    print(f"  * Best Balanced Accuracy: Threshold = {best_bal['threshold']} -> BalAcc = {best_bal['balanced_accuracy']:.4f} | F1 = {best_bal['f1_score']:.4f}")
    print(f"  * Best F1-Score:          Threshold = {best_f1['threshold']} -> BalAcc = {best_f1['balanced_accuracy']:.4f} | F1 = {best_f1['f1_score']:.4f}")
    
    # Controlled Feature Ablation / Shift Impact Tests
    print("\n" + "=" * 110)
    print("CONTROLLED FEATURE ABLATION & GENERALIZATION SHIFT EXPERIMENTS")
    print("=" * 110)
    
    X_train = np.array([get_feature_vector(r) for r in train_rows], dtype=np.float64)
    y_train = np.array([int(r["target_binary"]) for r in train_rows], dtype=np.int64)
    X_test = np.array([get_feature_vector(r) for r in test_rows], dtype=np.float64)
    y_test = np.array([int(r["target_binary"]) for r in test_rows], dtype=np.int64)
    X_catsa = np.array([get_feature_vector(r) for r in catsa_rows], dtype=np.float64)
    
    # Track 1: Baseline Full (25 features)
    spw = float(np.sum(y_train == 0) / np.sum(y_train == 1))
    
    # Track 2: Remove Accelerometer Features (Kinetic Shift Check)
    acc_indices = [i for i, f in enumerate(WRIST_CORE_FEATURES) if "acc_" in f]
    non_acc_indices = [i for i, f in enumerate(WRIST_CORE_FEATURES) if "acc_" not in f]
    
    # Track 3: Remove Absolute EDA Levels (Keep only relative/phasic: eda_slope, eda_phasic_peaks, eda_phasic_auc)
    eda_abs_indices = [i for i, f in enumerate(WRIST_CORE_FEATURES) if f in ["eda_mean", "eda_min", "eda_max", "eda_tonic_mean"]]
    non_eda_abs_indices = [i for i, f in enumerate(WRIST_CORE_FEATURES) if f not in ["eda_mean", "eda_min", "eda_max", "eda_tonic_mean"]]
    
    # Track 4: Remove Top Domain Shift Outliers (Features with KS > 0.85 between Train NS and CATSA Base)
    top_shift_features = [e["feature"] for e in audit_table if e["ks_statistic"] > 0.85]
    non_shift_indices = [i for i, f in enumerate(WRIST_CORE_FEATURES) if f not in top_shift_features]
    
    experiments = [
        ("Full Model (25 Features)", list(range(25))),
        ("Without ACC Features (21 Feats)", non_acc_indices),
        ("Without Absolute EDA Baselines (21 Feats)", non_eda_abs_indices),
        (f"Without High-Shift Features ({len(non_shift_indices)} Feats: KS<=0.85)", non_shift_indices)
    ]
    
    ablation_results = []
    for exp_name, feat_idx in experiments:
        X_tr_sub = X_train[:, feat_idx]
        X_val_sub = X_val[:, feat_idx]
        X_te_sub = X_test[:, feat_idx]
        X_cat_sub = X_catsa[:, feat_idx]
        
        m = xgb.XGBClassifier(
            n_estimators=300, max_depth=6, learning_rate=0.03, scale_pos_weight=spw,
            subsample=0.85, colsample_bytree=0.85, reg_alpha=0.1, reg_lambda=1.0,
            random_state=42, eval_metric="logloss", early_stopping_rounds=30, n_jobs=-1
        )
        m.fit(X_tr_sub, y_train, eval_set=[(X_val_sub, y_val)], verbose=False)
        
        y_prob_te = m.predict_proba(X_te_sub)[:, 1]
        y_pred_te = (y_prob_te >= 0.5).astype(int)
        
        acc_te = accuracy_score(y_test, y_pred_te)
        bal_te = balanced_accuracy_score(y_test, y_pred_te)
        f1_te = f1_score(y_test, y_pred_te, zero_division=0)
        roc_te = roc_auc_score(y_test, y_prob_te)
        
        # Test on CATSA Baseline
        catsa_base_indices = [i for i, r in enumerate(catsa_rows) if r.get("condition") == "Baseline"]
        y_prob_cat_base = m.predict_proba(X_cat_sub[catsa_base_indices])[:, 1]
        mean_cat_base_prob = float(np.mean(y_prob_cat_base))
        pct_cat_base_high = float(np.mean(y_prob_cat_base >= 0.5) * 100)
        
        ablation_entry = {
            "experiment": exp_name,
            "features_used": len(feat_idx),
            "internal_test_accuracy": round(float(acc_te), 4),
            "internal_test_bal_acc": round(float(bal_te), 4),
            "internal_test_f1": round(float(f1_te), 4),
            "internal_test_roc_auc": round(float(roc_te), 4),
            "catsa_baseline_mean_prob": round(mean_cat_base_prob, 4),
            "catsa_baseline_high_pct": round(pct_cat_base_high, 2)
        }
        ablation_results.append(ablation_entry)
        
        print(f"  * {exp_name:<42} | Test BalAcc: {bal_te:.4f} | Test ROC-AUC: {roc_te:.4f} | CATSA Base P(Stress): {mean_cat_base_prob:.4f} (High: {pct_cat_base_high:.1f}%)")
        
    audit_manifest = {
        "audit_version": "1.0.0",
        "feature_distribution_shift": audit_table,
        "calibration_diagnostics": {
            "brier_score": round(float(brier), 4),
            "expected_calibration_error": round(float(ece), 4),
            "maximum_calibration_error": round(float(mce), 4),
            "reliability_bins": bin_details,
            "optimal_threshold_bal_acc": best_bal,
            "optimal_threshold_f1": best_f1
        },
        "ablation_experiments": ablation_results
    }
    
    with open(os.path.join(RESULTS_DIR, "domain_shift_audit.json"), "w", encoding="utf-8") as f:
        json.dump(audit_manifest, f, indent=2)
        
    print(f"\n[OK] Domain Shift Audit Manifest saved to: {os.path.join(RESULTS_DIR, 'domain_shift_audit.json')}")
    return audit_manifest

if __name__ == "__main__":
    run_audit()
