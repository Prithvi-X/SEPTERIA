# SEPTERIA System Architecture (SIH26186)

## 1. Context & Purpose
**SEPTERIA** is an AI-based predictive personnel stress and welfare monitoring platform designed specifically for Ministry of Home Affairs (MHA) Central Armed Police Forces (CAPF: CRPF, BSF, ITBP, CISF, SSB, Assam Rifles).

**Core Principle:**
> *"Stress is not a single sensor reading. Interpret physiology in the context of the person, the duty, the environment, and the trajectory."*

---

## 2. Monorepo Architecture Overview

```
                          ┌────────────────────────────────┐
                          │   Next.js 15 Authority Web     │
                          │   (Commanders & Welfare)       │
                          └───────────────┬────────────────┘
                                          │ REST (JWT / HTTPS)
                                          ▼
┌────────────────────────┐        ┌────────────────────────────────┐
│   Flutter Mobile App   ├───────►│        FastAPI Backend         │
│   (Personnel Portal)   │        │         (/api/v1 REST)         │
└────────────────────────┘        └───────┬──────────────┬─────────┘
                                          │              │
                                          ▼              ▼
                        ┌───────────────────┐  ┌───────────────────┐
                        │   PostgreSQL 16   │  │   AI/ML Engine    │
                        │ (Relational DB)   │  │ (XGBoost / Graph) │
                        └───────────────────┘  └───────────────────┘
```

---

## 3. Tier Responsibilities

### Tier 1: Personnel Mobile App (Flutter)
- **Role:** Private personnel wellness view and self-reporting.
- **Key Capabilities:**
  - View personal recovery trajectory and baseline equilibrium.
  - View current authoritative operational context assigned by command.
  - Submit voluntary wellness check-ins (stress, fatigue, mood, sleep).
  - Submit confidential support requests directly to welfare officers.
  - Zero access to other personnel records or administrative controls.

### Tier 2: Authority Web Dashboard (Next.js 15)
- **Role:** Force administration, operational context manager, and welfare tracking.
- **Key Views:**
  - **Force Overview:** Synthetic aggregate readiness, active zones, temporary assignment countdowns.
  - **Personnel Directory:** Search personnel by ID, rank, posting, and unit.
  - **Operational Context Manager:** Create bulk/unit-level zone assignments (Zone 1/2/3), set time-bound durations with automatic reversion, and trigger 14-day post-leave transition states.
  - **Welfare Cases:** Role-restricted view for Welfare and Medical Officers showing risk level, confidence, and SHAP driver explanations.
  - **Aggregate Intelligence:** Commander view with unit-level stress trends (individual identifiable health data redacted).

### Tier 3: Backend API (FastAPI)
- **Role:** Central business logic, authentication, RBAC authorization, and API versioning.
- **Endpoints:**
  - `/api/v1/health`: System health status check.
  - `/api/v1/auth/login`: Secure sign-in issuing signed JWT access tokens.
  - `/api/v1/auth/me`: Protected current user profile inspection.
  - Modular placeholders for `/personnel`, `/operations`, `/wellness`, `/physiology`, `/predictions`, `/welfare`, `/graph`, `/voice`.

### Tier 4: Database (PostgreSQL 16)
- **Role:** Single relational source of truth across all tiers.
- **Key Tables:** `users`, `units`, `personnel`, `operational_contexts`, `assignments`, `wellness_records`, `physiological_records`, `baselines`, `predictions`, `recommendations`, `audit_logs`.

---

## 4. Analytical Zones (MHA/CAPF Context)

| Zone | Operational Context | Primary Stress Emphasis |
| :--- | :--- | :--- |
| **Zone 1** | High-Intensity / Active Operations | Acute operational load, HR/HRV response, physical exertion, duty hours. |
| **Zone 2** | Border / Remote / Extreme Environment | Cumulative recovery deterioration, sleep deficits, extreme heat/cold exposure, isolation. |
| **Zone 3** | Critical Incident / Post-Incident Recovery | Incident response trajectory, resting HR elevation, longitudinal recovery post-event. |

*Note: Post-leave monitoring is a 14-day temporary transition state layered over the active operational zone, not a fourth zone.*
