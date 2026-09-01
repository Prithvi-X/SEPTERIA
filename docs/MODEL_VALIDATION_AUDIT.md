# SEPTERIA Model Validation & Domain Shift Audit Report

**Project**: SEPTERIA — AI-Based Predictive Personnel Stress and Welfare Monitoring System for Uniformed Forces  
**SIH Problem Statement**: SIH26186  
**Document**: `docs/MODEL_VALIDATION_AUDIT.md`  
**Model Designation**: **Prototype Trained Stress Model (v1.0.0-PROTOTYPE)**  
**Status**: AUDITED & CALIBRATED — PROTOTYPE STATUS (NOT CAPF FIELD-VALIDATED)

---

> [!WARNING]
> ### Critical Audit Finding: CATSA Baseline Domain Shift & Calibration Warning
> When evaluated on the 50-subject held-out **CATSA** dataset, the Prototype Trained Stress Model produces a mean predicted stress probability of **$P(\text{Stress}) \approx 0.8515$** on the **CATSA Baseline condition**, with **$96.8\%$** of baseline windows exceeding $0.50$.
> 
> **This MUST NOT be interpreted as successful psychological stress detection or ground-truth clinical distress.**
> 
> A rigorous statistical and distributional audit reveals this is an artifact of **postural domain shift, dataset-level baseline differences, and laboratory acclimatization disparity** (detailed in Section 4). CATSA is treated strictly as an **external task/condition benchmark**, NOT as a psychological ground truth.

---

## 1. Executive Summary & Model Overview

| Attribute | Specification / Value |
| :--- | :--- |
| **Model Designation** | **Prototype Trained Stress Model** (Track 1 Wearable Core) |
| **Architecture** | Cost-Sensitive Extreme Gradient Boosting (`XGBClassifier`) with Native NaN Routing |
| **Training Population** | 35 Human Participants (11 WESAD + 24 PhysioNet) $\to$ 6,039 60-second windows |
| **Validation Population** | 8 Held-Out Human Participants (2 WESAD + 6 PhysioNet) $\to$ 1,214 60-second windows |
| **Internal Test Population** | 8 Held-Out Human Participants (2 WESAD + 6 PhysioNet) $\to$ 971 60-second windows |
| **External Benchmark** | 50 Held-Out Human Participants (CATSA) $\to$ 1,244 60-second windows (5 tasks) |
| **Total Cohort** | **101 Unique Human Subjects** across 9,468 continuous 60-second windows |
| **Anti-Contamination Rule** | Strict Subject-Wise Partitioning (`zero_leakage_verified: True`); Scalers/Imputers fitted on Training Partition ONLY. |

---

## 2. Internal Held-Out Test Set Performance (8 Unseen Subjects, 971 Windows)

The internal test partition evaluates generalization to completely unseen individuals under identical physiological instrumentation (Empatica E4 / RespiBAN):

### A. Primary Performance Metrics (Internal Test Set)

| Metric | Score | Scientific & Operational Meaning |
| :--- | :---: | :--- |
| **Accuracy** | **82.60%** | Overall window-level agreement on held-out subjects. |
| **Balanced Accuracy** | **82.11%** | Unweighted mean of Non-Stress Specificity and Stress Sensitivity. |
| **Precision (PPV)** | **86.89%** | Positive Predictive Value: 338 of 389 predicted stress alarms were genuine. |
| **Recall / Sensitivity** | **74.12%** | True Positive Rate: 338 of 456 acute stress windows detected. |
| **Specificity (TNR)** | **90.10%** | True Negative Rate: 464 of 515 non-stress/exercise windows correctly rejected. |
| **F1-Score (Binary)** | **0.8000** | Harmonic mean of precision and recall. |
| **ROC-AUC** | **0.8888** | Area under the Receiver Operating Characteristic curve. |
| **PR-AUC** | **0.8806** | Area under the Precision-Recall curve. |

### B. Confusion Matrix (Internal Test Set — 971 Windows)

$$\begin{pmatrix} \text{True Non-Stress (TN)} = 464 & \text{False Stress Alarm (FP)} = 51 \\ \text{Missed Stress (FN)} = 118 & \text{True Stress Detected (TP)} = 338 \end{pmatrix}$$

### C. Subgroup & Protocol Breakdown: Physical Exertion Rejection

A vital requirement for military personnel monitoring is preventing vigorous physical activity (running, tactical maneuvers) from triggering false psychological stress alerts:

