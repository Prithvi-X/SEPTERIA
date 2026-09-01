# SEPTERIA Voice Intelligence & Multimodal Welfare Specification (Phase 8)

**Project**: SEPTERIA — AI-Based Predictive Personnel Stress and Welfare Monitoring System for Uniformed Forces  
**SIH Problem Statement**: SIH26186  
**Document**: `docs/VOICE_MULTIMODAL_SPEC.md`  
**Technology**: Python / Librosa Signal Processing + Multimodal Evidence Fusion Engine  
**Status**: IMPLEMENTED & VERIFIED — PHASE 8 COMPLETE

---

> [!IMPORTANT]
> ### Privacy & Ethical Mandate
> 1. **User-Initiated & Voluntary**: Voice recording is strictly optional, initiated explicitly by the soldier, preceded by informed consent, and requires active microphone permission with visible recording states.
> 2. **Zero Raw Audio Retention**: Raw audio byte streams are decoded in memory, processed for numerical acoustic features, and immediately discarded. No audio files or raw waveforms are stored on disk or in the database.
> 3. **Non-Diagnostic Acoustic Representation**: Acoustic features are descriptive markers of physiological activation and vocal dynamics; they do NOT constitute medical diagnoses, psychiatric evaluations, or proof of mental illness.
> 4. **Voice Alone Never Escalates**: Acoustic deviation alone **CANNOT** trigger `WELFARE_CHECK` or `MEDICAL_REVIEW` without corroborating multi-day physiological or autonomic trajectory deterioration.

---

## 1. End-to-End Multimodal Intelligence Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       OPTIONAL VOLUNTARY VOICE CHECK-IN                     │
│                                                                             │
│   [ Soldier in Mobile App ] ──► [ Explicit Consent ] ──► [ 20-30s Audio ]   │
│                                                               │             │
│                                                  (In-Memory Signal Process, │
│                                                   Raw Audio Discarded)      │
└───────────────────────────────────────────────────────────────┼─────────────┘
                                                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ACOUSTIC SIGNAL PROCESSING (Python/Librosa)              │
│                                                                             │
│   - Duration & SNR Gate (>= 5s, >= 6 dB SNR proxy, Clipping Check)          │
│   - F0 Mean, F0 Std, F0 IQR (PYIN fundamental frequency)                    │
│   - Pause Dynamics: Pause Ratio, Mean Pause Duration, Syllable Rate Proxy   │
│   - Energy & Dynamics: RMS Energy Mean, RMS Std, Dynamic Range              │
│   - Spectral Shape: Centroid, Bandwidth, Zero-Crossing Rate                 │
│   - Timbre: MFCCs 1-13 Means & Standard Deviations                          │
└───────────────────────────────────────────────────────────────┼─────────────┘
                                                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PERSONAL VOICE BASELINE & DEVIATION                      │
│                                                                             │
│   - Requires >= 3 Historical Baseline Samples (Else: UNAVAILABLE)           │
│   - Computes Personal Median & MAD (Median Absolute Deviation)              │
│   - Robust Acoustic Deviation z-scores:                                     │
│       z_f0 = (F0 - Median_F0) / (1.4826 * MAD_F0)                           │
│       z_pause = (Pause - Median_Pause) / (1.4826 * MAD_Pause)               │
│       z_energy = (RMS - Median_RMS) / (1.4826 * MAD_RMS)                   │
└───────────────────────────────────────────────────────────────┼─────────────┘
                                                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     MULTIMODAL EVIDENCE FUSION SERVICE                      │
