"""
SEPTERIA Feature Extraction Library
Scientific, uncorrupted signal transformations for 60-second physiological and motion telemetry.
Strict Policy: Zero synthetic fallback values. If data is missing/invalid/insufficient, return np.nan.
"""

import numpy as np
from scipy import signal

def extract_cardiovascular_features(hr_array, duration_sec=60.0):
    """
    Extracts heart rate summary metrics from an array of 1 Hz HR values (bpm).
    Returns np.nan for metrics if HR array is empty, corrupted, or invalid.
    """
    if hr_array is None:
        return {
            "hr_mean": np.nan, "hr_std": np.nan, "hr_min": np.nan, "hr_max": np.nan, "hr_slope": np.nan
        }
        
    hr = np.asarray(hr_array, dtype=np.float64)
    hr = hr[~np.isnan(hr)]
    # Physiological sanity filter: 30 bpm to 240 bpm
    valid_hr = hr[(hr >= 30.0) & (hr <= 240.0)]
    
    if len(valid_hr) < 5: # Need at least 5s of valid HR readings
        return {
            "hr_mean": np.nan, "hr_std": np.nan, "hr_min": np.nan, "hr_max": np.nan, "hr_slope": np.nan
        }
    
    mean_val = float(np.mean(valid_hr))
    std_val = float(np.std(valid_hr, ddof=1)) if len(valid_hr) > 1 else 0.0
    min_val = float(np.min(valid_hr))
    max_val = float(np.max(valid_hr))
    
    if len(valid_hr) >= 2:
        t = np.linspace(0, duration_sec, len(valid_hr))
        slope_val = float(np.polyfit(t, valid_hr, 1)[0])
    else:
        slope_val = 0.0
        
    return {
        "hr_mean": round(mean_val, 4),
        "hr_std": round(std_val, 4),
        "hr_min": round(min_val, 4),
        "hr_max": round(max_val, 4),
        "hr_slope": round(slope_val, 6)
    }

def extract_hrv_features(ibi_array_ms):
    """
    Extracts time-domain Heart Rate Variability (HRV) / Pulse Rate Variability (PRV) metrics from NN/IBI intervals (ms).
    Requires at least 15 valid intervals in a 60-second window (representing at least 15-20s of stable rhythm).
    Returns np.nan if fewer than 15 valid intervals exist.
    """
    if ibi_array_ms is None:
        return {
            "hrv_rmssd": np.nan, "hrv_sdnn": np.nan, "hrv_pnn50": np.nan, "hrv_cv": np.nan
        }
        
    ibi = np.asarray(ibi_array_ms, dtype=np.float64)
    ibi = ibi[~np.isnan(ibi)]
    # Physiological filtering: 300 ms (200 bpm) to 2000 ms (30 bpm)
    valid_ibi = ibi[(ibi >= 300.0) & (ibi <= 2000.0)]
    
    if len(valid_ibi) < 15: # Strict minimum threshold of 15 valid intervals
        return {
            "hrv_rmssd": np.nan, "hrv_sdnn": np.nan, "hrv_pnn50": np.nan, "hrv_cv": np.nan
        }
    
    diffs = np.diff(valid_ibi)
    rmssd = float(np.sqrt(np.mean(diffs ** 2)))
    sdnn = float(np.std(valid_ibi, ddof=1))
    pnn50 = float(np.sum(np.abs(diffs) > 50.0) / len(diffs) * 100.0)
    mean_ibi = float(np.mean(valid_ibi))
    cv = float((sdnn / mean_ibi) * 100.0) if mean_ibi > 0 else np.nan
    
    return {
        "hrv_rmssd": round(rmssd, 4),
        "hrv_sdnn": round(sdnn, 4),
        "hrv_pnn50": round(pnn50, 4),
        "hrv_cv": round(cv, 4)
    }

