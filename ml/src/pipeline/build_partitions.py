import os
import sys
import csv
import json
from collections import defaultdict
import numpy as np

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')

PROCESSED_DIR = r"d:\IITM\SIH\PROTOTYPE\ANTIGRAVITY\ANTI-INFO\ml\data\processed"

WESAD_TRAIN = ["S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9", "S10", "S11", "S13"]
WESAD_VAL = ["S14", "S15"]
WESAD_TEST = ["S16", "S17"]

PHYSIONET_TRAIN = [f"S{i:02d}" for i in range(1, 13)] + [f"f{i:02d}" for i in range(1, 13)]
PHYSIONET_VAL = ["S13", "S14", "S15", "f13", "f15", "f16"]
PHYSIONET_TEST = ["S16", "S17", "S18", "f14", "f17", "f18"]

WRIST_CORE_FEATURES = [
    "hr_mean", "hr_std", "hr_min", "hr_max", "hr_slope",
    "hrv_rmssd", "hrv_sdnn", "hrv_pnn50", "hrv_cv",
    "eda_mean", "eda_std", "eda_min", "eda_max", "eda_slope",
    "eda_tonic_mean", "eda_phasic_peaks", "eda_phasic_max_amplitude", "eda_phasic_auc",
    "temp_mean", "temp_std", "temp_slope",
    "acc_magnitude_mean", "acc_magnitude_std", "acc_motion_energy", "acc_peak_acceleration"
]

CHEST_ADDITIONAL_FEATURES = [
    "chest_ecg_hr_mean", "chest_ecg_hrv_rmssd", "chest_ecg_hrv_sdnn",
    "chest_resp_rate", "chest_resp_std", "chest_emg_mean"
]

