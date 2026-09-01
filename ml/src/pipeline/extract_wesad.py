import os
import sys
import csv
import pickle
import time
import numpy as np
from scipy import signal

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')
sys.path.insert(0, r"d:\IITM\SIH\PROTOTYPE\ANTIGRAVITY\ANTI-INFO")
from ml.src.features.feature_lib import (
    extract_cardiovascular_features,
    extract_hrv_features,
    extract_eda_features,
    extract_temperature_features,
    extract_accelerometry_features,
    extract_chest_respiration_features,
    extract_chest_emg_features,
    extract_chest_ecg_features
)

def derive_bvp_hr_and_prv(bvp_array, fs=64.0):
    bvp = np.asarray(bvp_array, dtype=np.float64)
    if len(bvp) < int(fs * 30):
        return None, None
        
    nyq = 0.5 * fs
    b, a = signal.butter(2, [0.5 / nyq, 3.5 / nyq], btype='bandpass')
    filtered = signal.filtfilt(b, a, bvp)
    
    min_dist = int(fs * 0.35) # Max 170 bpm
    prominence = np.std(filtered) * 0.3
    peaks, _ = signal.find_peaks(filtered, distance=min_dist, prominence=prominence)
    
    if len(peaks) < 15: # Minimum 15 pulse peaks in 60s
        return None, None
        
    peak_times = peaks / fs
    ibi_sec = np.diff(peak_times)
    ibi_ms = ibi_sec * 1000.0
    
    valid_mask = (ibi_ms >= 300.0) & (ibi_ms <= 2000.0)
    if np.sum(valid_mask) < 15:
        return None, None
        
    valid_ibi_ms = ibi_ms[valid_mask]
    hr_bpm = 60.0 / (valid_ibi_ms / 1000.0)
    
    return hr_bpm, valid_ibi_ms