def extract_eda_features(eda_array, fs=4.0, duration_sec=60.0):
    """
    Extracts sympathetic Electrodermal Activity features including Tonic SCL and Phasic SCR metrics.
    Returns np.nan if EDA signal is empty, flatlined at zero (<0.005 uS), or invalid.
    """
    if eda_array is None:
        return {
            "eda_mean": np.nan, "eda_std": np.nan, "eda_min": np.nan, "eda_max": np.nan,
            "eda_slope": np.nan, "eda_tonic_mean": np.nan, "eda_phasic_peaks": np.nan,
            "eda_phasic_max_amplitude": np.nan, "eda_phasic_auc": np.nan
        }
        
    eda = np.asarray(eda_array, dtype=np.float64)
    eda = eda[~np.isnan(eda)]
    # Contact check: conductance should be > 0.005 uS
    valid_eda = eda[eda > 0.005]
    
    if len(valid_eda) < int(fs * 5): # Require at least 5s of valid skin contact
        return {
            "eda_mean": np.nan, "eda_std": np.nan, "eda_min": np.nan, "eda_max": np.nan,
            "eda_slope": np.nan, "eda_tonic_mean": np.nan, "eda_phasic_peaks": np.nan,
            "eda_phasic_max_amplitude": np.nan, "eda_phasic_auc": np.nan
        }
    
    mean_val = float(np.mean(valid_eda))
    std_val = float(np.std(valid_eda, ddof=1)) if len(valid_eda) > 1 else 0.0
    min_val = float(np.min(valid_eda))
    max_val = float(np.max(valid_eda))
    
    if len(valid_eda) >= 2:
        t = np.linspace(0, duration_sec, len(valid_eda))
        slope_val = float(np.polyfit(t, valid_eda, 1)[0])
    else:
        slope_val = 0.0
        
    # Tonic extraction via 2nd-order lowpass Butterworth filter at 0.05 Hz
    nyquist = 0.5 * fs
    cutoff = min(0.05, nyquist * 0.9)
    b, a = signal.butter(2, cutoff / nyquist, btype='low')
    
    if len(valid_eda) >= 15:
        tonic = signal.filtfilt(b, a, valid_eda)
    else:
        tonic = valid_eda.copy()
        
    tonic_mean = float(np.mean(tonic))
    phasic = valid_eda - tonic
    phasic = np.maximum(0.0, phasic)
    
    min_distance_samples = max(1, int(fs * 1.0))
    peaks, props = signal.find_peaks(phasic, prominence=0.02, distance=min_distance_samples)
    
    peak_count = int(len(peaks))
    max_amp = float(np.max(phasic[peaks])) if len(peaks) > 0 else 0.0
    auc = float(np.trapezoid(phasic, dx=1.0/fs)) if len(phasic) > 1 else 0.0
    
    return {
        "eda_mean": round(mean_val, 4),
        "eda_std": round(std_val, 4),
        "eda_min": round(min_val, 4),
        "eda_max": round(max_val, 4),
        "eda_slope": round(slope_val, 6),
        "eda_tonic_mean": round(tonic_mean, 4),
        "eda_phasic_peaks": peak_count,
        "eda_phasic_max_amplitude": round(max_amp, 4),
        "eda_phasic_auc": round(auc, 4)
    }

def extract_temperature_features(temp_array, duration_sec=60.0):
    """
    Extracts skin surface temperature metrics.
    Filters non-physiological skin temperature (< 20 deg C or > 45 deg C).
    """
    if temp_array is None:
        return {"temp_mean": np.nan, "temp_std": np.nan, "temp_slope": np.nan}
        
    temp = np.asarray(temp_array, dtype=np.float64)
    temp = temp[~np.isnan(temp)]
    valid_temp = temp[(temp >= 20.0) & (temp <= 45.0)]
    
    if len(valid_temp) == 0:
        return {"temp_mean": np.nan, "temp_std": np.nan, "temp_slope": np.nan}
        
    mean_val = float(np.mean(valid_temp))
    std_val = float(np.std(valid_temp, ddof=1)) if len(valid_temp) > 1 else 0.0
    
    if len(valid_temp) >= 2:
        t = np.linspace(0, duration_sec, len(valid_temp))
        slope_val = float(np.polyfit(t, valid_temp, 1)[0])
    else:
        slope_val = 0.0
        
    return {
        "temp_mean": round(mean_val, 4),
        "temp_std": round(std_val, 4),
        "temp_slope": round(slope_val, 6)
    }

def extract_accelerometry_features(acc_x, acc_y, acc_z):
    """
    Extracts 3-axis accelerometer kinetic features and motion energy proxy.
    """
    if acc_x is None or acc_y is None or acc_z is None:
        return {
            "acc_magnitude_mean": np.nan, "acc_magnitude_std": np.nan,
            "acc_motion_energy": np.nan, "acc_peak_acceleration": np.nan
        }
        
    ax = np.asarray(acc_x, dtype=np.float64)
    ay = np.asarray(acc_y, dtype=np.float64)
    az = np.asarray(acc_z, dtype=np.float64)
    
    if len(ax) == 0 or len(ay) == 0 or len(az) == 0:
        return {
            "acc_magnitude_mean": np.nan, "acc_magnitude_std": np.nan,
            "acc_motion_energy": np.nan, "acc_peak_acceleration": np.nan
        }
        
    mag = np.sqrt(ax**2 + ay**2 + az**2)
    mag = mag[~np.isnan(mag)]
    
    if len(mag) == 0:
        return {
            "acc_magnitude_mean": np.nan, "acc_magnitude_std": np.nan,
            "acc_motion_energy": np.nan, "acc_peak_acceleration": np.nan
        }
        
    mean_mag = float(np.mean(mag))
    std_mag = float(np.std(mag, ddof=1)) if len(mag) > 1 else 0.0
    motion_energy = float(np.var(mag))
    peak_acc = float(np.max(mag))
    
    return {
        "acc_magnitude_mean": round(mean_mag, 4),
        "acc_magnitude_std": round(std_mag, 4),
        "acc_motion_energy": round(motion_energy, 4),
        "acc_peak_acceleration": round(peak_acc, 4)
    }

