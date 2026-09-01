# SEPTERIA: Public Physiological & Stress Dataset Audit & Exploration

**Project**: SEPTERIA  
**SIH Problem Statement**: SIH26186 — AI-Based Predictive Personnel Stress and Welfare Monitoring System for Uniformed Forces  
**Phase**: Pre-Phase 6 Dataset Audit & Exploration  
**Objective**: Rigorous empirical inspection, signal verification, missing-data audit, and role assignment for four downloaded public datasets without training, merging, or modifying files.

---

## 1. Executive Summary & Inventory Overview

The project repository's `Dataset/` directory contains four public datasets and one auxiliary file:

| Dataset / File | Local Folder Path | Format | Participants / Subjects | Signals Available | Labels / Target Semantics | Recommended Role |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **1. WESAD** | `Dataset/archive/WESAD/` | `.pkl`, `.csv`, `.txt` | **15** (`S2`–`S17`) | Chest: ECG, EMG, EDA, Temp, Resp, ACC (700Hz)<br>Wrist: BVP (64Hz), ACC (32Hz), EDA (4Hz), TEMP (4Hz) | Discrete 7-class laboratory ground truth (0: Transient, 1: Baseline, 2: TSST Stress, 3: Amusement, 4: Meditation) | **Primary Training Dataset** |
| **2. PhysioNet Stress + Exercise** (v1.0.1) | `Dataset/wearable-device-dataset-.../Wearable_Dataset/` | `.csv`, `.ipynb`, `.txt` | **36** (`S01`–`S18`, `f01`–`f18`) | Wrist (Empatica E4): BVP (64Hz), ACC (32Hz), EDA (4Hz), TEMP (4Hz), HR (1Hz), IBI (Event) | Protocol phase markers (`tags.csv`), self-reported stress (0–10 Likert scale), structured aerobic cycle & anaerobic sprints | **Secondary Training Dataset (Exertion vs. Stress Discrimination)** |
| **3. CATSA** | `Dataset/CATSA/CATSA/` | `.csv` | **50** (`Sub1`–`Sub50`) | Wrist (Empatica E4): BVP (64Hz), ACC (32Hz), EDA (4Hz), TEMP (4Hz), HR (1Hz) | Task/condition labels that can support external stress-related evaluation (5 tasks: `Baseline`, `Logic`, `Nback`, `Stroop`, `Sudoku` in 180s epochs) | **External Validation & Generalization Dataset** |
| **4. TILES-2018** | `Dataset/tiles-dataset-release-master/` | `.py`, `.r`, `.sh`, `.csv` | 212 in paper | *Code repository only* (Fitbit, OMSignal, OwlinOne pipelines) | Daily surveys, STAI, IGTB psychological battery | **Do NOT Use as Training Data** (Reference for longitudinal pipeline architecture only) |
| **5. UN Peacekeeping Stats** | `Dataset/datacommons-uchistorical.csv` | `.csv` | N/A | *Macro-level troop counts (2010–2020)* | UN contributing country troop statistics | **Do NOT Use** (Unrelated macro-statistical file) |

---

## 2. Dataset Deep Dives

### Dataset 1: WESAD (Wearable Stress and Affect Detection)

- **Source / Citation**: Schmidt et al., ACM International Joint Conference on Pervasive and Ubiquitous Computing (UbiComp 2018).
- **Location**: `Dataset/archive/WESAD/` (archive size: ~2.6 GB uncompressed).
- **Subjects**: **15 subjects** (`S2`, `S3`, `S4`, `S5`, `S6`, `S7`, `S8`, `S9`, `S10`, `S11`, `S13`, `S14`, `S15`, `S16`, `S17`).
  - *Note*: `S1` was a pilot run; `S12` was excluded due to RespiBAN sensor malfunction.
- **Hardware & Signals**:
  1. **Chest Unit (RespiBAN Professional @ 700 Hz)**:
     - `ACC`: 3-axis accelerometer ($\pm 2g$)
     - `ECG`: Lead-II electrocardiography ($\text{mV}$)
     - `EMG`: Trapezius muscle electromyography ($\text{mV}$)
     - `EDA`: Electrodermal activity ($\mu\text{S}$)
     - `Temp`: Skin temperature ($^\circ\text{C}$)
     - `Resp`: Respiration expansion gauge ($\%$)
  2. **Wristband (Empatica E4)**:
     - `BVP`: 64 Hz photoplethysmography
     - `ACC`: 32 Hz 3-axis acceleration (unit: $1/64g$)
     - `EDA`: 4 Hz electrodermal activity ($\mu\text{S}$)
     - `TEMP`: 4 Hz skin surface temperature ($^\circ\text{C}$)
