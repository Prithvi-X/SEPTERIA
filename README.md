# SEPTERIA (SIH26186)
**AI-Based Predictive Personnel Stress and Welfare Monitoring System for Uniformed Forces**

---

## 1. Project Overview & Scope
**SEPTERIA** is a context-aware, predictive personnel welfare and stress monitoring platform developed for **Smart India Hackathon (SIH 2026 - Problem Statement SIH26186)** under the Ministry of Home Affairs (MHA) / Central Reserve Police Force (CRPF) & CAPF context.

### The Core Problem
Uniformed personnel deployed in counter-insurgency (Zone 1), high-altitude/extreme border environments (Zone 2), and critical incident operations (Zone 3) undergo intense cumulative physical and psychological strain. Traditional welfare monitoring is reactive, periodic, and lacks operational context.

### The SEPTERIA Solution
SEPTERIA integrates **authoritative organizational context** (duty type, night shifts, environment, 14-day post-leave transitions) with **voluntary personnel self-reporting** and **physiological telemetry** (HRV, resting HR, sleep patterns) to predict elevated stress trajectories early, delivering explainable recommendations (via SHAP drivers) to authorized welfare officers while preserving strict personnel privacy.

---

## 2. Technology Stack (Frozen)

| Layer | Technologies |
| :--- | :--- |
| **Authority Web Portal** | Next.js 15 (App Router), React 19, TypeScript, Tailwind CSS |
| **Personnel Mobile App** | Flutter 3.x, Dart |
| **Backend API** | FastAPI, Python 3.11+, Pydantic v2, SQLAlchemy 2.x, Alembic |
| **Database** | PostgreSQL 16 |
| **AI / Machine Learning** | Python, pandas, NumPy, scikit-learn, XGBoost, SHAP *(Phase 9+)* |
| **Contextual Graph** | NetworkX *(Phase 10)* |
| **Voice Processing** | librosa *(Phase 11)* |
| **Security & Auth** | Signed JWT (HS256), Bcrypt password hashing, Backend RBAC, Audit Logging |
| **Deployment** | Docker & Docker Compose |

---

## 3. Monorepo Directory Structure

```
SEPTERIA/
├── apps/
│   ├── authority-web/          # Next.js 15 Web Dashboard for Commanders & Welfare Officers
│   └── personnel-mobile/       # Flutter Mobile App for CAPF Personnel
│
├── backend/
│   ├── app/
│   │   ├── api/                # FastAPI Routers (v1) & Dependencies (deps.py)
│   │   ├── core/               # Configuration, Security, DB Engine, Logging
│   │   ├── models/             # SQLAlchemy ORM Models
│   │   ├── schemas/            # Pydantic Request/Response Contracts
│   │   ├── services/           # Authentication & Domain Services
│   │   └── main.py             # FastAPI App Factory & Middleware
│   ├── alembic/                # Alembic Schema Migrations
│   ├── tests/                  # Pytest Automated Test Suite
│   └── requirements.txt
│
├── ml/                         # ML Training, Feature Engineering, Inference Skeletons
├── graph/                      # Contextual Personnel Graph Skeletons
├── shared/
│   ├── constants/              # Shared Enums (Roles, Zones, EvidenceStatus, Trajectories)
│   └── schemas/                # Cross-tier Pydantic / TypeScript Schema Contracts
│
├── database/
│   ├── migrations/             # SQL Migration Scripts
│   └── seeds/                  # Synthetic Development Seeder (dev_seed.py)
│
├── docs/                       # Architecture & Data Contract Documentation
├── docker/                     # Container Definitions (Dockerfile.backend, Dockerfile.authority-web)
├── .env.example                # Environment Variable Template
├── docker-compose.yml          # Local Container Orchestration
└── README.md
```

---

## 4. Phase 1 Implementation Status

### REAL / IMPLEMENTED (Phase 1)
- [x] Complete Monorepo Directory Structure.
- [x] Shared Data Contracts (Python Pydantic & TypeScript) for Personnel, Operational Context, Wellness, Physiology, Predictions, and Recommendations.
- [x] FastAPI Backend with:
  - Application entry point with CORS middleware and structured logging.
  - Configuration system via `pydantic-settings` reading `.env`.
  - `GET /api/v1/health` health check endpoint.
  - JWT generation, validation, and Bcrypt password hashing.
  - `POST /api/v1/auth/login` and protected `GET /api/v1/auth/me` endpoints.
  - Backend Role-Based Access Control (RBAC) dependency (`require_roles`).
  - Modular API route placeholders for `/personnel`, `/operations`, `/wellness`, `/physiology`, `/predictions`, `/welfare`, `/graph`, `/voice`.
- [x] PostgreSQL 16 Database Configuration:
  - Declarative SQLAlchemy models: `User`, `Unit`, `Personnel`, `OperationalContext`, `Assignment`, `WellnessRecord`, `PhysiologicalRecord`, `Baseline`, `Prediction`, `Recommendation`, `AuditLog`.
  - Alembic migration environment and initial schema migration (`001_initial_schema.py`).
  - Synthetic development dataset seeder (`database/seeds/dev_seed.py`) with labeled demo accounts for all 5 roles.
