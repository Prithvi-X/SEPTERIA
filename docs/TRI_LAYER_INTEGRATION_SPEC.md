# SEPTERIA Tri-Layer Integration & Mathematical Gating Specification

**Project**: SEPTERIA — AI-Based Predictive Personnel Stress and Welfare Monitoring System for Uniformed Forces  
**SIH Problem Statement**: SIH26186  
**Document**: `docs/TRI_LAYER_INTEGRATION_SPEC.md`  
**Version**: 1.2.0-REVISED (Exertion Context Disambiguation & Configurable Gating Architecture)  
**Status**: APPROVED CONCEPTUAL SPECIFICATION — PENDING IMPLEMENTATION

---

> [!IMPORTANT]
> ### Crucial Model & Architecture Boundaries
> 1. **Layer 1 ML Boundary**: The machine learning model is strictly a **Prototype Trained Stress Model** trained on public wearable laboratory datasets (WESAD, PhysioNet). It produces a raw physiological stress likelihood $P_{\text{physio}} \in [0.0, 1.0]$. It did **NOT** learn operational relationships or combat deployment dynamics.
> 2. **Layer 2 Interpretation Boundary**: Personal baseline normalization, multi-source corroboration, and operational context interpretation are performed by the Phase 5 logic engine.
> 3. **Layer 3 Decision Boundary**: Final welfare alerts are gated by temporal persistence, data quality checks, and human-in-the-loop decision-support rules.
> 4. **Exertion Context Disambiguation (No Hard Clamping)**: Physical exertion (running, tactical maneuvers) does **NOT** prove the absence of psychological stress; an individual can experience physical exertion and acute psychological stress simultaneously. During exertion, physiological activation alone is disqualified from triggering stress alerts, but independent corroborating evidence (sleep deficit, recovery debt, deteriorating trajectory) remains active.
> 5. **Provisional Prototype Parameters**: All mathematical constants, weights, and thresholds defined herein are **provisional prototype parameters**. They are completely configurable and require calibration against specific wearable hardware and military operational data.
> 6. **Zone Decision-Gating Semantics**:
>    - **Zone 1: High-Intensity / Active Operations**
>    - **Zone 2: Border / Remote / Extreme Environment**
>    - **Zone 3: Critical Incident / Post-Incident Recovery**  
>    *Operational zones define environmental contexts and decision-gating rules, NEVER risk rankings or medically validated thresholds.*

---

