# AI Training Target & Feature Schema Specification

**Project**: SEPTERIA — AI-Based Predictive Personnel Stress and Welfare Monitoring System  
**SIH Problem Statement**: SIH26186  
**Document Version**: 2.1.0  
**Status**: APPROVED & RECONCILED (Step 2 & Step 3 Specification)

---

## 1. Problem Framing & AI Training Target

### A. Target Definition
The initial machine learning model (Phase 6 Stage A) is formulated strictly as a **Binary Physiological Stress Classifier**:
$$\hat{y} \in \{0, 1\}$$

- **Class 0 (`NON_STRESS`)**:
  - **Scientific Meaning**: The source protocol state is not the target acute-stress condition (baseline rest, neutral resting state, amusement/relaxation, meditation, or physical exercise/exertion).
  - **Important Clarification**: Label `0` does **NOT** imply the complete absence of all psychological distress or total mental well-being; it signifies that physiological measurements in this window are consistent with non-stress or exertion protocols rather than acute stress induction.
- **Class 1 (`ACUTE_STRESS`)**:
  - **Scientific Meaning**: Acute cognitive, social-evaluative, or psychological stress state (e.g. Trier Social Stress Test, Montreal Imaging Stress Task, Stroop color-word conflict under time pressure, mental arithmetic challenges).

### B. Two-Stage Experiment Plan
1. **Stage A (Physiological-Only Baseline)**:
   - Evaluated on wearable physiological and kinetic features extracted from public benchmark datasets (Group A 25 features).
   - **Zero Synthetic Imputation**: Real-world operational context fields are **NOT** fabricated or filled with artificial values for public datasets.
2. **Stage B (SEPTERIA Multimodal + Operational Context Layer)**:
   - Combines Stage A physiological stress probabilities with SEPTERIA operational context (Zone 1/2/3, Night Shift, Post-Leave Day, Recovery Debt, Trajectory Slope, Personal Baseline Deviations).

---

## 2. Dataset Label Harmonization Matrix

| Dataset | Protocol / Condition | Source Label | Target $y$ | Scientific & Physiological Rationale |
| :--- | :--- | :---: | :---: | :--- |
| **WESAD** | Baseline | `1` | `0` | Seated neutral resting condition (20 mins). |
| **WESAD** | Stress (TSST) | `2` | `1` | Trier Social Stress Test (public speaking + mental arithmetic). |
| **WESAD** | Amusement | `3` | `0` | Video watching in relaxed state. |
| **WESAD** | Meditation | `4` | `0` | Guided post-stress relaxation. |
| **WESAD** | Transient / Unlabeled | `0, 5, 6, 7` | **DROP** | Transition/debriefing segments. Replaced by strict purity filter. |
| **PhysioNet** | Baseline Rest (STRESS) | First 120s | `0` | Seated pre-stress resting baseline. |
| **PhysioNet** | Stress Tasks (STRESS) | Mid-session | `1` | Cognitive stress battery (Stroop, arithmetic). |
| **PhysioNet** | Post-Stress Rest | Final 120s | `0` | Seated recovery period. |
| **PhysioNet** | Aerobic Exercise | Entire session | `0` | Ergometer cycling. Physiological elevation consistent with exertion. |
| **PhysioNet** | Anaerobic Exercise | Entire session | `0` | High-intensity sprint intervals. Physical exertion. |
| **CATSA** | Baseline Rest | `Baseline` | *Benchmark* | Seated baseline rest across 50 subjects. |
| **CATSA** | Cognitive Tasks | `Logic, Nback, Stroop, Sudoku` | *Benchmark* | External task/condition generalization benchmark. |

---

## 3. Windowing & Signal Processing Parameters

1. **Window Duration**: $60\text{ seconds}$
2. **Step Size**: $30\text{ seconds}$ ($50\%$ overlap)
3. **Purity Threshold**: Windows must have $\ge 70\%$ label purity.
4. **Zero Synthetic Imputation Policy**:
   - If a sensor signal is missing, disconnected ($<0.005\,\mu\text{S}$ for EDA, $<20^\circ\text{C}$ for Temp), or corrupted by motion ($<15$ beats in 60s), the metric is **strictly encoded as `NaN`**.
   - Under no circumstances are missing modalities or sensor dropouts filled with constant defaults (e.g. 0.0, 75.0 bpm, or 15.0 breaths/min).

