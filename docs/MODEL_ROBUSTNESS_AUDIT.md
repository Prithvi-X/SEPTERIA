# SEPTERIA Controlled Model Robustness & Tri-Layer Architecture Audit

**Project**: SEPTERIA — AI-Based Predictive Personnel Stress and Welfare Monitoring System for Uniformed Forces  
**SIH Problem Statement**: SIH26186  
**Document**: `docs/MODEL_ROBUSTNESS_AUDIT.md`  
**Model Designation**: **Prototype Stress Model - Robustness Candidate (v1.0.0-CANDIDATE)**  
**Status**: AUDITED — PROTOTYPE CANDIDATE ONLY (NOT CAPF FIELD-VALIDATED; NOT INTEGRATED INTO LIVE APPLICATION)

---

> [!IMPORTANT]
> ### Methodological Safeguards & Anti-Contamination Mandate
> 1. **Research Candidate Status Only**: Model C is maintained as a **Prototype Stress Model - Robustness Candidate**. It has **NOT** replaced the live application models and is **NOT** deployed into production.
> 2. **Zero CATSA Tuning**: CATSA (50 independent subjects, 1,244 windows) was evaluated strictly as an untouched external benchmark. The model was **NOT** tuned, retrained, or altered to artificially reduce the baseline $96.8\%$ prediction figure.
> 3. **Preservation of Kinetic Accelerometry (ACC)**: Accelerometry features were preserved to ensure high-intensity physical exercise (running, patrols, drills) is rejected from triggering false psychological stress alarms.
> 4. **No Synthetic Context Claims**: In public laboratory datasets (WESAD, PhysioNet, CATSA), operational context (combat zones, night shifts, post-leave day, sleep deficit) is absent and was set to neutral reference defaults ($0.0$). Model C's context features are evaluated as structural architecture inputs, not as empirically trained combat weights.

---

## 1. Controlled Robustness Experiment Setup (Models A, B, C)

To investigate personal baseline normalization, absolute sensor drift, and operational context fusion, three distinct model variants were trained and benchmarked under identical hyperparameters and strict subject-wise isolation:

1. **Model A (Physiological-Only Baseline — 25 Features)**:
   - Core wearable features across Cardiovascular (HR stats, slope), Autonomic PRV (rMSSD, SDNN, pNN50, CV), Sympathetic EDA (tonic SCL, phasic SCR bursts, AUC), Thermal (Temp mean, std, slope), and Kinetic ACC (mean, std, motion energy, peak).
2. **Model B (Physiological + Personal-Baseline Deviations — 32 Features)**:
   - Model A features supplemented with **7 Subject-Normalized Deviation Features** derived strictly from each subject's personal resting baseline:
     - `dev_hr_abs`, `dev_hr_robust_z`
     - `dev_hrv_rmssd_abs`, `dev_hrv_rmssd_robust_z`
     - `dev_eda_tonic_ratio` (relative fold change $\frac{\text{observed}}{\text{baseline}}$), `dev_eda_tonic_diff`
     - `dev_temp_diff` (temperature drift relative to personal baseline)
3. **Model C (Physiological + Personal Baseline + Operational Context — 38 Features)**:
   - Model B features combined with **6 SEPTERIA Operational Context Features**:
     - `context_zone_active_ops`, `context_is_night_shift`, `context_post_leave_day`
     - `recovery_burden_score` (cumulative strain proxy), `sleep_deficit_hours`, `trajectory_direction_hrv`

---

## 2. Comprehensive Model Comparison Matrix (Models A, B, C)