## 1. Tri-Layer Architectural Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ LAYER 1: PHYSIOLOGICAL INFERENCE ENGINE (ML Core)                           │
│ - Inputs: 25 Wearable Features (60s Window: HR, PRV, EDA, TEMP, ACC)        │
│ - Model: Prototype XGBoost Stress Model (`xgboost_stress_model.joblib`)      │
│ - Missing Telemetry: Native NaN routing (motion-corrupted PRV)              │
│ - Output: Raw Physiological Stress Probability P_physio ∈ [0.0, 1.0]        │
│ - Data Quality Metric: Q_data ∈ [0.0, 1.0] (Sensor contact, valid beats)    │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ LAYER 2: PERSONAL BASELINE & CONTEXT DISAMBIGUATION (Phase 5 Logic Engine)  │
│ - Inputs: P_physio, Q_data, Personnel ID, Personal Baseline (Median, MAD),  │
│           Authoritative Zone, Shift Context, Leave Status                   │
│                                                                             │
│ 1. Exertion Context Tagging & Attribution Disambiguation:                   │
│    - Detects active movement -> Tag: `PHYSICAL_EXERTION`                    │
│    - Discounts attribution of physiological elevation to acute stress alone │
│    - Disallows single-channel physiological escalation during exertion      │
│    - Retains independent non-kinetic corroboration (sleep, debt, trend)     │
│                                                                             │
│ 2. Personal Baseline Robust Deviation Modulator:                            │
│    - Compares current window against soldier's personal resting baseline    │
│    - Dampens ML probability when current state is homeostatically normal    │
│    - Accentuates probability when personal autonomic strain is elevated     │
│                                                                             │
│ 3. Multi-Source Evidence Corroboration:                                     │
│    - Trajectory Direction: IMPROVING (+1), STABLE (0), DETERIORATING (-1)   │
│    - Recovery Burden Score (0 - 100) and Sleep Deficit Hours (Δ Sleep)      │
│                                                                             │
│ 4. 3-Zone Operational Decision Gating:                                      │
│    - Zone 1 (High-Intensity / Active Ops): Decision Gate T1                 │
│    - Zone 2 (Border / Remote Duty): Decision Gate T2                        │
│    - Zone 3 (Critical Incident Recovery): Dynamic Bounded Gate T3           │
│                                                                             │
│ - Output: Context-Calibrated Stress Index P_calibrated ∈ [0.0, 1.0]         │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ LAYER 3: FINAL WELFARE RISK DECISION & COOLDOWN GATING (Action Gate)        │
│                                                                             │
│ 1. Data Quality & Evidence Consistency Gate:                                │
│    - If Q_data < min_quality OR contradictory evidence -> LOW CONFIDENCE    │
│    - Refuses to manufacture certainty or escalate on degraded telemetry     │
│                                                                             │
│ 2. Configurable Temporal Persistence Filter (Anti-Spike Gate):              │
│    - Requires K-of-N consecutive windows above decision gate to escalate    │
│    - Prevents transient spikes from triggering alarm fatigue                │
│                                                                             │
│ 3. 4-Tier Welfare State Mapping (Human-in-the-Loop):                        │
│    - GREEN  (Optimal Equilibrium / Physiological Exertion Normalcy)         │
│    - YELLOW (Mild Elevation / Routine Unit Monitoring)                      │
│    - AMBER  (Sustained Autonomic Strain / Recommend Authorized Welfare Check│
│    - RED    (Severe Disruption + Deteriorating Trajectory / Recommend       │
│              Authorized Welfare/Medical Review)                             │
│                                                                             │
│ 4. Human Professional Decision Authority:                                   │
│    - No automatic medical diagnoses or mandatory duty groundings            │
│    - Decision-support payloads for Unit Medical Officers and Psychologists  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Configurable Prototype Parameters Schema (`TriLayerConfig`)

All thresholds, multipliers, and penalty factors are encapsulated as provisional prototype parameters requiring field calibration:

```python
DEFAULT_TRI_LAYER_CONFIG = {
    # -------------------------------------------------------------------------
    # Layer 2: Kinetic Exertion Disambiguation (Provisional Prototype Parameters)
    # -------------------------------------------------------------------------
    "exertion_motion_energy_threshold": 2.0,      # Provisional kinetic energy threshold
    "exertion_magnitude_std_threshold": 1.5,      # Provisional acceleration std threshold
    "exertion_attribution_discount": 0.40,        # Discount factor on raw P_physio attribution during exertion
    
    # -------------------------------------------------------------------------
    # Layer 2: Personal Baseline Modulation (Provisional Prototype Parameters)
    # -------------------------------------------------------------------------
    "baseline_dampening_factor": 0.60,            # Factor applied when within normal personal baseline
    "baseline_autonomic_z_normal_cutoff": 0.50,   # Composite z-score threshold for normal baseline state
    "baseline_amplification_slope": 0.20,         # Sensitivity scale when personal baseline is elevated
    "baseline_autonomic_z_elevated_cutoff": 1.50, # Composite z-score threshold for elevated personal strain
    
    # -------------------------------------------------------------------------
    # Layer 2: 3-Zone Operational Decision Gates (Provisional Gating Parameters)
    # -------------------------------------------------------------------------
    "zone_1_decision_threshold": 0.60,            # High-Intensity / Active Operations decision gate
    "zone_2_decision_threshold": 0.50,            # Border / Remote / Extreme Environment decision gate
    "zone_3_base_threshold": 0.50,                # Critical Incident base decision gate
    "zone_3_min_threshold": 0.30,                 # Critical Incident sensitivity lower bound
    "zone_3_recovery_debt_weight": 0.002,         # Sensitivity adjustment weight per burden point
    "zone_3_sleep_deficit_weight": 0.03,          # Sensitivity adjustment weight per deficit hour
    
    # -------------------------------------------------------------------------
    # Layer 3: Temporal Persistence (Anti-Spike Rule)
    # -------------------------------------------------------------------------
    "persistence_required_windows": 2,            # K windows required above decision gate
    "persistence_window_history_size": 3,         # N total recent windows evaluated
    
    # -------------------------------------------------------------------------
    # Layer 3: Data Quality & Action Confidence Gating
    # -------------------------------------------------------------------------
    "min_data_quality_for_action": 0.50,          # Minimum quality required for alert escalation
    "contradiction_penalty_factor": 0.50,         # Penalty coefficient applied when evidence is contradictory
    "cooldown_period_minutes": 30                 # Minimum interval between repeated alert escalations
}
```

---

## 3. Mathematical Formulations & Gating Logic

### A. Kinetic Exertion Disambiguation (No Hard Clamping)

Physical exertion (sprints, patrols, obstacle courses) naturally elevates heart rate and skin conductance due to metabolic demand. Crucially, a soldier can experience intense physical exertion and severe psychological threat simultaneously.

1. **Exertion Context Detection**:
   $$\text{IsExertion} = (\text{acc\_motion\_energy} \ge \theta_{\text{motion}}) \lor (\text{acc\_magnitude\_std} \ge \theta_{\text{acc\_std}})$$

2. **Attribution Disambiguation**:
   - When $\text{IsExertion} = \text{True}$, raw physiological stress probability is discounted to reflect metabolic confounding:
     $$\tilde{P}_{\text{exertion}} = P_{\text{physio}} \times \left(1.0 - \theta_{\text{exertion\_discount}}\right)$$
   - **Gating Rule**: During physical exertion, physiological elevation alone **CANNOT** escalate an alert to `AMBER` or `RED`.
   - **Corroborating Evidence Exception**: If independent corroborating indicators (Recovery Debt $\ge 60$, Sleep Deficit $\ge 3.0\text{h}$, deteriorating multi-window trajectory) are present alongside exertion, the engine tags the window as `COMBINED_PHYSICAL_AUTONOMIC_STRAIN` and allows non-punitive welfare review.

---

### B. Personal Baseline Robust $z$-Score Modulation

For a given personnel member with established historical baseline median ($\tilde{x}$) and Median Absolute Deviation ($\text{MAD}$):

1. **Robust Standardized Deviations**:
   $$z_{\text{HR}} = \frac{0.6745 \times (\text{HR}_{\text{obs}} - \tilde{x}_{\text{HR}})}{\max(\text{MAD}_{\text{HR}}, 1.0)}$$
   $$z_{\text{rMSSD}} = \frac{0.6745 \times (\text{rMSSD}_{\text{obs}} - \tilde{x}_{\text{rMSSD}})}{\max(\text{MAD}_{\text{rMSSD}}, 1.0)}$$
   $$r_{\text{EDA}} = \frac{\text{EDA\_tonic}_{\text{obs}}}{\max(\tilde{x}_{\text{EDA}}, 0.05)}$$

2. **Composite Autonomic Strain Index**:
   $$\bar{z}_{\text{autonomic}} = \frac{z_{\text{HR}} - z_{\text{rMSSD}} + \max(0, r_{\text{EDA}} - 1.0) \times 2.0}{3.0}$$

3. **Baseline-Modulated Probability**:
   $$\tilde{P}_{\text{baseline}} = \begin{cases} \tilde{P}_{\text{exertion}} \times \theta_{\text{dampen}}, & \text{if } \bar{z}_{\text{autonomic}} \le \theta_{z\text{\_normal}} \text{ (within normal personal homeostatic baseline)} \\ \min\left(1.0, \tilde{P}_{\text{exertion}} \times \left(1.0 + \theta_{\text{amp\_slope}} \times \bar{z}_{\text{autonomic}}\right)\right), & \text{if } \bar{z}_{\text{autonomic}} \ge \theta_{z\text{\_elevated}} \text{ (elevated personal strain)} \\ \tilde{P}_{\text{exertion}}, & \text{otherwise (moderate / intermediate deviation)} \end{cases}$$

---

### C. 3-Zone Operational Decision Gates & Context Rules

Operational zones provide situational context and define operational decision gates (they are **NOT** risk rankings or medical thresholds):

1. **Zone 1 — High-Intensity / Active Operations**:
   - Active combat, counter-insurgency, tactical mountain patrol.
   - Decision Gate: $T_{\text{zone}} = \theta_{\text{zone1\_gate}}$ ($0.60$ default).
   - High specificity prioritizes eliminating false alarms during dynamic operational maneuvers.
2. **Zone 2 — Border / Remote / Extreme Environment**:
   - Border outpost duty, extended remote surveillance, extreme environmental deployment.
   - Decision Gate: $T_{\text{zone}} = \theta_{\text{zone2\_gate}}$ ($0.50$ default).
   - Evaluates multi-day recovery trajectory and cumulative sleep deficit equilibrium.
3. **Zone 3 — Critical Incident / Post-Incident Recovery**:
   - Post-ambush debriefing, casualty evacuation recovery, high-trauma post-incident window.
   - Bounded Evidence-Based Dynamic Decision Gate:
     $$T_{\text{zone}} = \text{clip}\left(\theta_{\text{zone3\_base}} - w_{\text{burden}} \cdot \text{RecoveryDebt} - w_{\text{sleep}} \cdot \text{SleepDeficit}, \theta_{\text{zone3\_min}}, \theta_{\text{zone3\_base}}\right)$$
   - *Rationale*: A soldier in Zone 3 with high recovery debt and sleep deficit has higher vulnerability; the decision gate is dynamically adjusted ($T_{\text{zone}} \to 0.30 - 0.38$) to ensure post-incident autonomic disruption is surfaced for early medical review.

---

### D. Data Quality Gating & Evidence Consistency

Telemetry degradation (motion artifact, optical sensor liftoff, loose wristband) must **lower algorithmic confidence** rather than create artificial certainty:

1. **Window Quality Score ($Q_{\text{data}} \in [0.0, 1.0]$)**:
   - Evaluates valid beat count ($N_{\text{beats}} \ge 15$), physiological bounds ($20^\circ\text{C} \le \text{Temp} \le 45^\circ\text{C}$, $\text{EDA} \ge 0.005\,\mu\text{S}$), and signal completeness.
2. **Evidence Contradiction Check**:
   - If HR is very high ($>110\text{ bpm}$) but EDA is flatlined ($<0.05\,\mu\text{S}$) and ACC is near zero, tag as `CONTRADICTORY_EVIDENCE`.
3. **Action Confidence Index**:
   $$\text{ActionConfidence} = Q_{\text{data}} \times \left(1.0 - \theta_{\text{contradiction\_penalty}} \times \mathbb{I}_{\text{contradiction}}\right)$$
4. **Quality Gate**:
   - If $\text{ActionConfidence} < \theta_{\text{min\_quality}}$ ($0.50$ default):
     - State = `INCONCLUSIVE_DATA` (Tagged with: "Telemetry quality insufficient for alert escalation; continue passive monitoring").

---

### E. Temporal Persistence (Anti-Spike Rule)

To prevent transient spikes (e.g. coughing, momentary surprise, adjusting gear) from triggering alarm fatigue:
- Evaluate the last $N$ consecutive 60-second windows (default $N=3$).
- Require at least $K$ windows (default $K=2$) to have $\tilde{P}_{\text{baseline}} \ge T_{\text{zone}}$.
- An isolated single-window elevation is classified as `TRANSIENT_SPIKE` and kept at `YELLOW` (monitoring) rather than escalating to `AMBER` or `RED`.

---

### F. 4-Tier Welfare State Mapping & Human-in-the-Loop Protocol

| Welfare State | Trigger Criteria | Action Confidence | Recommended Operational Action |
| :--- | :--- | :---: | :--- |
| **GREEN** | $\tilde{P}_{\text{baseline}} < T_{\text{zone}}$ OR (IsExertion AND Recovery Debt $< 50$) | Any | Normal physiological equilibrium; routine passive monitoring. |
| **YELLOW** | $\tilde{P}_{\text{baseline}} \ge T_{\text{zone}}$ (single window) OR mild baseline elevation ($z > 1.0$) | $\ge 0.50$ | Routine unit welfare monitoring; verify hydration and rest. |
| **AMBER** | Sustained elevation ($K$-of-$N$ windows $\ge T_{\text{zone}}$) AND Recovery Debt $\ge 50$ | $\ge 0.60$ | **Recommend authorized unit welfare check** by designated peer / section commander. |
| **RED** | Sustained elevation ($K$-of-$N$ windows $\ge T_{\text{zone}}$) AND Trajectory is `DETERIORATING` AND Recovery Debt $\ge 70$ | $\ge 0.70$ | **Recommend authorized welfare/medical review** by Unit Medical Officer (UMO) / Psychologist. |
| **INCONCLUSIVE** | Action Confidence $< 0.50$ | $< 0.50$ | Data quality insufficient for action; check device fit. |

> [!CAUTION]
> **Human-in-the-Loop Command Policy**:
> The system **NEVER** issues automatic medical diagnoses, mandatory duty groundings, or disciplinary flags. All recommendations are presented as decision-support evidence to authorized medical and welfare professionals.

---

## 4. Verification & Testing Strategy

Tests will **NOT** merely assert hardcoded synthetic values. Tests must verify the underlying **logical and mathematical invariants**:

1. **Exertion Logic Invariant**:
   - `test_exertion_discounts_attribution_without_hard_clamp`: High kinetic motion reduces stress attribution without zeroing out or hard-clamping probability; independent corroborating recovery debt remains measurable.
2. **Personal Baseline Modulation Invariant**:
   - `test_baseline_homeostasis_dampens_uncertainty`: When a soldier's personal deviations are within homeostatic baseline ($z < 0.5$), calibrated probability must be strictly lower than raw ML probability.
3. **Temporal Persistence Invariant**:
   - `test_transient_spike_does_not_escalate`: A single 60s spike followed by normal baseline windows must not escalate beyond `YELLOW`.
   - `test_persistent_elevation_escalates`: Sustained multi-window elevation ($K$-of-$N$) must trigger `AMBER`/`RED` consideration.
4. **Data Quality & Confidence Invariant**:
   - `test_degraded_telemetry_lowers_confidence`: Corrupted or contradictory channels apply configurable penalty and reduce `ActionConfidence`, preventing alert escalation.
5. **Zone Context Invariant**:
   - `test_zone_context_changes_decision_gate`: The exact same physiological window must be evaluated against different decision-gating rules in Zone 1 vs Zone 2 vs Zone 3.
6. **Human-in-the-Loop Advisory Invariant**:
   - `test_recommendations_are_strictly_advisory`: Output payload text must strictly use advisory phrasing ("Recommend authorized welfare/medical review") with zero automated mandatory clinical orders.

---

## 5. Artifact Manifest

1. **Specification Document**: [`docs/TRI_LAYER_INTEGRATION_SPEC.md`](file:///d:/IITM/SIH/PROTOTYPE/ANTIGRAVITY/ANTI-INFO/docs/TRI_LAYER_INTEGRATION_SPEC.md)
2. **Implementation Plan Artifact**: [`implementation_plan.md`](file:///C:/Users/Prith/.gemini/antigravity/brain/5f43e19b-824b-4bd0-9bdf-75a1ce937f84/implementation_plan.md)

---

**The revised mathematical gating specification is finalized. I have stopped here in accordance with your instructions and am awaiting your review.**