def build_partitions():
    wesad_f = os.path.join(PROCESSED_DIR, "wesad_features.csv")
    physionet_f = os.path.join(PROCESSED_DIR, "physionet_features.csv")
    catsa_f = os.path.join(PROCESSED_DIR, "catsa_features.csv")
    
    wesad_rows = []
    if os.path.exists(wesad_f):
        with open(wesad_f, "r", encoding="utf-8") as f:
            wesad_rows = list(csv.DictReader(f))
            
    physionet_rows = []
    if os.path.exists(physionet_f):
        with open(physionet_f, "r", encoding="utf-8") as f:
            physionet_rows = list(csv.DictReader(f))
            
    catsa_rows = []
    if os.path.exists(catsa_f):
        with open(catsa_f, "r", encoding="utf-8") as f:
            catsa_rows = list(csv.DictReader(f))
            
    print(f"Loaded {len(wesad_rows):,} WESAD rows, {len(physionet_rows):,} PhysioNet rows, {len(catsa_rows):,} CATSA rows.", flush=True)
    
    train_rows = []
    val_rows = []
    test_rows = []
    
    for r in wesad_rows:
        s = r["subject_id"].split("_")[0]
        if s in WESAD_TRAIN:
            train_rows.append(r)
        elif s in WESAD_VAL:
            val_rows.append(r)
        elif s in WESAD_TEST:
            test_rows.append(r)
            
    for r in physionet_rows:
        s = r["subject_id"].split("_")[0]
        if s in PHYSIONET_TRAIN:
            train_rows.append(r)
        elif s in PHYSIONET_VAL:
            val_rows.append(r)
        elif s in PHYSIONET_TEST:
            test_rows.append(r)
            
    # Leakage Audit across Biological Subject Identifiers
    train_subs = set([f"{r['dataset']}_{r['subject_id'].split('_')[0]}" for r in train_rows])
    val_subs = set([f"{r['dataset']}_{r['subject_id'].split('_')[0]}" for r in val_rows])
    test_subs = set([f"{r['dataset']}_{r['subject_id'].split('_')[0]}" for r in test_rows])
    catsa_subs = set([f"CATSA_{r['subject_id'].split('_')[0]}" for r in catsa_rows])
    
    overlap_train_val = list(train_subs.intersection(val_subs))
    overlap_train_test = list(train_subs.intersection(test_subs))
    overlap_val_test = list(val_subs.intersection(test_subs))
    overlap_train_catsa = list(train_subs.intersection(catsa_subs))
    
    zero_leakage = (
        len(overlap_train_val) == 0 and
        len(overlap_train_test) == 0 and
        len(overlap_val_test) == 0 and
        len(overlap_train_catsa) == 0
    )
    
    # Write Partition Files
    common_fieldnames = [
        "dataset", "subject_id", "window_idx", "target_binary", "source_label",
        "has_wrist_modality", "has_chest_modality"
    ] + WRIST_CORE_FEATURES
    
    def write_partition(path, rows):
        with open(path, "w", newline="", encoding="utf-8") as out:
            writer = csv.DictWriter(out, fieldnames=common_fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
            
    write_partition(os.path.join(PROCESSED_DIR, "train_features.csv"), train_rows)
    write_partition(os.path.join(PROCESSED_DIR, "val_features.csv"), val_rows)
    write_partition(os.path.join(PROCESSED_DIR, "test_internal_features.csv"), test_rows)
    
    catsa_fields = [
        "dataset", "subject_id", "condition", "window_idx",
        "has_wrist_modality", "has_chest_modality"
    ] + WRIST_CORE_FEATURES
    with open(os.path.join(PROCESSED_DIR, "test_external_catsa_features.csv"), "w", newline="", encoding="utf-8") as out:
        writer = csv.DictWriter(out, fieldnames=catsa_fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(catsa_rows)
        
    # Feature-by-feature missingness and NaN audit
    def get_feature_missingness(rows, feats):
        res = {}
        total = len(rows)
        for f in feats:
            nan_cnt = 0
            for r in rows:
                v = r.get(f, "")
                if v == "" or v is None or v.lower() == "nan":
                    nan_cnt += 1
            res[f] = {
                "nan_count": nan_cnt,
                "nan_pct": round(nan_cnt / max(1, total) * 100, 2)
            }
        return res

    def get_stats(rows, name):
        targets = [int(r["target_binary"]) for r in rows if "target_binary" in r]
        subjects = sorted(list(set([f"{r['dataset']}_{r['subject_id'].split('_')[0]}" for r in rows])))
        n_0 = targets.count(0)
        n_1 = targets.count(1)
        ratio = round(n_0 / max(1, n_1), 2)
        missingness = get_feature_missingness(rows, WRIST_CORE_FEATURES)
        total_nan_entries = sum(v["nan_count"] for v in missingness.values())
        
        return {
            "partition": name,
            "total_windows": len(rows),
            "unique_subjects_count": len(subjects),
            "unique_subjects": subjects,
            "class_0_non_stress": n_0,
            "class_1_acute_stress": n_1,
            "class_0_pct": round(n_0 / max(1, len(targets)) * 100, 1),
            "class_1_pct": round(n_1 / max(1, len(targets)) * 100, 1),
            "empirical_imbalance_ratio": ratio,
            "total_nan_entries_across_features": total_nan_entries,
            "feature_missingness": missingness
        }
        
    stats_train = get_stats(train_rows, "train")
    stats_val = get_stats(val_rows, "validation")
    stats_test = get_stats(test_rows, "internal_test")
    
    catsa_missingness = get_feature_missingness(catsa_rows, WRIST_CORE_FEATURES)
    stats_catsa = {
        "partition": "external_catsa",
        "total_windows": len(catsa_rows),
        "unique_subjects_count": len(catsa_subs),
        "unique_subjects": sorted(list(catsa_subs)),
        "total_nan_entries_across_features": sum(v["nan_count"] for v in catsa_missingness.values()),
        "feature_missingness": catsa_missingness
    }
    
    summary = {
        "summary_version": "2.1.0",
        "modality_design": {
            "wrist_common_core_features_count": len(WRIST_CORE_FEATURES),
            "chest_additional_features_count": len(CHEST_ADDITIONAL_FEATURES),
            "zero_imputation_policy": "STRICT_ZERO_SYNTHETIC_IMPUTATION",
            "modality_flags": ["has_wrist_modality", "has_chest_modality"]
        },
        "leakage_audit": {
            "subject_overlap_train_val": overlap_train_val,
            "subject_overlap_train_test": overlap_train_test,
            "subject_overlap_val_test": overlap_val_test,
            "subject_overlap_train_catsa": overlap_train_catsa,
            "zero_leakage_verified": zero_leakage
        },
        "partitions": {
            "train": stats_train,
            "validation": stats_val,
            "internal_test": stats_test,
            "external_catsa": stats_catsa
        }
    }
    
    summary_path = os.path.join(PROCESSED_DIR, "extraction_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
        
    print("\n==========================================", flush=True)
    print("EXTRACTION & PARTITIONING AUDIT SUMMARY", flush=True)
    print("==========================================", flush=True)
    print(f"Zero Subject Leakage: {zero_leakage}", flush=True)
    print(f"Train Set: {len(train_rows):,} windows ({stats_train['unique_subjects_count']} subjects) | Class 0: {stats_train['class_0_pct']}%, Class 1: {stats_train['class_1_pct']}% | Imbalance Ratio: {stats_train['empirical_imbalance_ratio']}", flush=True)
    print(f"Val Set:   {len(val_rows):,} windows ({stats_val['unique_subjects_count']} subjects) | Class 0: {stats_val['class_0_pct']}%, Class 1: {stats_val['class_1_pct']}%", flush=True)
    print(f"Test Set:  {len(test_rows):,} windows ({stats_test['unique_subjects_count']} subjects) | Class 0: {stats_test['class_0_pct']}%, Class 1: {stats_test['class_1_pct']}%", flush=True)
    print(f"CATSA Ext: {len(catsa_rows):,} windows ({stats_catsa['unique_subjects_count']} subjects)", flush=True)
    print(f"Total Unique Human Participants: {stats_train['unique_subjects_count'] + stats_val['unique_subjects_count'] + stats_test['unique_subjects_count'] + stats_catsa['unique_subjects_count']}", flush=True)
    print(f"Summary JSON written to: {summary_path}\n", flush=True)
    return summary

if __name__ == "__main__":
    build_partitions()