- **Ground Truth Labels**:
  - Sampled at 700 Hz synchronized to chest sensor:
    - `0`: Not defined / Transient phase ($\sim 40\%$ of time)
    - `1`: Baseline / Neutral reading ($\sim 20$ minutes per subject)
    - `2`: Stress (Trier Social Stress Test — public speaking + mental arithmetic, $\sim 11 - 12$ minutes)
    - `3`: Amusement (Funny video clips, $\sim 6$ minutes)
    - `4`: Meditation / De-escalation ($\sim 13$ minutes)
    - `5`, `6`, `7`: Ignored / undefined
- **Self-Report Questionnaires**:
  - `S{id}_quest.csv`: Pre/post PANAS (Positive/Negative Affect), STAI (State Anxiety), and SAM (Valence/Arousal).
- **Missing Data & Quality**:
  - Zero NaN values in `.pkl` arrays for the 15 subjects.
  - High signal-to-noise ratio in controlled laboratory conditions.
- **Files Needed for ML**:
  - `archive/WESAD/S{id}/S{id}.pkl` (contains all synchronized signals and ground truth label arrays).
- **Files Ignored**:
  - `archive/WESAD/S{id}/S{id}_respiban.txt` (redundant ASCII raw dump of chest data, already in pickle).
  - `archive/WESAD/S{id}/S{id}_E4_Data/` (redundant unsynchronized raw E4 CSVs, already synchronized in pickle).
- **License**: Academic Research Use.

---

### Dataset 2: PhysioNet Wearable Stress & Structured Exercise Sessions (v1.0.1)

- **Source / Citation**: Garcia-Ceja et al., PhysioNet (2020) / *Sensors* Journal.
- **Location**: `Dataset/wearable-device-dataset-.../Wearable_Dataset/`
- **Subjects**: **36 distinct participants**:
  - 18 males in Stage 1 (`S01`–`S18`, Protocol V1)
  - 18 females in Stage 2 (`f01`–`f18`, Protocol V2)
- **Protocols & Subdirectories**:
  1. `STRESS/` (37 session folders): Trier Mental Challenge Task (TMCT), Stroop test, Real Opinion defense, Opposite Opinion debate, Subtraction arithmetic.
  2. `AEROBIC/` (31 session folders): Cycle ergometer aerobic exercise with structured RPM/resistance steps ($60 \to 110\text{ RPM}$).
  3. `ANAEROBIC/` (32 session folders): High-intensity sprint intervals.
- **Hardware & Signals (Empatica E4 Wristband)**:
  - `BVP.csv`: 64 Hz PPG
  - `ACC.csv`: 32 Hz 3-axis acceleration ($1/64g$)
  - `EDA.csv`: 4 Hz electrodermal activity ($\mu\text{S}$)
  - `TEMP.csv`: 4 Hz skin surface temperature ($^\circ\text{C}$)
  - `HR.csv`: 1 Hz heart rate (bpm)
  - `IBI.csv`: Event-based inter-beat intervals (seconds)
  - `tags.csv`: UTC timestamps of event/protocol button presses
- **Target Variables / Labels**:
  - Protocol phase tags (`tags.csv`).
  - `Stress_Level_v1.csv` & `Stress_Level_v2.csv`: Participant self-reported stress ratings on a $0 - 10$ scale across each protocol segment.
- **Missing Data & Constraints (documented in `data_constraints.txt`)**:
  - `S02`: Duplicate download rows in E4 files.
  - `f07`: Protection dock covered PPG/TEMP sensors (only EDA/ACC are valid).
  - `f14`, `S11`, `S16`: Bluetooth drops caused split sessions (`_a` and `_b`).
  - `S01`: IBI file is empty in anaerobic protocol.
  - `S03`, `S07`: Stopped aerobic protocol early.
  - `S12`: Skipped aerobic protocol.
- **Files Needed for ML**:
  - `Wearable_Dataset/STRESS/{id}/*.csv`
  - `Wearable_Dataset/AEROBIC/{id}/*.csv`
  - `Wearable_Dataset/ANAEROBIC/{id}/*.csv`
  - `Stress_Level_v1.csv`, `Stress_Level_v2.csv`, `subject-info.csv`
- **Files Ignored**:
  - `Wearable_Dataset.ipynb` (visualization notebook), `SHA256SUMS.txt`.
- **License**: Open Data Commons Attribution License (ODC-By v1.0).

---

### Dataset 3: CATSA (Cognitive and Affective Time-Series Analysis)