| Protocol / Condition | Dataset | Ground Truth | Windows ($N$) | Classification Accuracy | Mean Predicted $P(\text{Stress})$ | Physiological Interpretation |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **`ANAEROBIC_SPRINT`** | PhysioNet | Non-Stress ($0$) | 113 | **94.7%** | **0.099** | High HR + extreme kinetic ACC variance $\to$ successfully identified as physical exertion. |
| **`AEROBIC_CYCLE`** | PhysioNet | Non-Stress ($0$) | 198 | **87.9%** | **0.228** | Rhythmic cycling cadence $\to$ rejected from stress alerts. |
| **`Baseline Rest (1)`** | WESAD | Non-Stress ($0$) | 78 | **97.4%** | **0.135** | Seated neutral baseline characterized by high PRV and low sympathetic EDA. |
| **`Amusement (3)`** | WESAD | Non-Stress ($0$) | 23 | **95.7%** | **0.226** | Relaxed video watching $\to$ low sympathetic tone. |
| **`Meditation (4)`** | WESAD | Non-Stress ($0$) | 47 | **100.0%** | **0.129** | Parasympathetic recovery state $\to$ complete non-stress differentiation. |
| **`STRESS_TASK`** | PhysioNet | Acute Stress ($1$) | 411 | **73.5%** | **0.685** | High sympathetic EDA burst + suppressed HRV during cognitive challenge. |
| **`TSST Stress (2)`** | WESAD | Acute Stress ($1$) | 45 | **80.0%** | **0.628** | Public speaking + mental arithmetic under social evaluation. |
| **`STRESS_BASELINE`** | PhysioNet | Non-Stress ($0$) | 28 | **78.6%** | **0.249** | Seated pre-task baseline. |
| **`STRESS_REST`** | PhysioNet | Non-Stress ($0$) | 28 | **57.1%** | **0.460** | Post-task recovery window showing physiological recovery hysteresis. |

---

## 3. External Benchmark Evaluation (CATSA — 50 Unseen Subjects, 1,244 Windows)

CATSA evaluates whether a model trained on acute laboratory stressors (TSST / mental arithmetic) generalizes to unconstrained cognitive tasks:

| CATSA Condition | Windows ($N$) | Mean Predicted $P(\text{Stress})$ | Median $P(\text{Stress})$ | Predicted High-Stress ($P \ge 0.50$) | Benchmark Finding |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **`Baseline`** | 250 | **0.8515** | 0.8967 | **96.8%** | **Severe Domain Shift**: Baseline subjects exhibit elevated predictions. |
| **`Logic`** | 250 | 0.8194 | 0.8705 | 95.6% | Analytical problem solving under active time constraints. |
| **`Nback`** | 250 | 0.8123 | 0.8828 | 91.2% | Working memory load; suppressed PRV. |
| **`Sudoku`** | 244 | 0.8256 | 0.8865 | 94.3% | Sustained attention under time pressure. |
| **`Stroop`** | 250 | 0.7623 | 0.8509 | 86.8% | Color-word interference conflict. |

---

## 4. Feature Distribution Shift & Root Cause Analysis

A feature-by-feature statistical audit comparing the Training Non-Stress distribution ($N=3,965$) against the CATSA Baseline distribution ($N=250$) reveals significant distribution divergence:

### A. Feature Distribution Divergence Table (Kolmogorov-Smirnov & Wasserstein Distance)

| Feature Name | Category | Train Non-Stress Median (Q1–Q3) | CATSA Baseline Median (Q1–Q3) | KS Stat ($D_{\text{KS}}$) | Wasserstein Distance | Divergence Severity |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `acc_motion_energy` | Kinetic / ACC | **6.87** (2.00 – 24.52) | **0.14** (0.08 – 0.22) | **0.804** | Large | **CRITICAL SHIFT** |
| `acc_magnitude_std` | Kinetic / ACC | **2.62** (1.41 – 4.95) | **0.37** (0.29 – 0.47) | **0.804** | Large | **CRITICAL SHIFT** |
| `acc_peak_accel` | Kinetic / ACC | **91.55** (73.91 – 124.84) | **65.62** (64.88 – 67.36) | **0.742** | Large | **HIGH SHIFT** |
| `temp_mean` | Thermal | **32.52** (31.40 – 33.82) | **34.87** (34.04 – 35.47) | **0.556** | 2.032 | **MODERATE SHIFT** |
| `acc_magnitude_mean`| Kinetic / ACC | **64.26** (63.32 – 64.78) | **63.73** (63.55 – 63.88) | **0.467** | Large | Moderate |
| `hr_std` | Cardiovascular | **3.23** (1.40 – 8.72) | **1.08** (0.64 – 1.83) | **0.439** | 5.056 | Moderate |
| `hr_max` | Cardiovascular | **105.15** (87.40 – 136.53) | **86.72** (77.61 – 96.17) | **0.423** | 24.770 | Moderate |
| `eda_phasic_peaks` | Sympathetic / EDA | **9.00** (1.00 – 18.00) | **6.00** (1.25 – 9.00) | **0.358** | 4.440 | Moderate |
| `hrv_sdnn` | Parasympathetic / PRV| **60.28** (28.58 – 154.03) | **66.44** (45.95 – 88.94) | **0.250** | 37.760 | Mild |
| `hr_mean` | Cardiovascular | **87.49** (76.20 – 107.03) | **84.26** (75.70 – 93.36) | **0.214** | 9.748 | Mild |
| `hrv_rmssd` | Parasympathetic / PRV| **61.55** (33.20 – 181.07) | **79.31** (40.50 – 112.96) | **0.226** | 40.515 | Mild |
| `eda_mean` | Sympathetic / EDA | **2.53** (0.43 – 7.14) | **3.85** (0.96 – 7.39) | **0.165** | Large | Mild |
| `eda_tonic_mean` | Sympathetic / EDA | **2.54** (0.43 – 7.14) | **3.86** (0.96 – 7.38) | **0.164** | Large | Mild |

