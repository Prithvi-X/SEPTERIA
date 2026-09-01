# SEPTERIA: Final Demonstration & Presentation Guide

**Project**: SEPTERIA — AI-Based Predictive Personnel Stress and Welfare Monitoring System for Uniformed Forces  
**SIH Problem Statement**: SIH26186  
**Status**: Ready for Grand Finale Evaluation & Live Demonstration  
**Classification**: Research Prototype • Decision Support • Non-Punitive  

---

## 1. Important Ethical & Scientific Claim Boundaries

> [!IMPORTANT]
> **MANDATORY SCIENTIFIC & ETHICAL BOUNDARIES**:
> - **Not a Clinical Diagnostic Tool**: SEPTERIA does not diagnose psychiatric conditions, depression, PTSD, or suicide risk.
> - **Not a Replacement for Medical/Human Authority**: Final welfare decisions and clinical reviews remain strictly under the purview of authorized Unit Medical Officers and Unit Psychologists.
> - **No False Claims of Real Field Validation**: All physiological data presented in this prototype are generated using deterministic synthetic streams or laboratory benchmark datasets (WESAD, PhysioNet, CaTSA).
> - **Zero Raw Audio Retention**: Voice check-in is 100% voluntary and user-initiated; raw audio bytes are processed in volatile memory and discarded immediately without persistent storage.
> - **Strict Role-Based Privacy Isolation**: Section Commanders have access **only** to aggregate unit readiness metrics and shift patterns. Individual raw biometrics, personal baselines, and voice parameters are strictly blocked from commander views.

---

## 2. Master Demonstration Scenario (BSF Unit 47)

- **Battalion**: 47th Battalion Border Security Force (`BSF-BN-47`), Tanot Forward Sector B (Rajasthan).
- **Personnel**: Constable Rajesh Kumar (`BSF-47-01`), Lead Scout / GD.
- **Timeline & Operational Progression**:
  1. **Phase A (Baseline Equilibrium)**: Normal resting recovery at base station (Resting HR 64 bpm, HRV 65 ms, 7.8 hrs sleep).
  2. **Phase B (Operational Context Escalation)**: Assigned to **Zone 2** (Forward Remote Border Post), Night Patrol shift (20:00 - 04:00), on **Temporary Forward Assignment** (7 days remaining), during **Day 3 / 14 Post-Leave Transition**.
  3. **Phase C (Cumulative Telemetry Deterioration)**: Over 7 simulated days, sleep decreases to 3.8 hrs, resting HR elevates to 84 bpm (+20 bpm), HRV suppresses to 24 ms (autonomic reserve depletion), and kinetic exertion is logged during patrol.
  4. **Phase D (Tri-Layer ML Decision Gating)**: Kinetic motion is disambiguated from psychological distress; persistent baseline deviation across multi-day windows passes Zone 2 gate.
  5. **Phase E (Contextual Personnel Graph)**: Cluster analysis detects **14 Jawans** in Unit 47 experiencing concurrent recovery deterioration under identical Night Shift / Zone 2 environmental exposure.
  6. **Phase F (Voluntary Voice Check-In)**: User initiates optional 20-second check-in; acoustic analysis detects elevated pitch and increased pause ratio without clinical labeling.
  7. **Phase G (Multimodal Evidence Convergence)**: System issues advisory state **`WELFARE_CHECK`** with non-punitive action text: *"Recommend authorized unit welfare check (Corroborating multi-stream strain across baseline, recovery, and operational indicators)."*

---

## 3. Two-Minute Live Demonstration Flow

| Step | Time | Screen / Action | What to Say / Present |
| :--- | :--- | :--- | :--- |
| **1** | `0:00 - 0:30` | **Authority Web Dashboard** (`http://localhost:3000`) | *"Here is the Commander View for BSF Battalion 47. Notice that commanders see fleet operational readiness, shift distributions, and unit-level cluster alerts without exposing private individual biometrics."* |
| **2** | `0:30 - 1:00` | **Contextual Personnel Graph** | *"The Contextual Graph identifies a shared recovery strain pattern affecting 14 Jawans on the Tanot Night Patrol sector, indicating environmental/duty burden rather than individual failure."* |
| **3** | `1:00 - 1:30` | **Personnel Mobile App** (Flutter) | *"Switching to Constable Rajesh Kumar's confidential phone view: He sees his authoritative operational context (Zone 2, Night Shift, Day 3 post-leave), recovery debt (4.5h), and can voluntary record a voice check-in."* |
| **4** | `1:30 - 2:00` | **Multimodal Decision & Recommendation** | *"All five evidence streams converge into our Tri-Layer Decision Engine, recommending an authorized unit welfare check. The system acts as a non-punitive early decision support shield."* |

---