| Evaluation Stage | Evaluation Metric | Model A (Physio-Only) | Model B (+ Personal Baseline) | Model C (Robustness Candidate) | Robustness & Generalization Interpretation |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Feature Configuration** | **Total Features Count** | **25 Features** | **32 Features** | **38 Features** | Progressive context and baseline integration. |
| **Internal Validation**<br>*(8 Subjects, 1,214 Windows)* | **Accuracy** | 82.37% | **83.11%** | **83.11%** | Baseline normalization stabilizes validation predictions. |
| | **Balanced Accuracy** | 80.47% | 81.52% | **81.66%** | $+1.19\%$ improvement over Model A. |
| | **F1-Score (Binary)** | 0.7648 | 0.7812 | **0.7840** | Highest harmonic balance. |
| | **ROC-AUC** | 0.9136 | **0.9406** | 0.9376 | Personal deviations increase ROC-AUC by $+0.027$. |
| | **Brier Calibration Loss**| 0.1310 | 0.1245 | **0.1218** | Lower probability loss. |
| | **Expected Calibration Error (ECE)** | 10.01% | 9.05% | **8.73%** | Lowest calibration gap ($8.73\%$) on Model C. |
| **Internal Test Set**<br>*(8 Unseen Subjects, 971 Windows)* | **Accuracy** | **82.60%** | 81.26% | 81.87% | High test discrimination on unseen subjects. |
| | **Balanced Accuracy** | **82.11%** | 80.65% | 81.27% | Balanced across non-stress and acute stress. |
| | **Precision (PPV)** | 86.89% | **87.23%** | 87.05% | High confidence in predicted stress alerts. |
| | **Recall / Sensitivity** | **74.12%** | 70.61% | 71.27% | Captures $>71\%$ of acute stress windows. |
| | **Specificity (TNR)** | 90.10% | 90.68% | **91.26%** | High non-stress rejection ($>91\%$). |
| | **F1-Score (Binary)** | **0.8000** | 0.7797 | 0.7869 | Robust F1 across all variants. |
| | **ROC-AUC** | 0.8888 | 0.9144 | **0.9252** | Model C achieves highest test ROC-AUC ($0.9252$). |
| | **PR-AUC** | 0.8806 | 0.8912 | **0.9045** | Precision-Recall curve area exceeds $0.90$. |
| **External Benchmark (CATSA)**<br>*(50 Unseen Subjects, 1,244 Windows)* | **Baseline Task ($N=250$) Mean $P$** | 0.8515 | 0.8260 | **0.8163** | Personal baseline deviations reduce baseline shift. |
| | **Baseline Windows $P \ge 0.50$** | 96.8% | 98.0% | 96.8% | Demonstrates persistent postural domain shift. |
| | **Logic Task ($N=250$) Mean $P$** | 0.8194 | **0.8342** | 0.8331 | High cognitive load detection. |
| | **Nback Task ($N=250$) Mean $P$** | 0.8123 | 0.8210 | **0.8245** | Working memory load activation. |
| | **Stroop Task ($N=250$) Mean $P$** | 0.7623 | 0.7884 | **0.7904** | Conflict challenge differentiation. |
| | **Sudoku Task ($N=244$) Mean $P$** | 0.8256 | 0.8384 | **0.8408** | Analytical problem solving under time pressure. |
| **Top 3 Predictive Features** | **By Information Gain** | `hrv_sdnn` (85.4)<br>`acc_mag_std` (57.3)<br>`acc_motion` (53.2) | `hrv_sdnn` (106.7)<br>`acc_motion` (75.6)<br>`acc_mag_std` (73.9) | `hrv_sdnn` (91.7)<br>`acc_mag_std` (78.6)<br>`acc_motion` (68.4) | Autonomic variability + Kinetic energy dominate. |

---

## 3. Contextual Feature Reality Check at Inference Time

> [!WARNING]
> ### Critical Audit Finding: Training Data vs. Inference-Time Context Availability
> In public research datasets (WESAD, PhysioNet, CATSA), operational variables (`context_zone_active_ops`, `context_is_night_shift`, `context_post_leave_day`, `sleep_deficit_hours`) **do not exist in the raw data**.
> 
> During training, these features were set to **neutral reference defaults ($0.0$)**.
> 
> **Scientific Implication**:
> - Model C's decision trees did **NOT** learn genuine empirical interactions with combat zones or sleep deprivation from the public datasets.
> - Therefore, Model C must **NOT** be described as a "fully contextualized end-to-end AI".
> - Operational context must be applied as an **explicit hierarchical gating layer** (Layer 2 & Layer 3) rather than conflating static lab constants with machine-learned tactical context.

---

## 4. SEPTERIA Tri-Layer Architecture Separation

To maintain strict scientific validity and prevent algorithmic overreach, SEPTERIA enforces a clear three-layer separation:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ LAYER 1: PHYSIOLOGICAL STRESS LIKELIHOOD MODEL (Phase 6 ML Core)            │
│ Inputs: 25 Wearable Features (HR, PRV, EDA, TEMP, ACC)                      │
│ Output: P(Physiological Stress) ∈ [0.0, 1.0]                                │
│ Source: Trained strictly on empirical wearable physiology (WESAD/PhysioNet) │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ LAYER 2: PERSONAL BASELINE & CONTEXT INTERPRETATION (Phase 5 Logic Engine)  │
│ Inputs: Layer 1 P(Stress), Personal Baseline z-scores (HR/HRV/EDA/TEMP),     │
│         Recovery Debt Score, Trajectory Slopes, Authoritative Metadata:     │
│         - Zone 1: Active Operations / Combat (Exertion override)            │
│         - Zone 2: Transit / Training / Routine Duty                         │
│         - Zone 3: Critical Incident / Post-Incident Recovery                │
│         - Shift Timing: Night Shift (20:00 - 04:00)                         │
│         - Leave Transition: Post-Leave Re-entry Period (Days 0 - 14)        │
│ Output: Calibrated Contextual Risk Assessment & Confidence Index            │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ LAYER 3: FINAL WELFARE RISK DECISION & INTERVENTION GATE                    │
│ Inputs: Layer 2 Risk Assessment, Operational Duty Constraints, Cooldown Timers│
│ Output: Welfare Alert Level (Green / Yellow / Amber / Red)                  │
│ Action: Secure Alert Routing to Unit Medical Officer / Psychologist         │
│ Guardrail: Non-punitive, human-in-the-loop decision support ONLY            │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Operational Zone Semantics & Threshold Guidelines