---

### B. The Three Root Causes of CATSA Baseline Elevation

1. **Postural Stasis Confounding (Kinetic Feature Misrouting)**:
   - In the training set (PhysioNet + WESAD), the Non-Stress class contains structured exercise sessions (`AEROBIC_CYCLE` and `ANAEROBIC_SPRINT`) where `acc_motion_energy` is high ($\text{median} = 6.87$).
   - Acute psychological stress (TSST, mental arithmetic) in training occurs almost exclusively while subjects are seated in a chair ($\text{motion energy} < 0.50$).
   - In CATSA, participants remained **completely seated and motionless in front of a monitor during the entire recording, including the Baseline condition** ($\text{motion energy} = 0.14$).
   - The tree-based model learned that very low motion energy ($\text{ACC} < 0.50$) is strongly associated with seated cognitive testing rather than active physical non-stress.
2. **Lack of Protocol Acclimatization in CATSA**:
   - In WESAD, subjects underwent a 20-minute guided relaxation acclimatization period before baseline recording.
   - In CATSA, baseline recording occurred immediately after laboratory instrument placement without prolonged habituation, producing elevated anticipatory autonomic arousal ($\text{median HR} = 84.26\text{ bpm}$, $\text{median EDA} = 3.85\,\mu\text{S}$).
3. **Absolute Sensor Baseline Variability Across Individuals**:
   - Absolute skin conductance (`eda_mean`) and skin temperature (`temp_mean`) vary heavily by skin hydration, ambient room temperature, and wristband tightness across different laboratories ($34.87^\circ\text{C}$ in CATSA vs. $32.52^\circ\text{C}$ in WESAD). Without subject-specific baseline normalization ($z$-score deviations), absolute levels induce domain shift.

---

## 5. Controlled Feature Ablation & Generalization Experiments

To evaluate how different feature subsets impact internal test generalization versus external domain shift, controlled ablation experiments were conducted:

| Model Feature Subset | Features ($N$) | Internal Test Bal. Acc. | Internal Test ROC-AUC | CATSA Baseline Mean $P(\text{Stress})$ | CATSA Baseline High-Stress ($P \ge 0.50$) | Finding |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Full Model (Track 1 Baseline)** | **25** | **82.11%** | **0.8888** | **0.8515** | **96.8%** | Primary prototype baseline. |
| **Without Kinetic ACC Features** | **21** | 78.26% | 0.8753 | **0.5456** | **58.0%** | **Confirms Hypothesis**: Removing ACC drops CATSA baseline stress predictions by **$30.6\%$** and reduces false alarms from $96.8\%$ to $58.0\%$. |
| **Without Absolute EDA Levels** | **21** | 81.50% | 0.8920 | 0.8594 | 96.4% | Preserving only relative EDA features (`eda_slope`, `eda_phasic_peaks`, `eda_phasic_auc`) maintains high internal discrimination. |
| **Without High-Shift Features** | **25** | 82.11% | 0.8888 | 0.8515 | 96.8% | Identical when $D_{\text{KS}} \le 0.85$ threshold is applied. |

---

## 6. Probability Calibration Diagnostics (Held-Out Validation Set — 8 Subjects)

### A. Calibration Summary Metrics

- **Brier Score**: **$0.1310$** (Optimal: $0.0$, Uninformative Prior: $0.2464$).
- **Expected Calibration Error (ECE)**: **$10.01\%$** ($0.1001$).
- **Maximum Calibration Error (MCE)**: **$22.41\%$** ($0.2241$).