- **Location**: `Dataset/CATSA/CATSA/`
- **Subjects**: **50 distinct subjects** (`Sub1` through `Sub50`).
- **Hardware**: Empatica E4 Wristband.
- **Tasks per Subject** (5 structured conditions $\times 180$ seconds each = 15 minutes/subject):
  1. `Baseline/`: Neutral resting baseline ($180\text{s}$)
  2. `Logic/`: Logical puzzle solving ($180\text{s}$)
  3. `Nback/`: Working memory load ($180\text{s}$)
  4. `Stroop/`: Attention conflict / color-word interference ($180\text{s}$)
  5. `Sudoku/`: Mental arithmetic / grid calculation ($180\text{s}$)
- **Signals & Dimensions (per 180s task)**:
  - `ACC.csv`: 5,760 samples (3-axis @ 32 Hz)
  - `BVP.csv`: 11,520 samples (1-axis @ 64 Hz)
  - `EDA.csv`: 720 samples (1-axis @ 4 Hz)
  - `TEMP.csv`: 720 samples (1-axis @ 4 Hz)
  - `HR.csv`: 180 samples (1-axis @ 1 Hz)
- **Target Variables / Labels**:
  - **Task/condition labels that can support external stress-related evaluation**:
    - 5 conditions: `Baseline` (0 / Neutral), `Logic` (Cognitive Stress), `Nback` (Working Memory Load), `Stroop` (Attention Conflict / Stress), `Sudoku` (Mental Arithmetic / Stress).
  - Total task sessions: $50 \text{ subjects} \times 5 \text{ tasks} = 250 \text{ sessions}$.
- **Files Needed for ML**:
  - `CATSA/Sub{id}/{Task}/*.csv`
- **Files Ignored**:
  - `README.pdf`
- **License**: Academic / Open Research.

---

### Dataset 4: TILES-2018 (`tiles-dataset-release-master`)

- **Location**: `Dataset/tiles-dataset-release-master/`
- **Nature of Files**: **Software pipeline repository only** (Python, R, Shell scripts, schemas, and summary plotting tables).
- **Finding**: The actual multi-week sensor stream database for 212 hospital workers is hosted externally under a Data Use Agreement (DUA) at `https://tiles-data.isi.edu`.
- **Recommendation**: **DO NOT USE AS TRAINING DATA**. Useful purely as architectural reference for daily survey scoring and wearable feature extraction algorithms.

---

### Dataset 5: `datacommons-uchistorical.csv`

- **Location**: `Dataset/datacommons-uchistorical.csv`
- **Nature of File**: Macro-level country troop contribution counts to UN peacekeeping missions (2010–2020).
- **Finding**: Completely unrelated to human physiology, wearable sensors, or stress monitoring.
- **Recommendation**: **DO NOT USE / EXCLUDE**.

---

## 3. Dataset Suitability Assessment Matrix

| Dataset | A. Physiological Stress Classification | B. Stress vs. Physical Exertion Discrimination | C. Longitudinal & Cross-Subject Generalization | Overall Recommendation |
| :--- | :---: | :---: | :---: | :--- |
| **WESAD** | **Primary public dataset for initial multimodal stress modelling**<br>Chest + wrist, verified TSST vs neutral/meditation | **MODERATE**<br>Baseline vs amusement vs stress, but lacks heavy physical exercise | **MODERATE**<br>15 subjects in lab | **PRIMARY TRAINING DATASET** |
| **PhysioNet Stress + Exercise** | **EXCELLENT**<br>Cognitive stress tasks + 0–10 self-reports | **OUTSTANDING (Crucial)**<br>Contains matched aerobic cycle + anaerobic sprints | **HIGH**<br>36 male & female subjects across 3 distinct protocols | **SECONDARY TRAINING DATASET (Exertion Discriminator)** |
| **CATSA** | **EXCELLENT**<br>Task/condition labels that can support external stress-related evaluation (4 cognitive tasks vs baseline) | **LOW**<br>Cognitive tasks only | **HIGH**<br>50 independent subjects for cross-dataset out-of-fold generalization testing | **EXTERNAL VALIDATION DATASET** |
| **TILES-2018** | **NOT USABLE LOCALLY** | **NOT USABLE LOCALLY** | **NOT USABLE LOCALLY** | **EXCLUDE (Code Only)** |
| **UN Peacekeeping** | **NOT APPLICABLE** | **NOT APPLICABLE** | **NOT APPLICABLE** | **EXCLUDE (Unrelated)** |

---