## 4. Five-Minute Detailed Technical Walkthrough

### Part 1: System Reset & Telemetry Ingestion (Minute 1)
- Trigger clean demonstration reset via terminal or UI:
  ```powershell
  python scripts/run_full_demo.py
  ```
- **Key Highlight**: Edge Ingestion Layer (`EdgeDataSourceAdapter`) receives Bluetooth SIG GATT 0x2A37 Heart Rate and Android Health Connect packets, verifies idempotency keys (SHA-256) to prevent duplicate insertion during retries, audits clock drift, and passes data to the **Phase 4 Data Quality Pipeline**.

### Part 2: Personal Baseline & Tri-Layer Decision Gating (Minute 2)
- Open **Tri-Layer Stress Engine** telemetry evaluation.
- **Key Highlight**: Show that physical exertion (accelerometer energy $> 2.0\text{ m/s}^2$) **never** triggers an emergency alert on its own. The Tri-Layer engine disambiguates kinetic motion, compares autonomic metrics against the soldier's personal baseline ($z_{\text{autonomic}} = +2.45$), and applies Zone 2 decision threshold gating ($T = 0.50$).

### Part 3: Contextual Personnel Graph Intelligence (Minute 3)
- Navigate to **Contextual Personnel Graph Explorer**.
- **Key Highlight**: NetworkX graph maps unit relationships, duty shifts, and recovery trajectories. When 14 Jawans in the same platoon exhibit synchronized autonomic strain, the graph tags a **Shared Operational Pattern** (`PAT-BSF-BN-47-ZONE_2-Night-1`), recommending command shift rotations rather than pathologizing individual soldiers.

### Part 4: Voluntary Voice Intelligence & Privacy (Minute 4)
- Open **Voice Check-In** screen on Mobile.
- **Key Highlight**: Explicit consent is required before recording. The Librosa/SciPy engine extracts $F_0$ pitch dynamics, pause ratios, and MFCC features in volatile memory. Raw audio is immediately discarded (`raw_audio_retained = False`). Feature shifts are presented in non-diagnostic, supportive language.

### Part 5: Command vs Welfare RBAC Enforcement (Minute 5)
- Log in as **Welfare / Medical Officer** vs **Battalion Commander**.
- **Key Highlight**: Prove database-level RBAC. Commander sees aggregate readiness percentages; Welfare Officers see authorized intervention checklists; Personnel see strictly their own recovery trends.

---

## 5. Exact Screens & URLs for Presentation

1. **Authority Command Dashboard**:
   - URL: `http://localhost:3000/dashboard`
   - Role: `commander@septeria.mil` (Password: `commander123`)
2. **Contextual Personnel Graph Visualizer**:
   - URL: `http://localhost:3000/graph`
   - Role: `commander@septeria.mil` / `welfare@septeria.mil`
3. **Medical & Welfare Case Manager**:
   - URL: `http://localhost:3000/welfare`
   - Role: `welfare@septeria.mil` (Password: `welfare123`)
4. **Personnel Mobile Self-Service App**:
   - Target: Flutter Android / Web Client (`apps/personnel-mobile`)
   - Role: `soldier@septeria.mil` (Password: `soldier123`)
5. **Interactive API Documentation**:
   - URL: `http://localhost:8000/api/v1/docs`

---

## 6. Graceful Degradation & Fallback Modes

| Failure Condition | System Behavior | User/Authority Display |
| :--- | :--- | :--- |
| **No Wearable Connected** | `EdgeSyntheticAdapter` active | `SYNTHETIC DEMONSTRATION DATA` banner shown. |
| **Tactical Network Disconnected** | `EdgeSyncQueue` buffers locally | `SYNC: Pending (Offline Buffer Active)`; zero data dropped. |
| **Voice Feature Unavailable** | Baseline fallback without acoustic stream | Multimodal engine re-weights physiological and baseline evidence ($w_{\text{voice}} \to 0$). |
| **Low Data Quality / Noise ($Q < 0.40$)** | Phase 4 Quality Gate intercepts | Advisory state displays `INCONCLUSIVE_DATA`; routine monitoring maintained. |
| **PostgreSQL Unreachable** | Automatic local SQLite fallback | System logs warning and maintains 100% operation on `septeria.db`. |

---

## 7. Command Execution Quick Reference

```powershell
# 1. Run Complete End-to-End Master Demo
python scripts/run_full_demo.py

# 2. Run Full Automated Test Suite (117+ Tests)
pytest backend/tests/ ml/tests/ -v

# 3. Launch Backend API Server
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

# 4. Launch Authority Web Dashboard
cd apps/authority-web; npm run dev

# 5. Launch Personnel Mobile App
cd apps/personnel-mobile; flutter run -d chrome
```
