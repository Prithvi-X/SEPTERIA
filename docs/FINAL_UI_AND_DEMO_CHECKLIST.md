# SEPTERIA (SIH26186) — Final UI & Demo Checklist

**Project Name:** SEPTERIA  
**Problem Statement:** SIH26186 — Predictive Stress & Welfare Monitoring System for CAPF Personnel  
**Version:** 1.0.0-PROD-DEMO (Phase 11 Complete)  
**Safety Classification:** Non-punitive decision support prototype. Not a clinical diagnostic device.

---

## 1. System Architecture & Launch Configuration

| Subsystem | Tech Stack | Port / Location | Status |
| :--- | :--- | :--- | :--- |
| **Backend REST API** | FastAPI, Python 3.11, SQLAlchemy, Uvicorn | `http://127.0.0.1:8000` | ✅ Active (117/117 Tests Passed) |
| **Authority Web Portal** | Next.js 14, Tailwind CSS, Lucide Icons | `http://localhost:3000` | ✅ Active (TypeScript Clean) |
| **Personnel Mobile App** | Flutter 3.x, Dart | `apps/personnel-mobile` | ✅ Active (BLE GATT 0x2A37) |
| **ML Inference Core** | XGBoost (WESAD / PhysioNet / SWELL-KW) | `ml/models/` | ✅ Active ($P_{\text{physio}}$ Gated) |
| **Contextual Graph** | NetworkX (7 Relational Entity Types) | In-Memory / PostgreSQL | ✅ Active (Cluster Detection) |
| **Voice Intelligence** | PyAudioAnalysis / SciPy / Parselmouth | In-Memory (Zero Audio Retained) | ✅ Active ($F_0$ / Pause Ratio) |
| **Edge / Hardware Hub** | Standard Bluetooth SIG BLE GATT & Health Connect | Adapter Layer | ✅ Active (Pluggable Ingestion) |

---

## 2. Master Credentials & RBAC Access Matrix

| Role | Email / ID | Password | Scope & Privacy Guarantee |
| :--- | :--- | :--- | :--- |
| **Welfare / Medical Officer** | `welfare@septeria.gov.in` | `Welfare@1234` | **Full Case Access**: Multimodal SHAP drivers, resting HR/HRV baselines, voluntary voice deviation, clinical triage protocol. |
| **Unit Commander** | `commander@septeria.gov.in` | `Commander@1234` | **Aggregate Unit Intelligence**: Battalion headcount, shift fatigue alerts, contextual graph cluster patterns (`PAT-BSF-BN-47-ZONE_2-Night-1`). **Individual biometrics strictly redacted**. |
| **Admin Authority** | `admin@septeria.gov.in` | `Admin@1234` | **System Governance**: Operational zone assignments, master demo reset, fleet health audit, audit trail logs. |
| **Soldier / Jawan (Mobile)** | `BSF-47-01` (Constable Rajesh Kumar) | `Rajesh@1234` | **Self-Service**: Personal recovery score, sleep debt tracking, voluntary voice check-in, confidential peer support. |

---

## 3. End-to-End Demonstration Walkthrough (12-Step Pitch Flow)

### Act I: Force Command & Tactical Deployment (1.5 Minutes)
1. **Navigate to Force Overview** (`http://localhost:3000/dashboard`):
   - **Visual Polish**: Confirm dark tactical theme, PostgreSQL live indicator, and **"DEMO MODE • SYNTHETIC DEMONSTRATION DATA"** header banner.
   - **Key Invariant Highlight**: Point out that **Operational Zones represent tactical deployment contexts** (Zone 1 Active Ops, Zone 2 Border Outpost, Zone 3 Recovery), **NOT individual risk levels**.
   - **Fleet Ingestion**: Highlight 98.4% BLE GATT telemetry completeness.

2. **Navigate to Command Force Intelligence** (`http://localhost:3000/analytics`):
   - **Unit Selection**: Select `47th Battalion BSF (Tanot Sector)`.
   - **Shared Distress Alert**: Inspect pattern alert `PAT-BSF-BN-47-ZONE_2-Night-1` (14 Jawans affected concurrently by Night Shift rotation).
   - **Contextual Graph Canvas**: Point out NetworkX topology visualizing the unit cluster.
   - **Commander Privacy Mandate**: Show the prominent blue banner: *"Commander Privacy Boundary Enforced: Zero individual biometrics or private voice recordings accessible."*

---