│                                                                             │
│   Inputs:                                                                   │
│     - Layer 1: XGBoost Physiological Stress Probability (P_physio)          │
│     - Layer 2: Personal Baseline z_autonomic, Recovery Burden, Sleep Debt   │
│     - Context: Zone (1, 2, 3), Exertion Tag, Threat Level                   │
│     - Layer 5: Autonomic Trajectory (Improving, Stable, Deteriorating)      │
│     - Phase 7: Contextual Graph Shared Patterns (Cluster Headcount)         │
│     - Phase 8: Optional Voluntary Voice Deviation & Quality                 │
│                                                                             │
│   Arbitration:                                                              │
│     - Agreement Index (Convergence across streams)                          │
│     - Contradiction Detection (Conflict penalty on false escalations)       │
│     - Exertion Disambiguation (High Motion discounts Physio attribution)    │
│                                                                             │
│   Output:                                                                   │
│     - Composite Welfare Score [0.0, 1.0]                                    │
│     - Multimodal Confidence [0.0, 1.0]                                      │
│     - Advisory State: STABLE / MONITORING / VOLUNTARY_CHECKIN /             │
│                       WELFARE_CHECK / MEDICAL_REVIEW / INCONCLUSIVE_DATA    │
│     - Non-Punitive Advisory Recommendation String                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Acoustic Feature Extraction Specification

| Feature Name | Signal Processing Extraction Method | Acoustic / Physiological Context |
| :--- | :--- | :--- |
| `f0_mean` | Probabilistic YIN (`librosa.pyin`) pitch tracking over voiced frames | Mean fundamental frequency (laryngeal vocal fold tension). |
| `f0_std` | Standard deviation of voiced fundamental frequency | Pitch modulation and prosodic variance. |
| `f0_iqr` | 75th - 25th percentile range of voiced F0 | Robust pitch dispersion resistant to octave jumps. |
| `pause_ratio` | Voice Activity Detection (VAD) energy thresholding ($1.0 - \text{SpeechRatio}$) | Proportion of hesitation and breathing pauses. |
| `mean_pause_duration_s` | Continuous silent interval duration ($> 150$ ms) | Articulatory latency and breath cycle duration. |
| `speech_rate_proxy_bpm` | Syllable energy burst rate per minute | Speech articulation cadence proxy. |
| `rms_energy_mean` | Root-mean-square frame energy | Vocal projection power and acoustic intensity. |
| `rms_energy_std` | Standard deviation of RMS energy across frames | Vocal dynamic range and intensity modulation. |
| `spectral_centroid_mean` | Center of mass of the magnitude spectrum | Timbre brightness and vocal tract acoustic resonance. |
| `spectral_bandwidth_mean` | Spectral spread around centroid | Acoustic frequency distribution width. |
| `zero_crossing_rate_mean` | Rate of sign-changes along the signal | High-frequency noise and fricative density. |
| `mfcc_1_13` (Mean & Std) | 13 Mel-Frequency Cepstral Coefficients | Vocal tract spectral envelope characteristics. |

---

## 3. Multimodal Evidence Fusion Mathematics

### 3.1 Individual Stream Evidence Normalization
Each active stream maps to a bounded evidence score $e_i \in [0.0, 1.0]$ representing physiological/operational strain:
1. **Physiological Stream**:
   $$e_{\text{physio}} = \begin{cases} P_{\text{physio}} \times 0.40, & \text{if } \text{is\_physical\_exertion} \\ P_{\text{physio}}, & \text{otherwise} \end{cases}$$
2. **Autonomic Baseline Stream**:
   $$e_{\text{baseline}} = \tanh\left(\frac{\max(0, z_{\text{autonomic}})}{2.0}\right)$$
3. **Recovery Trajectory Stream**:
   $$e_{\text{trajectory}} = \begin{cases} 0.85, & \text{Deteriorating} \\ 0.35, & \text{Stable} \\ 0.10, & \text{Improving} \end{cases}$$
4. **Sleep & Recovery Debt Stream**:
   $$e_{\text{lifestyle}} = 0.60 \times \min\left(1.0, \frac{\text{SleepDebt}}{6.0}\right) + 0.40 \times \min\left(1.0, \frac{\text{RecoveryBurden}}{100.0}\right)$$
5. **Contextual Graph Stream**:
   $$e_{\text{graph}} = \begin{cases} 0.75, & \text{if Shared Pattern Detected in Unit} \\ 0.20, & \text{otherwise} \end{cases}$$
