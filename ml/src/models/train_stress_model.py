"""
SEPTERIA Machine Learning Training & Evaluation Pipeline (Phase 6 / Step 4)
Model: Multi-Model Physiological Stress Prediction (XGBoost, LightGBM, Random Forest, Logistic Regression)
Target: Binary Acute Stress Classification (0 = Non-Stress/Exertion, 1 = Acute Stress)
Partitioning: Strict Subject-Wise Group Partitioning (35 Train, 8 Val, 8 Test, 50 CATSA = 101 Subjects)
Zero-Leakage Policy: Preprocessors & Scalers fit exclusively on the Training Partition.
"""

import os
import sys
import json
import csv
from collections import defaultdict
import numpy as np
import joblib

# ML Libraries
from sklearn.preprocessing import RobustScaler
from sklearn.impute import SimpleImputer
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GroupKFold
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
    classification_report
)

import xgboost as xgb
import lightgbm as lgb

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

PROCESSED_DIR = r"d:\IITM\SIH\PROTOTYPE\ANTIGRAVITY\ANTI-INFO\ml\data\processed"
MODELS_DIR = r"d:\IITM\SIH\PROTOTYPE\ANTIGRAVITY\ANTI-INFO\ml\models"
RESULTS_DIR = r"d:\IITM\SIH\PROTOTYPE\ANTIGRAVITY\ANTI-INFO\ml\results"

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

WRIST_CORE_FEATURES = [
    "hr_mean", "hr_std", "hr_min", "hr_max", "hr_slope",
    "hrv_rmssd", "hrv_sdnn", "hrv_pnn50", "hrv_cv",
    "eda_mean", "eda_std", "eda_min", "eda_max", "eda_slope",
    "eda_tonic_mean", "eda_phasic_peaks", "eda_phasic_max_amplitude", "eda_phasic_auc",
    "temp_mean", "temp_std", "temp_slope",
    "acc_magnitude_mean", "acc_magnitude_std", "acc_motion_energy", "acc_peak_acceleration"
]

def load_partition_csv(filepath, has_target=True):
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    X_list = []
    y_list = []
    meta_list = []
    
    for r in rows:
        feat_vals = []
        for feat in WRIST_CORE_FEATURES:
            val_str = r.get(feat, "")
            if val_str == "" or val_str is None or val_str.lower() == "nan":
                feat_vals.append(np.nan)
            else:
                try:
                    feat_vals.append(float(val_str))
                except ValueError:
                    feat_vals.append(np.nan)
        X_list.append(feat_vals)
        
        meta = {
            "dataset": r.get("dataset", ""),
            "subject_id": r.get("subject_id", ""),
            "base_subject_id": f"{r.get('dataset', '')}_{r.get('subject_id', '').split('_')[0]}",
            "source_label": r.get("source_label", r.get("condition", "")),
            "window_idx": int(r.get("window_idx", 0))
        }
        meta_list.append(meta)
        
        if has_target and "target_binary" in r:
            y_list.append(int(r["target_binary"]))
            
    X = np.array(X_list, dtype=np.float64)
    y = np.array(y_list, dtype=np.int64) if has_target else None
    return X, y, meta_list, rows

def compute_metrics(y_true, y_pred, y_prob):
    acc = accuracy_score(y_true, y_pred)
    bal_acc = balanced_accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    f1_macro = f1_score(y_true, y_pred, average="macro", zero_division=0)
    
    # Specificity = TN / (TN + FP)
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()
    spec = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0
    
    try:
        roc_auc = roc_auc_score(y_true, y_prob)
    except Exception:
        roc_auc = 0.5
        
    try:
        pr_auc = average_precision_score(y_true, y_prob)
    except Exception:
        pr_auc = 0.0
        
    return {
        "accuracy": round(float(acc), 4),
        "balanced_accuracy": round(float(bal_acc), 4),
        "precision": round(float(prec), 4),
        "recall_sensitivity": round(float(rec), 4),
        "specificity": round(float(spec), 4),
        "f1_score_binary": round(float(f1), 4),
        "f1_score_macro": round(float(f1_macro), 4),
        "roc_auc": round(float(roc_auc), 4),
        "pr_auc": round(float(pr_auc), 4),
        "confusion_matrix": {
            "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)
        }
    }