- [x] Next.js 15 Authority Web Dashboard:
  - App Router application shell with sidebar and top header.
  - Professional, accessible MHA/CAPF administrative UI (slate/navy theme, no fake seals/logos).
  - Routes: `/login`, `/dashboard`, `/personnel`, `/operations`, `/welfare`, `/analytics`, `/settings`.
  - Development-only quick-fill login helper that sends real credentials to the backend for signed JWT generation.
  - Role-protected route architecture (`ProtectedRoute.tsx`).
  - Loading and error boundary states.
- [x] Flutter Personnel Mobile App:
  - Flutter application initialized with dark theme.
  - Screens: `LoginScreen`, `HomeScreen`, `RecoveryScreen`, `WellnessScreen`, `ProfileScreen`, `SupportScreen`.
  - Bottom navigation router.
  - Secure storage abstraction (`flutter_secure_storage`) for tokens.
  - `ApiService` layer interfacing with FastAPI backend.
- [x] Docker Orchestration (`docker-compose.yml`, Dockerfiles).
- [x] Automated Tests passing for Backend API, Health, Auth, RBAC, and Database Models.

### PLANNED / FUTURE PHASES (Not Implemented in Phase 1)
- [ ] Phase 2+: Full RBAC workflow expansions and session refresh rotations.
- [ ] Phase 4+: Interactive force overview charts and personnel search filters.
- [ ] Phase 5+: Dynamic bulk assignment execution, countdown scheduler, and automated context reversion worker.
- [ ] Phase 8+: Rolling personal baseline statistical computation engine.
- [ ] Phase 9+: XGBoost multimodal stress/recovery risk model training, validation, and SHAP driver explanations.
- [ ] Phase 10+: NetworkX contextual personnel graph construction and cooperative imputation.
- [ ] Phase 11+: Librosa voluntary acoustic voice feature extraction.
- [ ] Phase 12+: BLE / Android Health Connect hardware wearable integrations.

---

## 5. Prerequisites & Environment Setup

### System Prerequisites
- **Python**: 3.11 or higher
- **Node.js**: 20.x or higher (npm 10+)
- **Flutter**: 3.x with Dart SDK
- **PostgreSQL**: 16 (or Docker)

### Environment Configuration
Copy `.env.example` to `.env` in the root directory:
```bash
cp .env.example .env
```

Configure your PostgreSQL credentials in `.env`:
```env
DATABASE_URL=postgresql+psycopg2://septeria_user:septeria_secret@localhost:5432/septeria_db
JWT_SECRET=your_secure_256bit_secret_key
API_BASE_URL=http://localhost:8000/api/v1
```

---

## 6. How to Run the System

### Option A: Using Docker Compose (Recommended)
To run PostgreSQL 16, FastAPI Backend, and Next.js Web Dashboard together:
```bash
docker-compose up --build
```
- Web Dashboard: `http://localhost:3000`
- Backend API Docs: `http://localhost:8000/api/v1/docs`
- Health Check: `http://localhost:8000/api/v1/health`

---

### Option B: Running Services Locally

#### 1. Start PostgreSQL 16 & Seed Data
Ensure PostgreSQL is running locally on port 5432, then run the synthetic seeder:
```bash
python database/seeds/dev_seed.py
```

#### 2. Start FastAPI Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Swagger API documentation will be available at `http://127.0.0.1:8000/api/v1/docs`.

#### 3. Start Next.js Authority Web App
```bash
cd apps/authority-web
npm install
npm run dev
```
Open `http://localhost:3000` in your browser.

#### 4. Run Flutter Mobile App
```bash
cd apps/personnel-mobile
flutter pub get
flutter run
```

---

## 7. Synthetic Development Demo Accounts

All credentials authenticate directly against the real FastAPI backend via `/api/v1/auth/login`:

| Role | Email Identifier | Password | Access Scope |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin@septeria.gov.in` | `SepteriaAdmin2026!` | Full administrative and security controls |
| **Commander** | `commander.bsf47@septeria.gov.in` | `Commander2026!` | Unit operational context & aggregate trends (BSF-47) |
| **Welfare Officer** | `welfare.crpf@septeria.gov.in` | `Welfare2026!` | Confidential welfare cases and recommendations |
| **Medical Officer** | `medical.itbp@septeria.gov.in` | `Medical2026!` | Health and physiological assessment context |
| **Personnel** | `personnel.crpf88219@septeria.gov.in` | `Personnel2026!` | Private personal recovery view & support requests |

*Note: All accounts and personnel identifiers are synthetic demo data.*

---

## 8. Running Automated Tests

### Backend Test Suite
```bash
python -m pytest backend/tests -v
```

### Flutter Test Suite
```bash
cd apps/personnel-mobile
flutter test
```

---

## 9. Regulatory & Ethical Boundaries
1. **Welfare-First Focus**: SEPTERIA provides predictive stress risk guidance and recommendations to human welfare officers. It does not replace clinical judgement.
2. **Not a Suicide Predictor**: The system does NOT claim deterministic suicide prediction or clinical psychiatric diagnosis (PTSD/Depression).
3. **Data Minimization**: Commanders view aggregate unit trends; raw medical/physiological data is strictly segregated under role-based authorization.
4. **Synthetic Data Integrity**: All prototype demonstrations use clearly marked synthetic/demo datasets.