def extract_wesad_dataset(dataset_root, processed_dir):
    wesad_dir = os.path.join(dataset_root, "archive", "WESAD")
    subjects = [d for d in os.listdir(wesad_dir) if os.path.isdir(os.path.join(wesad_dir, d)) and d.startswith("S")]
    subjects.sort()
    
    os.makedirs(processed_dir, exist_ok=True)
    wrist_csv = os.path.join(processed_dir, "wesad_features.csv")
    chest_csv = os.path.join(processed_dir, "wesad_multimodal_chest_features.csv")
    
    wrist_fields = [
        "dataset", "subject_id", "window_idx", "target_binary", "source_label",
        "has_wrist_modality", "has_chest_modality",
        "hr_mean", "hr_std", "hr_min", "hr_max", "hr_slope",
        "hrv_rmssd", "hrv_sdnn", "hrv_pnn50", "hrv_cv",
        "eda_mean", "eda_std", "eda_min", "eda_max", "eda_slope",
        "eda_tonic_mean", "eda_phasic_peaks", "eda_phasic_max_amplitude", "eda_phasic_auc",
        "temp_mean", "temp_std", "temp_slope",
        "acc_magnitude_mean", "acc_magnitude_std", "acc_motion_energy", "acc_peak_acceleration"
    ]
    
    chest_fields = wrist_fields + [
        "chest_ecg_hr_mean", "chest_ecg_hrv_rmssd", "chest_ecg_hrv_sdnn",
        "chest_resp_rate", "chest_resp_std", "chest_emg_mean"
    ]
    
    total_windows = 0
    class_counts = {0: 0, 1: 0}
    
    with open(wrist_csv, "w", newline="", encoding="utf-8") as w_out, \
         open(chest_csv, "w", newline="", encoding="utf-8") as c_out:
         
        w_writer = csv.DictWriter(w_out, fieldnames=wrist_fields)
        c_writer = csv.DictWriter(c_out, fieldnames=chest_fields)
        w_writer.writeheader()
        c_writer.writeheader()
        
        for idx, s in enumerate(subjects, 1):
            pkl_path = os.path.join(wesad_dir, s, f"{s}.pkl")
            if not os.path.exists(pkl_path):
                continue
                
            t0 = time.time()
            print(f"[{idx}/{len(subjects)}] Loading & Extracting WESAD Subject {s}...", flush=True)
            with open(pkl_path, "rb") as f:
                data = pickle.load(f, encoding="latin1")
                
            labels = data["label"]
            wrist_data = data["signal"]["wrist"]
            chest_data = data["signal"]["chest"]
            
            fs_chest = 700
            fs_bvp = 64
            fs_acc = 32
            fs_eda = 4
            fs_temp = 4
            
            win_sec = 60
            step_sec = 30
            
            win_len_chest = win_sec * fs_chest
            step_len_chest = step_sec * fs_chest
            n_samples_chest = len(labels)
            
            w_idx = 0
            s_windows = 0
            for start_chest in range(0, n_samples_chest - win_len_chest + 1, step_len_chest):
                end_chest = start_chest + win_len_chest
                win_labels = labels[start_chest:end_chest]
                
                vals, counts = np.unique(win_labels, return_counts=True)
                dom_label = int(vals[np.argmax(counts)])
                dom_pct = np.max(counts) / len(win_labels)
                
                if dom_pct < 0.70:
                    continue
                    
                if dom_label in [1, 3, 4]:
                    target = 0
                elif dom_label == 2:
                    target = 1
                else:
                    continue
                    
                t_start = start_chest / fs_chest
                t_end = end_chest / fs_chest
                
                bvp_slice = wrist_data["BVP"][int(t_start * fs_bvp) : int(t_end * fs_bvp)].flatten()
                acc_slice = wrist_data["ACC"][int(t_start * fs_acc) : int(t_end * fs_acc)]
                eda_slice = wrist_data["EDA"][int(t_start * fs_eda) : int(t_end * fs_eda)].flatten()
                temp_slice = wrist_data["TEMP"][int(t_start * fs_temp) : int(t_end * fs_temp)].flatten()
                
                ecg_slice = chest_data["ECG"][start_chest:end_chest].flatten()
                resp_slice = chest_data["Resp"][start_chest:end_chest].flatten()
                emg_slice = chest_data["EMG"][start_chest:end_chest].flatten()
                
                hr_arr, prv_ibi_arr = derive_bvp_hr_and_prv(bvp_slice, fs=fs_bvp)
                
                # Base row with wrist features
                row_wrist = {
                    "dataset": "WESAD",
                    "subject_id": s,
                    "window_idx": w_idx,
                    "target_binary": target,
                    "source_label": dom_label,
                    "has_wrist_modality": 1,
                    "has_chest_modality": 0
                }
                row_wrist.update(extract_cardiovascular_features(hr_arr, duration_sec=win_sec))
                row_wrist.update(extract_hrv_features(prv_ibi_arr))
                row_wrist.update(extract_eda_features(eda_slice, fs=fs_eda, duration_sec=win_sec))
                row_wrist.update(extract_temperature_features(temp_slice, duration_sec=win_sec))
                row_wrist.update(extract_accelerometry_features(acc_slice[:, 0], acc_slice[:, 1], acc_slice[:, 2]))
                
                # Full row with chest features
                row_chest = dict(row_wrist)
                row_chest["has_chest_modality"] = 1
                row_chest.update(extract_chest_ecg_features(ecg_slice, fs=fs_chest))
                row_chest.update(extract_chest_respiration_features(resp_slice, fs=fs_chest))
                row_chest.update(extract_chest_emg_features(emg_slice))
                
                w_writer.writerow(row_wrist)
                c_writer.writerow(row_chest)
                
                class_counts[target] += 1
                total_windows += 1
                s_windows += 1
                w_idx += 1
                
            w_out.flush()
            c_out.flush()
            elapsed = time.time() - t0
            print(f"  -> {s} complete: {s_windows} windows extracted in {elapsed:.1f}s.", flush=True)
            del data, labels, wrist_data, chest_data
            
    print(f"\n[OK] WESAD Extraction Complete: {total_windows:,} total windows extracted.", flush=True)
    return total_windows, class_counts

if __name__ == "__main__":
    d_root = r"d:\IITM\SIH\PROTOTYPE\ANTIGRAVITY\ANTI-INFO\Dataset"
    p_dir = r"d:\IITM\SIH\PROTOTYPE\ANTIGRAVITY\ANTI-INFO\ml\data\processed"
    extract_wesad_dataset(d_root, p_dir)
