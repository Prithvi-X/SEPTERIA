import os
import sys
import csv
import numpy as np

sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')
sys.path.insert(0, r"d:\IITM\SIH\PROTOTYPE\ANTIGRAVITY\ANTI-INFO")
from ml.src.features.feature_lib import (
    extract_cardiovascular_features,
    extract_hrv_features,
    extract_eda_features,
    extract_temperature_features,
    extract_accelerometry_features
)

def load_e4_csv(filepath):
    if not os.path.exists(filepath):
        return None, 1.0
    
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.reader(f)
        try:
            start_time_str = next(reader)[0]
            fs_row = next(reader)
            fs = float(fs_row[0])
            data = [list(map(float, row)) for row in reader if row]
        except (StopIteration, ValueError, IndexError):
            return None, 1.0
            
    if not data:
        return None, fs
    arr = np.array(data, dtype=np.float64)
    if arr.ndim == 2 and arr.shape[1] == 1:
        arr = arr.flatten()
    return arr, fs

def load_e4_ibi_csv(filepath):
    if not os.path.exists(filepath):
        return None
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.reader(f)
        try:
            start_time_str = next(reader)[0]
            data = []
            for row in reader:
                if len(row) >= 2:
                    try:
                        offset_s = float(row[0])
                        ibi_s = float(row[1])
                        data.append((offset_s, ibi_s * 1000.0)) # Convert to ms
                    except ValueError:
                        continue
        except (StopIteration, ValueError, IndexError):
            return None
    return data

def extract_physionet_dataset(dataset_root, output_csv):
    pn_wearable = os.path.join(
        dataset_root,
        "wearable-device-dataset-from-induced-stress-and-structured-exercise-sessions-1.0.1",
        "wearable-device-dataset-from-induced-stress-and-structured-exercise-sessions-1.0.1",
        "Wearable_Dataset"
    )
    
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    
    fieldnames = [
        "dataset", "subject_id", "protocol", "window_idx", "target_binary", "source_label",
        "has_wrist_modality", "has_chest_modality",
        "hr_mean", "hr_std", "hr_min", "hr_max", "hr_slope",
        "hrv_rmssd", "hrv_sdnn", "hrv_pnn50", "hrv_cv",
        "eda_mean", "eda_std", "eda_min", "eda_max", "eda_slope",
        "eda_tonic_mean", "eda_phasic_peaks", "eda_phasic_max_amplitude", "eda_phasic_auc",
        "temp_mean", "temp_std", "temp_slope",
        "acc_magnitude_mean", "acc_magnitude_std", "acc_motion_energy", "acc_peak_acceleration"
    ]
    
    total_windows = 0
    class_counts = {0: 0, 1: 0}
    protocol_counts = {"STRESS": 0, "AEROBIC": 0, "ANAEROBIC": 0}
    
    win_sec = 60
    step_sec = 30
    
    with open(output_csv, "w", newline="", encoding="utf-8") as out_f:
        writer = csv.DictWriter(out_f, fieldnames=fieldnames)
        writer.writeheader()
        
        for protocol in ["STRESS", "AEROBIC", "ANAEROBIC"]:
            prot_dir = os.path.join(pn_wearable, protocol)
            if not os.path.exists(prot_dir):
                continue
                
            sessions = sorted(os.listdir(prot_dir))
            for s_id in sessions:
                s_dir = os.path.join(prot_dir, s_id)
                if not os.path.isdir(s_dir):
                    continue
                    
                acc, acc_fs = load_e4_csv(os.path.join(s_dir, "ACC.csv"))
                eda, eda_fs = load_e4_csv(os.path.join(s_dir, "EDA.csv"))
                temp, temp_fs = load_e4_csv(os.path.join(s_dir, "TEMP.csv"))
                hr, hr_fs = load_e4_csv(os.path.join(s_dir, "HR.csv"))
                ibi_data = load_e4_ibi_csv(os.path.join(s_dir, "IBI.csv"))
                
                if acc is None or eda is None or temp is None or hr is None:
                    continue
                if len(eda) < int(eda_fs * win_sec) or len(hr) < int(hr_fs * win_sec):
                    continue
                    
                duration_sec = min(
                    len(acc) / acc_fs,
                    len(eda) / eda_fs,
                    len(temp) / temp_fs,
                    len(hr) / hr_fs
                )
                
                w_idx = 0
                n_steps = int((duration_sec - win_sec) / step_sec) + 1
                for step in range(n_steps):
                    t_start = step * step_sec
                    t_end = t_start + win_sec
                    
                    if protocol == "AEROBIC":
                        target = 0
                        source_label = "AEROBIC_CYCLE"
                    elif protocol == "ANAEROBIC":
                        target = 0
                        source_label = "ANAEROBIC_SPRINT"
                    else: # STRESS
                        if t_start < 120:
                            target = 0
                            source_label = "STRESS_BASELINE"
                        elif t_end > (duration_sec - 120):
                            target = 0
                            source_label = "STRESS_REST"
                        else:
                            target = 1
                            source_label = "STRESS_TASK"
                            
                    hr_slice = hr[int(t_start * hr_fs) : int(t_end * hr_fs)]
                    eda_slice = eda[int(t_start * eda_fs) : int(t_end * eda_fs)]
                    temp_slice = temp[int(t_start * temp_fs) : int(t_end * temp_fs)]
                    acc_slice = acc[int(t_start * acc_fs) : int(t_end * acc_fs)]
                    
                    if len(hr_slice) < 5 or len(eda_slice) < 5:
                        continue
                        
                    # Strict uncorrupted IBI: require >= 15 empirical beat intervals in window
                    if ibi_data:
                        ibis_in_win = [item[1] for item in ibi_data if t_start <= item[0] < t_end]
                        ibi_arr = np.array(ibis_in_win) if len(ibis_in_win) >= 15 else None
                    else:
                        ibi_arr = None
                        
                    row = {
                        "dataset": "PhysioNet",
                        "subject_id": s_id,
                        "protocol": protocol,
                        "window_idx": w_idx,
                        "target_binary": target,
                        "source_label": source_label,
                        "has_wrist_modality": 1,
                        "has_chest_modality": 0
                    }
                    row.update(extract_cardiovascular_features(hr_slice, duration_sec=win_sec))
                    row.update(extract_hrv_features(ibi_arr))
                    row.update(extract_eda_features(eda_slice, fs=eda_fs, duration_sec=win_sec))
                    row.update(extract_temperature_features(temp_slice, duration_sec=win_sec))
                    row.update(extract_accelerometry_features(acc_slice[:, 0], acc_slice[:, 1], acc_slice[:, 2]))
                    
                    writer.writerow(row)
                    class_counts[target] += 1
                    protocol_counts[protocol] += 1
                    total_windows += 1
                    w_idx += 1
                    
            print(f"PhysioNet Protocol [{protocol}] Extraction Complete ({protocol_counts[protocol]} windows).", flush=True)
            
    print(f"\n[OK] PhysioNet Total Windows: {total_windows:,}", flush=True)
    return total_windows, class_counts

if __name__ == "__main__":
    d_root = r"d:\IITM\SIH\PROTOTYPE\ANTIGRAVITY\ANTI-INFO\Dataset"
    out_p = r"d:\IITM\SIH\PROTOTYPE\ANTIGRAVITY\ANTI-INFO\ml\data\processed\physionet_features.csv"
    extract_physionet_dataset(d_root, out_p)