def run_training_pipeline():
    print("=" * 80)
    print("SEPTERIA PHASE 6: AI MODEL TRAINING & EVALUATION PIPELINE")
    print("=" * 80)
    
    # 1. Load Data Partitions
    train_csv = os.path.join(PROCESSED_DIR, "train_features.csv")
    val_csv = os.path.join(PROCESSED_DIR, "val_features.csv")
    test_csv = os.path.join(PROCESSED_DIR, "test_internal_features.csv")
    catsa_csv = os.path.join(PROCESSED_DIR, "test_external_catsa_features.csv")
    
    X_train_raw, y_train, meta_train, _ = load_partition_csv(train_csv, has_target=True)
    X_val_raw, y_val, meta_val, _ = load_partition_csv(val_csv, has_target=True)
    X_test_raw, y_test, meta_test, _ = load_partition_csv(test_csv, has_target=True)
    X_catsa_raw, _, meta_catsa, _ = load_partition_csv(catsa_csv, has_target=False)
    
    # Group Subject IDs for GroupKFold
    train_groups = np.array([m["base_subject_id"] for m in meta_train])
    unique_train_subs = np.unique(train_groups)
    val_subs = np.unique([m["base_subject_id"] for m in meta_val])
    test_subs = np.unique([m["base_subject_id"] for m in meta_test])
    catsa_subs = np.unique([m["base_subject_id"] for m in meta_catsa])
    
    print("\n[PARTITION VERIFICATION]")
    print(f"  * Train Set:     {len(X_train_raw):,} windows across {len(unique_train_subs)} subjects ({np.sum(y_train==0)} non-stress, {np.sum(y_train==1)} stress, ratio: {np.sum(y_train==0)/np.sum(y_train==1):.2f})")
    print(f"  * Val Set:       {len(X_val_raw):,} windows across {len(val_subs)} subjects ({np.sum(y_val==0)} non-stress, {np.sum(y_val==1)} stress)")
    print(f"  * Test Set:      {len(X_test_raw):,} windows across {len(test_subs)} subjects ({np.sum(y_test==0)} non-stress, {np.sum(y_test==1)} stress)")
    print(f"  * External CATSA: {len(X_catsa_raw):,} windows across {len(catsa_subs)} subjects (5 tasks)")
    print(f"  * Total Unique Human Participants: {len(unique_train_subs) + len(val_subs) + len(test_subs) + len(catsa_subs)} (101 Subjects)")
    print(f"  * Features per Window: {len(WRIST_CORE_FEATURES)} common wearable features")
    
    # 2. Strict Preprocessing (Fitted on Training Fold ONLY)
    imputer = SimpleImputer(strategy="median")
    imputer.fit(X_train_raw)
    
    scaler = RobustScaler()
    X_train_imp = imputer.transform(X_train_raw)
    scaler.fit(X_train_imp)
    
    X_train_scaled = scaler.transform(X_train_imp)
    X_val_scaled = scaler.transform(imputer.transform(X_val_raw))
    X_test_scaled = scaler.transform(imputer.transform(X_test_raw))
    X_catsa_scaled = scaler.transform(imputer.transform(X_catsa_raw))
    
    joblib.dump({"imputer": imputer, "scaler": scaler, "features": WRIST_CORE_FEATURES}, os.path.join(MODELS_DIR, "feature_preprocessor.joblib"))
    print("\n[PREPROCESSOR] Fitted SimpleImputer & RobustScaler strictly on Training Partition.")
    
    # 3. Model Training & Comparison Suite
    results = {}
    models = {}
    
    # Model A: Dummy Classifier
    print("\n--> [1/5] Training Dummy Baseline Classifier (Majority Class)...")
    dummy = DummyClassifier(strategy="most_frequent")
    dummy.fit(X_train_scaled, y_train)
    models["dummy"] = dummy
    
    # Model B: Logistic Regression (L2 Regularized)
    print("--> [2/5] Training Logistic Regression (L2 Regularized with Class Weights)...")
    lr = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42, C=1.0)
    lr.fit(X_train_scaled, y_train)
    models["logistic_regression"] = lr
    
    # Model C: Random Forest Classifier
    print("--> [3/5] Training Random Forest Classifier (200 Trees, Balanced Subsample)...")
    rf = RandomForestClassifier(n_estimators=200, max_depth=12, min_samples_split=5, class_weight="balanced_subsample", random_state=42, n_jobs=-1)
    rf.fit(X_train_scaled, y_train)
    models["random_forest"] = rf
    
    # Model D: LightGBM Classifier
    print("--> [4/5] Training LightGBM Classifier (Gradient Boosted Decision Trees)...")
    scale_pos_weight = float(np.sum(y_train == 0) / np.sum(y_train == 1))
    lgbm = lgb.LGBMClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.05,
        scale_pos_weight=scale_pos_weight,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        verbosity=-1
    )
    lgbm.fit(
        X_train_raw, y_train,
        eval_set=[(X_val_raw, y_val)],
        callbacks=[lgb.early_stopping(stopping_rounds=25, verbose=False)]
    )
    models["lightgbm"] = lgbm
    
    # Model E: XGBoost Classifier (Primary Production Model)
    print("--> [5/5] Training Primary XGBoost Classifier (Native NaN Handling & Cost-Sensitive Loss)...")
    xgb_clf = xgb.XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.03,
        scale_pos_weight=scale_pos_weight,
        subsample=0.85,
        colsample_bytree=0.85,
        reg_alpha=0.1,
        reg_lambda=1.0,
        random_state=42,
        eval_metric="logloss",
        early_stopping_rounds=30,
        n_jobs=-1
    )
    xgb_clf.fit(
        X_train_raw, y_train,
        eval_set=[(X_train_raw, y_train), (X_val_raw, y_val)],
        verbose=False
    )
    models["xgboost"] = xgb_clf
    
    # Save Primary Model
    xgb_clf.save_model(os.path.join(MODELS_DIR, "xgboost_stress_model.json"))
    joblib.dump(xgb_clf, os.path.join(MODELS_DIR, "xgboost_stress_model.joblib"))
    print("  -> Saved XGBoost Model Artifacts: xgboost_stress_model.json & .joblib")
    
    # 4. Subject-Wise 5-Fold Group Cross-Validation on Training Partition
    print("\n" + "=" * 80)
    print("5-FOLD SUBJECT-WISE GROUP CROSS-VALIDATION (35 Training Subjects)")
    print("=" * 80)
    
    gkf = GroupKFold(n_splits=5)
    cv_scores = {"acc": [], "bal_acc": [], "f1": [], "roc_auc": [], "pr_auc": []}
    
    fold = 1
    for tr_idx, te_idx in gkf.split(X_train_raw, y_train, groups=train_groups):
        X_tr_f, y_tr_f = X_train_raw[tr_idx], y_train[tr_idx]
        X_te_f, y_te_f = X_train_raw[te_idx], y_train[te_idx]
        
        spw_f = float(np.sum(y_tr_f == 0) / np.sum(y_tr_f == 1))
        fold_model = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.03,
            scale_pos_weight=spw_f,
            subsample=0.85,
            colsample_bytree=0.85,
            reg_alpha=0.1,
            reg_lambda=1.0,
            random_state=42,
            eval_metric="logloss",
            n_jobs=-1
        )
        fold_model.fit(X_tr_f, y_tr_f, verbose=False)
        y_prob_f = fold_model.predict_proba(X_te_f)[:, 1]
        y_pred_f = (y_prob_f >= 0.5).astype(int)
        
        m_f = compute_metrics(y_te_f, y_pred_f, y_prob_f)
        cv_scores["acc"].append(m_f["accuracy"])
        cv_scores["bal_acc"].append(m_f["balanced_accuracy"])
        cv_scores["f1"].append(m_f["f1_score_binary"])
        cv_scores["roc_auc"].append(m_f["roc_auc"])
        cv_scores["pr_auc"].append(m_f["pr_auc"])
        
        held_out_subs = len(np.unique(train_groups[te_idx]))
        print(f"  Fold {fold}: {held_out_subs} Subjects ({len(te_idx):,} win) -> BalAcc: {m_f['balanced_accuracy']:.4f} | F1: {m_f['f1_score_binary']:.4f} | ROC-AUC: {m_f['roc_auc']:.4f}")
        fold += 1
        
    cv_summary = {
        "mean_accuracy": round(float(np.mean(cv_scores["acc"])), 4),
        "std_accuracy": round(float(np.std(cv_scores["acc"])), 4),
        "mean_balanced_accuracy": round(float(np.mean(cv_scores["bal_acc"])), 4),
        "std_balanced_accuracy": round(float(np.std(cv_scores["bal_acc"])), 4),
        "mean_f1_score": round(float(np.mean(cv_scores["f1"])), 4),
        "std_f1_score": round(float(np.std(cv_scores["f1"])), 4),
        "mean_roc_auc": round(float(np.mean(cv_scores["roc_auc"])), 4),
        "std_roc_auc": round(float(np.std(cv_scores["roc_auc"])), 4),
        "mean_pr_auc": round(float(np.mean(cv_scores["pr_auc"])), 4),
        "std_pr_auc": round(float(np.std(cv_scores["pr_auc"])), 4)
    }
    print(f"\n[5-Fold CV Aggregate] BalAcc: {cv_summary['mean_balanced_accuracy']:.4f} ± {cv_summary['std_balanced_accuracy']:.4f} | ROC-AUC: {cv_summary['mean_roc_auc']:.4f} ± {cv_summary['std_roc_auc']:.4f}")
    
    # 5. Benchmark Model Evaluation on Validation and Internal Test Sets
    print("\n" + "=" * 80)
    print("MODEL COMPARISON ON HELD-OUT VALIDATION SET (8 Subjects, 1,214 Windows)")
    print("=" * 80)
    
    val_comparison = {}
    for m_name, model in models.items():
        if m_name in ["dummy", "logistic_regression", "random_forest"]:
            y_prob_val = model.predict_proba(X_val_scaled)[:, 1]
        else:
            y_prob_val = model.predict_proba(X_val_raw)[:, 1]
        y_pred_val = (y_prob_val >= 0.5).astype(int)
        metrics = compute_metrics(y_val, y_pred_val, y_prob_val)
        val_comparison[m_name] = metrics
        print(f"  {m_name.upper():<22} -> Acc: {metrics['accuracy']:.4f} | BalAcc: {metrics['balanced_accuracy']:.4f} | F1: {metrics['f1_score_binary']:.4f} | ROC-AUC: {metrics['roc_auc']:.4f} | PR-AUC: {metrics['pr_auc']:.4f}")
        
    print("\n" + "=" * 80)
    print("MODEL COMPARISON ON HELD-OUT INTERNAL TEST SET (8 Subjects, 971 Windows)")
    print("=" * 80)
    
    test_comparison = {}
    for m_name, model in models.items():
        if m_name in ["dummy", "logistic_regression", "random_forest"]:
            y_prob_test = model.predict_proba(X_test_scaled)[:, 1]
        else:
            y_prob_test = model.predict_proba(X_test_raw)[:, 1]
        y_pred_test = (y_prob_test >= 0.5).astype(int)
        metrics = compute_metrics(y_test, y_pred_test, y_prob_test)
        test_comparison[m_name] = metrics
        print(f"  {m_name.upper():<22} -> Acc: {metrics['accuracy']:.4f} | BalAcc: {metrics['balanced_accuracy']:.4f} | F1: {metrics['f1_score_binary']:.4f} | ROC-AUC: {metrics['roc_auc']:.4f} | PR-AUC: {metrics['pr_auc']:.4f}")
        
    # 6. Detailed Protocol & Subgroup Breakdown on Internal Test Set (XGBoost)
    print("\n" + "=" * 80)
    print("XGBOOST SUBGROUP & PROTOCOL ANALYSIS (INTERNAL TEST SET)")
    print("=" * 80)
    
    y_prob_xgb_test = xgb_clf.predict_proba(X_test_raw)[:, 1]
    y_pred_xgb_test = (y_prob_xgb_test >= 0.5).astype(int)
    
    protocol_groups = defaultdict(lambda: {"y_true": [], "y_pred": [], "y_prob": []})
    for i, meta in enumerate(meta_test):
        p_name = meta["source_label"]
        protocol_groups[p_name]["y_true"].append(y_test[i])
        protocol_groups[p_name]["y_pred"].append(y_pred_xgb_test[i])
        protocol_groups[p_name]["y_prob"].append(y_prob_xgb_test[i])
        
    subgroup_metrics = {}
    for p_name, data in sorted(protocol_groups.items()):
        p_true = np.array(data["y_true"])
        p_pred = np.array(data["y_pred"])
        p_prob = np.array(data["y_prob"])
        
        acc_p = accuracy_score(p_true, p_pred)
        mean_p_prob = float(np.mean(p_prob))
        subgroup_metrics[p_name] = {
            "total_windows": len(p_true),
            "ground_truth_label": int(p_true[0]),
            "accuracy": round(float(acc_p), 4),
            "mean_predicted_stress_prob": round(mean_p_prob, 4)
        }
        print(f"  * Protocol [{p_name:<18}] (N={len(p_true):>3}, TrueClass={p_true[0]}): Acc = {acc_p*100:>5.1f}% | Mean P(Stress) = {mean_p_prob:.3f}")
        
    # 7. External Benchmark Evaluation on CATSA (50 Subjects, 1,244 Windows)
    print("\n" + "=" * 80)
    print("EXTERNAL BENCHMARK EVALUATION ON CATSA (50 Unseen Subjects, 5 Cognitive Tasks)")
    print("=" * 80)
    
    y_prob_catsa = xgb_clf.predict_proba(X_catsa_raw)[:, 1]
    catsa_task_groups = defaultdict(list)
    for i, meta in enumerate(meta_catsa):
        task = meta["source_label"]
        catsa_task_groups[task].append(y_prob_catsa[i])
        
    catsa_task_summary = {}
    for task, probs in sorted(catsa_task_groups.items()):
        probs_arr = np.array(probs)
        catsa_task_summary[task] = {
            "total_windows": len(probs_arr),
            "mean_stress_probability": round(float(np.mean(probs_arr)), 4),
            "median_stress_probability": round(float(np.median(probs_arr)), 4),
            "std_stress_probability": round(float(np.std(probs_arr)), 4),
            "high_stress_pct": round(float(np.mean(probs_arr >= 0.5) * 100), 2)
        }
        print(f"  * Task [{task:<10}] (N={len(probs_arr):>3} windows): Mean P(Stress) = {np.mean(probs_arr):.4f} | Median = {np.median(probs_arr):.4f} | P(Stress>=0.5) = {np.mean(probs_arr >= 0.5)*100:.1f}%")
        
    # 8. Feature Importance & Physiological Interpretability
    print("\n" + "=" * 80)
    print("FEATURE IMPORTANCE & PHYSIOLOGICAL INTERPRETABILITY (XGBoost)")
    print("=" * 80)
    
    booster = xgb_clf.get_booster()
    score_gain = booster.get_score(importance_type="gain")
    score_weight = booster.get_score(importance_type="weight")
    score_cover = booster.get_score(importance_type="cover")
    
    # Map feature names
    feature_importances = []
    for idx, f_name in enumerate(WRIST_CORE_FEATURES):
        f_key = f"f{idx}"
        gain = score_gain.get(f_key, 0.0)
        weight = score_weight.get(f_key, 0.0)
        cover = score_cover.get(f_key, 0.0)
        
        # Category
        if "hrv" in f_name:
            cat = "Parasympathetic / PRV"
        elif "hr_" in f_name:
            cat = "Cardiovascular"
        elif "eda" in f_name:
            cat = "Sympathetic / EDA"
        elif "temp" in f_name:
            cat = "Thermal / Vasoconstriction"
        else:
            cat = "Kinetic / ACC"
            
        feature_importances.append({
            "feature_index": idx,
            "feature_name": f_name,
            "category": cat,
            "gain": round(float(gain), 4),
            "weight": round(float(weight), 4),
            "cover": round(float(cover), 4)
        })
        
    feature_importances.sort(key=lambda x: x["gain"], reverse=True)
    
    # Category Gain Aggregate
    category_gain = defaultdict(float)
    total_gain = sum(f["gain"] for f in feature_importances)
    for f in feature_importances:
        category_gain[f["category"]] += f["gain"]
        
    print("Top 10 Most Predictive Physiological Features by XGBoost Gain:")
    for rank, f in enumerate(feature_importances[:10], 1):
        pct = (f["gain"] / max(1e-6, total_gain)) * 100
        print(f"  {rank:>2}. {f['feature_name']:<25} ({f['category']:<26}) -> Gain: {f['gain']:>7.2f} ({pct:>5.1f}%)")
        
    print("\nPhysiological Modality Contribution by Relative Information Gain:")
    for cat, c_gain in sorted(category_gain.items(), key=lambda x: x[1], reverse=True):
        print(f"  * {cat:<28} -> {c_gain:>8.2f} ({c_gain/max(1e-6, total_gain)*100:>5.1f}%)")
        
    # 9. Save Complete Evaluation Results
    eval_manifest = {
        "manifest_version": "1.0.0",
        "model_architecture": "XGBoost Classifier (Track 1 Wearable Core)",
        "features_count": len(WRIST_CORE_FEATURES),
        "cross_validation_5fold": cv_summary,
        "validation_set_evaluation": val_comparison,
        "internal_test_set_evaluation": test_comparison,
        "subgroup_protocol_analysis": subgroup_metrics,
        "external_catsa_generalization": catsa_task_summary,
        "feature_importances": feature_importances,
        "modality_contributions": {k: round(v/max(1e-6, total_gain)*100, 2) for k, v in category_gain.items()}
    }
    
    results_path = os.path.join(RESULTS_DIR, "evaluation_metrics.json")
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(eval_manifest, f, indent=2)
        
    print(f"\n[OK] Complete Evaluation Metrics saved to: {results_path}")
    print("=" * 80)
    return eval_manifest

if __name__ == "__main__":
    run_training_pipeline()