## 4. Cross-Dataset Compatibility & Technical Disparities

> [!WARNING]
> **Signal & Label Incompatibilities**:
> Datasets must NOT be naively concatenated because raw signals and labels have significant structural disparities:

1. **Sampling Frequency Mismatches**:
   - WESAD Chest ECG/Resp is $700\text{ Hz}$; Wrist BVP is $64\text{ Hz}$; EDA is $4\text{ Hz}$.
   - PhysioNet & CATSA have no ECG/Resp; they provide PPG BVP ($64\text{ Hz}$), EDA ($4\text{ Hz}$), and derived HR ($1\text{ Hz}$).
   - **Resolution for Phase 6**: Feature extraction must compute windowed summary metrics (e.g. 60s windows for HRV rMSSD, mean HR, EDA tonic/phasic power, ACC motion energy) rather than concatenating raw sample arrays.

2. **Sensor Hardware & Placement Disparities**:
   - WESAD includes both chest RespiBAN (medical grade ECG) and wrist Empatica E4.
   - PhysioNet and CATSA are exclusively wrist Empatica E4.
   - Models trained strictly on chest ECG will fail on wrist PPG due to motion artifacts and pulse transit time differences.

3. **Label Semantic Incompatibilities**:
   - WESAD: Discrete state classification (`1: Baseline`, `2: TSST Stress`, `3: Amusement`, `4: Meditation`).
   - PhysioNet: Continuous self-reported Likert stress scores ($0 - 10$) across task stages, plus binary exercise tags (`AEROBIC`, `ANAEROBIC`).
   - CATSA: Task condition categories (`Baseline`, `Logic`, `Nback`, `Stroop`, `Sudoku`).
   - **Resolution for Phase 6**: Binary or 3-level operational mapping (`Low/Baseline`, `Elevated Stress`, `Physical Exertion`) or training separate task-specific heads.

4. **Accelerometer Units & Calibration**:
   - WESAD Chest ACC is calibrated in Earth gravity units ($g$).
   - Empatica E4 Wrist ACC (WESAD wrist, PhysioNet, CATSA) is recorded in raw integer counts of $1/64g$ with ranges $[-128, +127]$.

---

## 5. Summary Manifest of Usable Files

A machine-readable manifest has been generated at [`ml/data/dataset_manifest.json`](file:///d:/IITM/SIH/PROTOTYPE/ANTIGRAVITY/ANTI-INFO/ml/data/dataset_manifest.json):

```
Dataset Directory
├── archive/WESAD/                      [PRIMARY TRAINING: 15 Subjects]
│   └── S{2..17}/S{id}.pkl              --> Wrist (BVP, EDA, TEMP, ACC) & Chest (ECG, Resp, EDA, ACC)
├── wearable-device-dataset-.../        [SECONDARY / EXERTION: 36 Subjects]
│   ├── Wearable_Dataset/STRESS/        --> Cognitive Stress Telemetry
│   ├── Wearable_Dataset/AEROBIC/       --> Cycle Ergometer Exertion Telemetry
│   ├── Wearable_Dataset/ANAEROBIC/     --> Sprint Interval Exertion Telemetry
│   └── Stress_Level_v{1,2}.csv         --> Self-Report Ground Truth
├── CATSA/CATSA/                        [EXTERNAL VALIDATION: 50 Subjects]
│   └── Sub{1..50}/{Task}/*.csv         --> 5 Conditions (Baseline, Logic, Nback, Stroop, Sudoku)
├── tiles-dataset-release-master/       [EXCLUDED: Code Pipeline Only]
└── datacommons-uchistorical.csv        [EXCLUDED: Unrelated UN Peacekeeping Counts]
```

---

## 6. Next Steps for Phase 6 (Pending Approval)

1. **Standardized Windowing Feature Extractor**:
   - 60-second sliding windows with 30-second overlap.
   - PPG/ECG: HR, HRV (rMSSD, SDNN, pNN50, LF/HF ratio).
   - EDA: Mean skin conductance level (SCL), non-specific skin conductance responses (NS.SCRs), phasic peak amplitude.
   - ACC: Mean vector magnitude, standard deviation, motion intensity.
   - TEMP: Slope, mean temperature.
2. **Exertion vs. Stress Disentanglement**:
   - Train multi-class or conditioned classifier distinguishing `Baseline`, `Cognitive/Social Stress`, and `Physical Exertion`.
3. **Leave-One-Subject-Out (LOSO) & Cross-Dataset Evaluation**:
   - Train on WESAD & PhysioNet $\to$ Zero-shot evaluation on 50 CATSA subjects.
