import os
import sys
import csv
import numpy as np
from scipy import signal

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')
sys.path.insert(0, r"d:\IITM\SIH\PROTOTYPE\ANTIGRAVITY\ANTI-INFO")
from ml.src.features.feature_lib import (
    extract_cardiovascular_features,
    extract_hrv_features,
    extract_eda_features,
    extract_temperature_features,
    extract_accelerometry_features
)

def derive_prv_from_bvp(bvp_slice, fs=64.0):
    """
    Derives Pulse Rate Variability (PRV) from raw 64 Hz optical Photoplethysmogram (BVP).
    Applies 2nd-order Butterworth bandpass (0.5 - 3.5 Hz).
    Enforces minimum 15 valid pulse beats (300ms - 2000ms) in 60-second window.
    Returns None if signal is degraded / fewer than 15 beats detected.
    """
    bvp = np.asarray(bvp_slice, dtype=np.float64)
    if len(bvp) < int(fs * 30):
        return None
        
    nyq = 0.5 * fs
    b, a = signal.butter(2, [0.5 / nyq, 3.5 / nyq], btype='bandpass')
    filtered = signal.filtfilt(b, a, bvp)
    
    min_dist = int(fs * 0.35) # Maximum 170 bpm
    prominence = np.std(filtered) * 0.3
    peaks, _ = signal.find_peaks(filtered, distance=min_dist, prominence=prominence)
    
    if len(peaks) < 15: # Strict minimum 15 beats in 60s
        return None
        
    peak_times_ms = (peaks / fs) * 1000.0
    ibis_ms = np.diff(peak_times_ms)
    
    # Filter physiological bounds (300ms to 2000ms)
    valid_mask = (ibis_ms >= 300.0) & (ibis_ms <= 2000.0)
    valid_ibis = ibis_ms[valid_mask]
    
    if len(valid_ibis) < 15:
        return None
        
    return valid_ibis