---

## 4. Heart Rate Variability (HRV) & Pulse Rate Variability (PRV) Derivation Protocol

| Dataset | Modality | Raw Sensor Stream | Heart Rate (HR) Source | Autonomic Variability (HRV/PRV) Source | Derivation Method & Quality Requirements |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **PhysioNet** | Wrist | `HR.csv`, `IBI.csv` | 1 Hz `HR.csv` | Empirical `IBI.csv` | E4 onboard beat timestamps. Requires $\ge 15$ beats in 60s; otherwise `NaN`. |
| **WESAD Wrist** | Wrist | `BVP` (64 Hz) | 64 Hz BVP Pulse Rate | 64 Hz BVP PRV | 2nd-order Butterworth bandpass ($0.5-3.5\text{ Hz}$), systolic peak detection ($\ge 0.3\times\text{std}$ prominence), physiological gating ($300-2000\text{ ms}$). Requires $\ge 15$ beats in 60s; otherwise `NaN`. |
| **CATSA** | Wrist | `HR.csv`, `BVP.csv` | 1 Hz `HR.csv` | 64 Hz BVP PRV | HR stats from 1 Hz `HR.csv`. PRV stats from 64 Hz `BVP.csv` ($\ge 15$ beats in 60s; otherwise `NaN`). **1 Hz HR is NEVER differenced for HRV**. |
| **WESAD Chest** | Chest | `ECG` (700 Hz) | 700 Hz ECG | 700 Hz ECG HRV | Pan-Tompkins QRS detection on 700 Hz Lead-II ECG yields true RR intervals ($\ge 15$ beats in 60s). |

---

## 5. Subject Allocation Matrix (101 Unique Human Participants)

```
Total Human Subjects Across Datasets: 101 Unique Biological Participants

├── Training Set (35 Subjects ~ 70% of Public Data):
│   ├── WESAD: 11 Subjects (S2, S3, S4, S5, S6, S7, S8, S9, S10, S11, S13)
│   └── PhysioNet: 24 Subjects (12 Males S01-S12 + 12 Females f01-f12, with S11_a/S11_b in S11)
│
├── Validation Set (8 Subjects ~ 15% - For Hyperparameter Tuning & Early Stopping):
│   ├── WESAD: 2 Subjects (S14, S15)
│   └── PhysioNet: 6 Subjects (3 Males S13-S15 + 3 Females f13, f15, f16)
│
├── Internal Test Set (8 Subjects ~ 15% - Held-Out for In-Domain Evaluation):
│   ├── WESAD: 2 Subjects (S16, S17)
│   └── PhysioNet: 6 Subjects (3 Males S16-S18 + 3 Females f14, f17, f18, with f14_a/f14_b in f14, and S16_a/S16_b in S16)
│
└── External Task/Condition Generalization Benchmark (50 Subjects ~ 100% Held-Out):
    └── CATSA: 50 Independent Subjects (Sub1 - Sub50 across Baseline, Logic, Nback, Stroop, Sudoku)
```

---

## 6. Data Leakage Prevention Checklist

| Leakage Risk | Mechanism | Prevention Protocol | Status |
| :--- | :--- | :--- | :---: |
| **Subject Contamination** | Overlapping subject physiology across train, val, test | Strict subject-ID partitioning; base biological ID matching. | **VERIFIED (Zero Overlap)** |
| **Window Boundary Overlap** | Sliding window overlap crossing train/test split | Windows are generated strictly within each subject. | **VERIFIED (Zero Leakage)** |
| **Feature Extraction Independence** | Statistics computed using global dataset values | Every feature is computed independently within each subject's 60s window. | **VERIFIED (Zero Leakage)** |
| **Modality Contamination** | Imputing missing chest features with zero or constants | Chest-only features removed from wrist partitions; explicit modality flags. | **VERIFIED (Zero Fabrication)** |
| **HRV Fabrication** | Deriving pseudo-HRV from 1 Hz HR | Removed. PRV from 64 Hz BVP / true IBI / ECG RR only. | **VERIFIED (Defensible Source)** |
| **Global Scaling Leakage** | Feature scalers fit on full dataset | Scalers fit strictly on training fold during Phase 6 model training. | **ENFORCED** |