### Act II: Multimodal Medical & Welfare Case Review (2.0 Minutes)
3. **Navigate to Medical & Welfare Review** (`http://localhost:3000/welfare`):
   - **Officer Clearance**: Note the green *"Medical RBAC Active"* badge.
   - **Case Triage Queue**: Select **Constable Rajesh Kumar (`BSF-47-01`)**.
   - **State Badge**: Confirm `WELFARE_CHECK` (Pulsing Amber/Red).
   - **Multimodal Evidence Breakdown (5 Converging Streams)**:
     - **Stream 1 (Wearable ML)**: $P_{\text{physio}} = 0.82$ (Sympathetic Activation, motion-disambiguated).
     - **Stream 2 (Personal Autonomic Baseline)**: Baseline shift $+20\text{ bpm}$ above personal resting median ($z = +2.45$).
     - **Stream 3 (Recovery Trajectory)**: Cumulative $4.5\text{h}$ sleep debt, $78\%$ recovery burden score.
     - **Stream 4 (Contextual Graph)**: Platoon correlation corroborated ($14$ Jawans in identical shift).
     - **Stream 5 (Voluntary Voice)**: Acoustic pitch & pause ratio deviation ($97.2\%$), zero raw audio stored.
   - **Evidence Agreement Index**: $84\%$ high multi-stream confidence.
   - **Human-in-the-Loop Action**: Click **"Acknowledge Case"** or **"Assign Peer Check"** to demonstrate non-punitive care workflow.

---

### Act III: Soldier Empowerment Mobile App (1.5 Minutes)
4. **Open Personnel Mobile Experience (`apps/personnel-mobile`)**:
   - **Jawan Home Tab**:
     - Displays current operational context (Zone 2, Night Patrol) as read-only.
     - Shows BLE Tactical Band connected and synced.
   - **My Trends & Recovery Tab**:
     - Shows personal recovery score and sleep debt without punitive ranking.
     - **Plain-Language Explainability**: *"Why did my state change? Cumulative night shift fatigue and 4.5h sleep deficit."*
   - **Voluntary Voice Check-In**:
     - Tap microphone to initiate 10-second voluntary voice check-in.
     - Extracted acoustic features ($F_0$, jitter, pause dynamics) processed locally in memory.
   - **Support & Confidential Privacy Center**:
     - Peer buddy request, Medical Officer tele-consultation request, and clear confirmation that biometrics are never shared with Commanding Officers.

---

## 4. Live Interactive Demo Controller (Zero Code Edits Needed)

The Authority Web Portal includes a floating **"Demo Controls"** modal in the top navigation bar:

| Demo Button | Backend Action Triggered | Intended Demo Outcome |
| :--- | :--- | :--- |
| **🔄 Master Demo Reset** | `POST /api/v1/system/reset-demo` | Cleans all synthetic telemetry and returns system to clean baseline. |
| **🟢 Load Normal Baseline** | `POST /api/v1/edge/demo/simulate-stream?scenario=A` | Demonstrates healthy recovery homeostasis (HR 64 bpm, HRV 65 ms, 7.8h sleep). |
| **🔴 Multi-Day Recovery Decline** | `POST /api/v1/edge/demo/simulate-stream?scenario=C` | Ingests 7-day cumulative strain for Unit 47, triggering `WELFARE_CHECK`. |
| **🏃 Kinetic Physical Exertion** | `POST /api/v1/edge/demo/simulate-stream?scenario=B` | Ingests active workout ($ACC > 2.0\text{ m/s}^2$), proving that physical exertion alone **never** triggers false alarm. |
| **⚙️ System Health Audit** | `GET /api/v1/system/health-audit` | Displays live multi-subsystem diagnostics verifying all 9 layers. |

---

## 5. Strict Scientific & Ethical Invariants

| Dimension | Mandatory Prototype Claim Boundary |
| :--- | :--- |
| **Deployment Status** | Working software prototype evaluated against benchmark datasets; requires formal CAPF field trial before live operational deployment. |
| **Clinical Diagnosis** | Not a medical diagnostic device, psychiatric diagnostic system, or suicide prediction tool. |
| **Command Visibility** | Commanders receive unit aggregates and shift rotation recommendations; commanders **never** see individual soldier biometrics. |
| **Voice Privacy** | Voice check-in is 100% voluntary; raw audio is processed strictly in-memory and immediately destroyed. |
| **Data Integrity** | Poor signal quality (SQI < 0.50) results in `INCONCLUSIVE_DATA` rather than false alarms. |

---

## 6. Verification Status

```bash
# Automated Test Verification (100% Passing)
pytest backend/tests/ ml/tests/ -v
================== 117 passed, 1 skipped in 68.31s ==================

# Next.js TypeScript Typecheck
npx tsc --noEmit
Exit Code: 0 (Zero Errors)
```

**SEPTERIA is now 100% presentation-ready, visually polished, and hardened for the SIH Final Demo.**