def extract_catsa_dataset(dataset_root, output_csv):
    catsa_raw = os.path.join(dataset_root, "CATSA", "CATSA")
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    
    fieldnames = [
        "dataset", "subject_id", "condition", "window_idx",
        "has_wrist_modality", "has_chest_modality",
        "hr_mean", "hr_std", "hr_min", "hr_max", "hr_slope",
        "hrv_rmssd", "hrv_sdnn", "hrv_pnn50", "hrv_cv",
        "eda_mean", "eda_std", "eda_min", "eda_max", "eda_slope",
        "eda_tonic_mean", "eda_phasic_peaks", "eda_phasic_max_amplitude", "eda_phasic_auc",
        "temp_mean", "temp_std", "temp_slope",
        "acc_magnitude_mean", "acc_magnitude_std", "acc_motion_energy", "acc_peak_acceleration"
    ]
    
    subjects = [d for d in os.listdir(catsa_raw) if os.path.isdir(os.path.join(catsa_raw, d)) and d.startswith("Sub")]
    subjects.sort(key=lambda x: int(x.replace("Sub", "")))
    conditions = ["Baseline", "Logic", "Nback", "Stroop", "Sudoku"]
    
    total_windows = 0
    cond_counts = {c: 0 for c in conditions}
    
    win_sec = 60
    step_sec = 30
    fs_bvp = 64
    fs_hr = 1
    fs_acc = 32
    fs_eda = 4
    fs_temp = 4
    
    def load_column_csv(fp):
        if not os.path.exists(fp):
            return None
        vals = []
        with open(fp, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            for row in reader:
                if row:
                    try:
                        if len(row) == 1:
                            vals.append(float(row[0]))
                        else:
                            vals.append([float(x) for x in row])
                    except ValueError:
                        continue
        if not vals:
            return None
        return np.array(vals, dtype=np.float64)

    with open(output_csv, "w", newline="", encoding="utf-8") as out_f:
        writer = csv.DictWriter(out_f, fieldnames=fieldnames)
        writer.writeheader()
        
        for s_idx, s in enumerate(subjects, 1):
            s_dir = os.path.join(catsa_raw, s)
            if not os.path.isdir(s_dir):
                continue
                
            for cond in conditions:
                cond_dir = os.path.join(s_dir, cond)
                if not os.path.isdir(cond_dir):
                    continue
                    
                bvp = load_column_csv(os.path.join(cond_dir, "BVP.csv"))
                hr = load_column_csv(os.path.join(cond_dir, "HR.csv"))
                eda = load_column_csv(os.path.join(cond_dir, "EDA.csv"))
                temp = load_column_csv(os.path.join(cond_dir, "TEMP.csv"))
                acc = load_column_csv(os.path.join(cond_dir, "ACC.csv"))
                
                if bvp is None or hr is None or eda is None or temp is None or acc is None:
                    continue
                    
                dur = min(
                    len(bvp)/fs_bvp,
                    len(hr)/fs_hr,
                    len(eda)/fs_eda,
                    len(temp)/fs_temp,
                    len(acc)/fs_acc
                )
                
                if dur < win_sec:
                    continue
                    
                n_steps = int((dur - win_sec) / step_sec) + 1
                for step in range(n_steps):
                    t_start = step * step_sec
                    t_end = t_start + win_sec
                    
                    bvp_slice = bvp[int(t_start * fs_bvp) : int(t_end * fs_bvp)]
                    hr_slice = hr[int(t_start * fs_hr) : int(t_end * fs_hr)]
                    eda_slice = eda[int(t_start * fs_eda) : int(t_end * fs_eda)]
                    temp_slice = temp[int(t_start * fs_temp) : int(t_end * fs_temp)]
                    acc_slice = acc[int(t_start * fs_acc) : int(t_end * fs_acc)]
                    
                    # 1. Cardiovascular metrics from 1 Hz HR stream
                    cardio_feats = extract_cardiovascular_features(hr_slice, duration_sec=win_sec)
                    
                    # 2. Pulse Rate Variability (PRV) strictly from 64 Hz optical BVP
                    prv_ibis = derive_prv_from_bvp(bvp_slice, fs=fs_bvp)
                    hrv_feats = extract_hrv_features(prv_ibis)
                    
                    # 3. EDA, Temp, ACC
                    eda_feats = extract_eda_features(eda_slice, fs=fs_eda, duration_sec=win_sec)
                    temp_feats = extract_temperature_features(temp_slice, duration_sec=win_sec)
                    
                    if acc_slice.ndim == 2 and acc_slice.shape[1] == 3:
                        acc_feats = extract_accelerometry_features(acc_slice[:, 0], acc_slice[:, 1], acc_slice[:, 2])
                    else:
                        acc_feats = extract_accelerometry_features(np.array([]), np.array([]), np.array([]))
                        
                    row = {
                        "dataset": "CATSA",
                        "subject_id": s,
                        "condition": cond,
                        "window_idx": step,
                        "has_wrist_modality": 1,
                        "has_chest_modality": 0
                    }
                    row.update(cardio_feats)
                    row.update(hrv_feats)
                    row.update(eda_feats)
                    row.update(temp_feats)
                    row.update(acc_feats)
                    
                    writer.writerow(row)
                    total_windows += 1
                    cond_counts[cond] += 1
                    
    print(f"\n[OK] CATSA Extraction Complete: {total_windows:,} total windows across {len(subjects)} subjects.", flush=True)
    print("  Condition Breakdown:", cond_counts, flush=True)
    return total_windows, cond_counts

if __name__ == "__main__":
    d_root = r"d:\IITM\SIH\PROTOTYPE\ANTIGRAVITY\ANTI-INFO\Dataset"
    out_p = r"d:\IITM\SIH\PROTOTYPE\ANTIGRAVITY\ANTI-INFO\ml\data\processed\catsa_features.csv"
    extract_catsa_dataset(d_root, out_p)