def extract_chest_respiration_features(resp_array, fs=700.0):
    """
    Extracts respiration rate (breaths/min) and variability from chest expansion band.
    Returns np.nan if chest sensor is missing or detached.
    """
    if resp_array is None:
        return {"chest_resp_rate": np.nan, "chest_resp_std": np.nan}
        
    resp = np.asarray(resp_array, dtype=np.float64)
    resp = resp[~np.isnan(resp)]
    if len(resp) < int(fs * 10):
        return {"chest_resp_rate": np.nan, "chest_resp_std": np.nan}
        
    nyq = 0.5 * fs
    b, a = signal.butter(2, [0.1 / nyq, 0.5 / nyq], btype='bandpass')
    filtered = signal.filtfilt(b, a, resp)
    
    peaks, _ = signal.find_peaks(filtered, distance=int(fs * 1.5))
    if len(peaks) < 2:
        return {"chest_resp_rate": np.nan, "chest_resp_std": np.nan}
        
    resp_rate = float(len(peaks) * (60.0 / (len(resp) / fs)))
    resp_std = float(np.std(filtered, ddof=1))
    
    return {
        "chest_resp_rate": round(resp_rate, 4),
        "chest_resp_std": round(resp_std, 4)
    }

def extract_chest_emg_features(emg_array):
    """
    Extracts root mean square (RMS) muscle tension from trapezius EMG.
    Returns np.nan if chest EMG sensor is absent.
    """
    if emg_array is None:
        return {"chest_emg_mean": np.nan}
        
    emg = np.asarray(emg_array, dtype=np.float64)
    emg = emg[~np.isnan(emg)]
    if len(emg) == 0:
        return {"chest_emg_mean": np.nan}
    rms = float(np.sqrt(np.mean(emg ** 2)))
    return {"chest_emg_mean": round(rms, 6)}

def extract_chest_ecg_features(ecg_array, fs=700.0):
    """
    Extracts true ECG-derived RR intervals, heart rate, and gold-standard ECG HRV metrics via Pan-Tompkins QRS detection.
    """
    if ecg_array is None:
        return {
            "chest_ecg_hr_mean": np.nan,
            "chest_ecg_hrv_rmssd": np.nan,
            "chest_ecg_hrv_sdnn": np.nan
        }
        
    ecg = np.asarray(ecg_array, dtype=np.float64)
    ecg = ecg[~np.isnan(ecg)]
    if len(ecg) < int(fs * 15):
        return {
            "chest_ecg_hr_mean": np.nan,
            "chest_ecg_hrv_rmssd": np.nan,
            "chest_ecg_hrv_sdnn": np.nan
        }
        
    nyq = 0.5 * fs
    b, a = signal.butter(2, [5.0 / nyq, 15.0 / nyq], btype='bandpass')
    filtered = signal.filtfilt(b, a, ecg)
    diff = np.diff(filtered)
    squared = diff ** 2
    int_win = int(fs * 0.15)
    integrated = np.convolve(squared, np.ones(int_win)/int_win, mode='same')
    
    peaks, _ = signal.find_peaks(integrated, distance=int(fs * 0.35), prominence=np.std(integrated) * 0.4)
    if len(peaks) < 15:
        return {
            "chest_ecg_hr_mean": np.nan,
            "chest_ecg_hrv_rmssd": np.nan,
            "chest_ecg_hrv_sdnn": np.nan
        }
        
    rr_ms = np.diff(peaks / fs) * 1000.0
    valid_rr = rr_ms[(rr_ms >= 300.0) & (rr_ms <= 2000.0)]
    if len(valid_rr) < 15:
        return {
            "chest_ecg_hr_mean": np.nan,
            "chest_ecg_hrv_rmssd": np.nan,
            "chest_ecg_hrv_sdnn": np.nan
        }
        
    mean_hr = float(60.0 / (np.mean(valid_rr) / 1000.0))
    rmssd = float(np.sqrt(np.mean(np.diff(valid_rr) ** 2)))
    sdnn = float(np.std(valid_rr, ddof=1))
    
    return {
        "chest_ecg_hr_mean": round(mean_hr, 4),
        "chest_ecg_hrv_rmssd": round(rmssd, 4),
        "chest_ecg_hrv_sdnn": round(sdnn, 4)
    }