6. **Voluntary Voice Stream**:
   $$e_{\text{voice}} = \text{DeviationMagnitude} \quad (\text{if baseline established and quality} \ge 0.35)$$

### 3.2 Dynamic Weight Normalization
$$\sum_{i \in \text{Active}} w_i = 1.0$$
$$\text{Score}_{\text{raw}} = \sum_{i} w_i \cdot e_i$$

### 3.3 Evidence Agreement & Contradiction Penalty
- **Agreement Index**:
  $$A_{\text{evidence}} = \max\left(0.10, 1.0 - 2.0 \cdot \sigma(\{e_i\})\right)$$
- **Contradiction Penalty**:
  $$\text{CompositeScore} = \begin{cases} \text{Score}_{\text{raw}} \times (1.0 - 0.40), & \text{if Contradiction Detected} \\ \text{Score}_{\text{raw}}, & \text{otherwise} \end{cases}$$

### 3.4 Multimodal Confidence
$$C_{\text{multimodal}} = 0.40 \cdot Q_{\text{data}} + 0.30 \cdot A_{\text{evidence}} + 0.15 \cdot \mathbb{I}_{\text{voice}} + 0.15 \cdot (0.5 \text{ if conflict else } 1.0)$$

---

## 4. Advisory Welfare Decision Hierarchy

| Composite Score | Corroborating Wearable Strain? | Operational Context | Advisory Welfare State | Human Review | Recommended Action |
| :---: | :---: | :---: | :---: | :---: | :--- |
| $< 0.20$ | No | Any | `STABLE` | No | *"Continue routine monitoring."* |
| $0.20 - 0.34$ | No | Any | `MONITORING_ONLY` | No | *"Maintain routine passive monitoring."* |
| $0.35 - 0.54$ | Moderate | Any | `VOLUNTARY_CHECKIN` | No | *"Consider voluntary wellness check-in and shift rest opportunity."* |
| $\ge 0.55$ | **Yes** ($\ge 1$ stream) | Zone 1 / 2 | `WELFARE_CHECK` | **Yes** | *"Recommend authorized unit welfare check (Corroborating multi-stream strain)."* |
| $\ge 0.75$ | **Yes** ($\ge 1$ stream) | **Zone 3** | `MEDICAL_REVIEW` | **Yes** | *"Recommend authorized welfare/medical review by Unit Medical Officer / Psychologist."* |
| $Q_{\text{data}} < 0.40$| N/A | Any | `INCONCLUSIVE_DATA` | No | *"Telemetry quality insufficient for multimodal assessment; maintain routine monitoring."* |

---

## 5. REST APIs Added & Extended

- **`POST /api/v1/voice/check-in`**: Processes voluntary 20-30s voice check-in, verifies consent, extracts acoustic features, evaluates personal baseline deviation, discards raw audio.
- **`GET /api/v1/voice/status`**: Returns personal acoustic baseline state ($N \ge 3$ required).
- **`GET /api/v1/voice/history`**: Returns historical acoustic feature snapshots for authenticated user.
- **`POST /api/v1/voice/demo-sample`**: Synthesizes WAV audio base64 stream for testing without physical mic hardware.
- **`POST /api/v1/welfare/evaluate`**: Executes multimodal evidence fusion across all intelligence streams.
- **`GET /api/v1/welfare/personnel/{id}/current`**: Returns current multimodal welfare assessment (RBAC enforced).
- **`GET /api/v1/welfare/unit/{unit_id}/summary`**: Returns aggregate unit welfare distribution for Command Authority.

---

## 6. Verification & Test Summary

- `backend/tests/test_voice_intelligence.py`: **16/16 tests passed**.
- `backend/tests/test_contextual_graph.py`: **12/12 tests passed**.
- `backend/tests/test_tri_layer_integration.py`: **7/7 tests passed**.
- `backend/test_feature_extraction.py`: **7/7 tests passed**.
- `backend/test_model_inference.py`: **4/4 tests passed**.
- **Total Repository Test Suite**: **46/46 tests passed (100%)**.