The operational zones are defined strictly in accordance with military and paramilitary doctrine:

1. **Zone 1 — Active Operations / Combat**:
   - **Operational Environment**: Active counter-insurgency, high-altitude border patrol, dynamic tactical maneuvers.
   - **Gating Policy**: High kinetic motion energy (`acc_motion_energy > 2.0`) and high zone stress thresholds ($T \ge 0.60$) are enforced to prevent physical exertion (running, climbing) from triggering false alarms and causing tactical distraction.
2. **Zone 2 — Transit / Training / Routine Duty**:
   - **Operational Environment**: Base camp duties, convoy transit, scheduled physical training, administrative tasks.
   - **Gating Policy**: Standard baseline threshold ($T \approx 0.50$) with personal baseline deviation verification.
3. **Zone 3 — Critical Incident / Post-Incident Recovery**:
   - **Operational Environment**: Immediate post-ambush debriefing, casualty evacuation recovery, high-trauma post-incident quarantine.
   - **Gating Policy**: **No fixed arbitrary threshold is assigned**. Sensitivity is dynamically adjusted based on the soldier's cumulative recovery debt and sleep deficit score, prioritizing early psychological support and medical review.

---

## 6. External CATSA Benchmark Dynamics & Domain Shift

### Summary of CATSA Baseline Arousal ($N=250$ windows, 50 subjects):
- Mean predicted probability: **$0.8163$** (Model C) / **$0.8515$** (Model A).
- Windows exceeding $0.50$: **$96.8\%$**.

### Why Direct Optimization on CATSA Is Prohibited:
1. **Postural Stasis Confounding**: CATSA subjects remained seated and motionless throughout the experiment ($\text{ACC motion energy} = 0.14$), mimicking the low-motion seated posture of laboratory mental stress tests rather than active non-stress physical exercise.
2. **No Acclimatization Period**: CATSA baseline was recorded immediately after sensor attachment, producing high anticipatory resting heart rate ($84.26\text{ bpm}$) and skin conductance ($3.86\,\mu\text{S}$).
3. **External Benchmark Integrity**: Modifying feature weights or thresholding rules specifically to suppress the CATSA baseline figure would constitute **unprincipled benchmark overfitting**. CATSA is preserved as an untouched external benchmark.

---

## 7. Explicit Limitations & Safeguards

1. **PROTOTYPE CANDIDATE STATUS**: Model C is maintained strictly as a **Prototype Stress Model - Robustness Candidate**. It is **NOT field-validated on Central Armed Police Forces (CAPF) or Indian Armed Forces operational personnel**.
2. **NO PRODUCTION REPLACEMENT**: The existing application models have **NOT** been replaced. Model C remains an offline research artifact.
3. **NO CLINICAL PSYCHOLOGICAL CLAIMS**: Predicted probabilities represent wearable physiological activation under laboratory tasks; they **DO NOT diagnose clinical depression, anxiety, PTSD, or psychiatric illness**.
4. **DECISION SUPPORT ONLY**: SEPTERIA outputs are intended exclusively for non-punitive welfare monitoring, unit medical officer decision support, and preventive recovery intervention.

---

## 8. Persisted Artifacts Manifest

1. **Controlled Robustness Audit Report**:  
   [`docs/MODEL_ROBUSTNESS_AUDIT.md`](file:///d:/IITM/SIH/PROTOTYPE/ANTIGRAVITY/ANTI-INFO/docs/MODEL_ROBUSTNESS_AUDIT.md)
2. **Robustness Experiments Summary Manifest**:  
   [`ml/results/robustness_experiments_summary.json`](file:///d:/IITM/SIH/PROTOTYPE/ANTIGRAVITY/ANTI-INFO/ml/results/robustness_experiments_summary.json)
3. **Model Validation Audit**:  
   [`docs/MODEL_VALIDATION_AUDIT.md`](file:///d:/IITM/SIH/PROTOTYPE/ANTIGRAVITY/ANTI-INFO/docs/MODEL_VALIDATION_AUDIT.md)
4. **Robustness Execution Script**:  
   [`ml/src/models/run_robustness_experiments.py`](file:///d:/IITM/SIH/PROTOTYPE/ANTIGRAVITY/ANTI-INFO/ml/src/models/run_robustness_experiments.py)
5. **Automated Unit Test Suite**:  
   `pytest ml/tests/` $\to$ **11/11 tests passed (100%)**.

---

**The controlled robustness audit and tri-layer architecture documentation are complete. I have stopped here in accordance with your instructions and am awaiting your review.**