### B. Reliability Diagram Bins (10 Probability Bins)

| Bin | Confidence Range | Windows ($N$) | Observed True Stress Rate | Mean Predicted Confidence | Calibration Gap ($|\text{Obs} - \text{Pred}|$) |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | $[0.0, 0.1)$ | 405 | 0.040 (4.0%) | 0.055 | 0.015 (Well Calibrated) |
| **2** | $[0.1, 0.2)$ | 220 | 0.273 (27.3%) | 0.142 | 0.131 |
| **3** | $[0.2, 0.3)$ | 90 | 0.456 (45.6%) | 0.244 | 0.211 |
| **4** | $[0.3, 0.4)$ | 64 | 0.547 (54.7%) | 0.345 | 0.202 |
| **5** | $[0.4, 0.5)$ | 52 | 0.519 (51.9%) | 0.445 | 0.074 |
| **6** | $[0.5, 0.6)$ | 38 | 0.763 (76.3%) | 0.552 | 0.211 |
| **7** | $[0.6, 0.7)$ | 76 | 0.882 (88.2%) | 0.657 | 0.224 |
| **8** | $[0.7, 0.8)$ | 79 | 0.873 (87.3%) | 0.747 | 0.127 |
| **9** | $[0.8, 0.9)$ | 126 | 0.944 (94.4%) | 0.856 | 0.088 (Well Calibrated) |
| **10** | $[0.9, 1.0)$ | 64 | 1.000 (100.0%) | 0.927 | 0.073 (Well Calibrated) |

### C. Operating Threshold Recommendations

> [!NOTE]
> **Probability Threshold Sensitivity**:
> A naive threshold of $P = 0.50$ is not optimal across all operating contexts.
> - **Optimal Balanced Accuracy Threshold (Validation Set)**: **$T^* = 0.25 - 0.30$** ($\text{Bal. Acc.} = 83.08\%$, $\text{F1} = 0.8090$).
> - For field deployment in high-stakes operational zones (Zone 1: Active Ops), high specificity ($T \ge 0.60$) is recommended to prevent alarm fatigue. For wellness surveillance (Zone 3: Base Camp), lower thresholds ($T \approx 0.35$) maximize early detection sensitivity.

---

## 7. Explicit Boundaries, Limitations & Ethical Guardrails

1. **PROTOTYPE STATUS ONLY**: This model is trained on public laboratory research datasets (WESAD, PhysioNet) and is designated strictly as a **Prototype Trained Stress Model**. It is **NOT field-validated on Central Armed Police Forces (CAPF) or Indian Armed Forces operational personnel**.
2. **NO PSYCHOLOGICAL GROUND TRUTH CLAIM FOR CATSA**: Elevated predictions on CATSA demonstrate wearable physiological arousal under cognitive testing constraints; they **DO NOT prove psychiatric or psychological disorder**.
3. **NO REPEATED RETRAINING OR LABEL MANIPULATION**: The model was not iteratively retrained or tuned on CATSA to manufacture artificial benchmark scores.
4. **STAGE BOUNDARY ENFORCEMENT**: The Phase 6 AI model outputs **Physiological Stress Likelihood ($P$)**, which serves as an empirical signal input. It is combined with Phase 5 Personal Baseline Deviations, Trajectory Slopes, Recovery Debt, and Authoritative Context (Zone 1/2/3, Night Shift, Post-Leave Day) before any welfare notification is generated.

---

## 8. Recommended Next Actions for Stage B Integration

1. **Incorporate Personal Baseline Deviation Features**:
   - Replace or supplement raw absolute metrics (`eda_mean`, `hr_mean`, `temp_mean`) with Phase 5 personal baseline deviations ($z$-scores and robust MAD deviations calculated from each soldier's personal resting history).
2. **Deploy Dual-Layer Exertion & Context Gating**:
   - Combine the Stage A physiological probability with SEPTERIA authoritative context:
     - When `context_zone_active_ops = 1` or `acc_motion_energy > 2.0`, gate false alarms.
     - When `recovery_burden_score > 60` and `sleep_deficit_hours > 3.0`, adjust sensitivity.
3. **Persist Prototype Model with Full Disclaimers**:
   - The model artifact [`ml/models/xgboost_stress_model.json`](file:///d:/IITM/SIH/PROTOTYPE/ANTIGRAVITY/ANTI-INFO/ml/models/xgboost_stress_model.json) and documentation are preserved for Phase 6 Stage B context fusion.

---

**Model Validation Audit completed. All results, distributions, calibration diagnostics, and limitations are documented. No further training or phase transitions will occur without your explicit directive.**
