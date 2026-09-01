# SEPTERIA (SIH26186) — Master Production Deployment Guide

**Target Architecture:**
1. **Backend & Machine Learning Engine:** Railway (Docker / Python 3.11 / FastAPI)
2. **Production Database:** Railway Managed PostgreSQL 16
3. **Authority Web Portal:** Vercel (Next.js 15)
4. **Uniformed Forces Personnel App:** Vercel / Cloudflare Pages / Static Hosting (Flutter Web)

---

## Part A: GitHub Repository Preparation

### 1. Dataset & Secret Exclusion Guarantee
Before pushing your repository to GitHub, verify that heavy training datasets and secrets are excluded while the trained XGBoost model files are preserved:

- **Strictly Excluded from Git:**
  - `Dataset/` (All raw public datasets: WESAD, PhysioNet, SWELL-KW, CATSA)
  - `ml/data/processed/` (Intermediate training CSV tables)
  - `septeria.db` & `*.sqlite` (Local development databases)
  - `.env`, `.env.local`, `.env.*.local` (Local secrets)
- **Strictly Included in Git:**
  - `ml/models/xgboost_stress_model.joblib` (Trained model weights)
  - `ml/models/feature_preprocessor.joblib` (Standardization scaler & schema metadata)
  - `Dockerfile`, `railway.json`, `apps/authority-web/vercel.json`, `apps/personnel-mobile/vercel.json`

### 2. Run Pre-Deployment Security Audit
Execute the automated security and isolation verification script:
```bash
python scripts/pre_deployment_security_check.py
```
Ensure all checks output `[PASS]`.

### 3. Push to GitHub
```bash
git add .
git commit -m "chore: prepare production deployment configuration for Railway and Vercel"
git branch -M main
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/septeria-prototype.git
git push -u origin main
```

---

## Part B: Railway PostgreSQL Database Provisioning

1. Log in to [Railway.app](https://railway.app).
2. Click **"New Project"** -> Select **"Provision PostgreSQL"**.
3. Once the database is created, click on the **PostgreSQL** card -> Go to **"Variables"** or **"Connect"**.
4. Railway automatically generates and provides the environment variable `DATABASE_URL`:
   ```text
   postgresql://postgres:PASSWORD@roundhouse.proxy.rlwy.net:PORT/railway
   ```
   *(Keep this tab open; Railway will automatically link this variable to your FastAPI backend service).*

---

## Part C: Railway FastAPI Backend Deployment

### 1. Deploy the Backend Service
1. In your Railway project dashboard, click **"+ New"** -> Select **"GitHub Repo"** -> Select your `septeria-prototype` repository.
2. Railway detects `Dockerfile` and `railway.json` automatically in the root of the repository.

### 2. Configure Railway Backend Environment Variables
In the Railway dashboard for the backend service, go to **"Variables"** and add:

| Variable Name | Production Value / Description | Example |
| :--- | :--- | :--- |
| `APP_ENV` | `production` | `production` |
| `PROJECT_NAME` | `SEPTERIA (SIH26186)` | `SEPTERIA (SIH26186)` |
| `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` | *(Reference Railway Postgres variable)* |
| `JWT_SECRET` | Strong 256-bit secret key | `$(openssl rand -hex 32)` |
| `JWT_ALGORITHM` | `HS256` | `HS256` |
| `JWT_EXPIRY_MINUTES` | `480` | `480` |
| `CORS_ORIGINS` | Comma-separated list of your Vercel domains | `https://septeria-authority.vercel.app,https://septeria-personnel.vercel.app` |

*(Note: `PORT` is dynamically injected by Railway; FastAPI binds to `0.0.0.0:${PORT}` automatically).*

### 3. Generate Public Domain for Backend
1. Go to **"Settings"** -> **"Networking"** -> Click **"Generate Domain"**.
2. Railway will assign a public domain, for example:
   ```text
   https://septeria-backend-production.up.railway.app
   ```
3. Your live API base URL will be:
   ```text
   https://septeria-backend-production.up.railway.app/api/v1
   ```

---

## Part D: Vercel Authority Web Portal Deployment

1. Log in to [Vercel.com](https://vercel.com).
2. Click **"Add New..."** -> **"Project"** -> Import your GitHub repository `septeria-prototype`.
3. Configure the project settings:
   - **Framework Preset:** `Next.js`
   - **Root Directory:** Click **Edit** and select **`apps/authority-web`**.
   - **Build Command:** `next build` (default)
   - **Output Directory:** `.next` (default)
4. Under **"Environment Variables"**, add:
   - **Name:** `NEXT_PUBLIC_API_BASE_URL`
   - **Value:** `https://septeria-backend-production.up.railway.app/api/v1` *(Replace with your actual Railway backend URL)*
   - **Name:** `NEXT_PUBLIC_ENABLE_DEV_AUTH_QUICKFILL`
   - **Value:** `true` *(Enables demonstration quick-fill buttons for jury presentation)*
5. Click **"Deploy"**.
6. Vercel will build and assign your live production URL (e.g. `https://septeria-authority.vercel.app`).

---

## Part E: Uniformed Forces Personnel Web App Deployment

You can deploy the compiled Flutter Web application to Vercel, Cloudflare Pages, or Netlify:

### Method 1: Local Build & Deploy to Vercel CLI (Recommended)

1. Build the production Flutter Web bundle injecting your live Railway API URL:
   ```bash
   # On Windows:
   scripts\build_production_flutter_web.bat https://septeria-backend-production.up.railway.app/api/v1

   # On Linux/macOS:
   chmod +x scripts/build_production_flutter_web.sh
   ./scripts/build_production_flutter_web.sh https://septeria-backend-production.up.railway.app/api/v1
   ```
2. Navigate into the mobile app directory and deploy `build/web` to Vercel:
   ```bash
   cd apps/personnel-mobile
   npx vercel deploy --prod build/web
   ```

### Method 2: Git-Integrated Vercel Project
1. In Vercel, create a new project importing `septeria-prototype`.
2. Set **Root Directory** to `apps/personnel-mobile`.
3. Set **Output Directory** to `build/web`.
4. Deploy the pre-built web bundle.

---

## Part F: Production Environment Variables Reference

```ini
# ==============================================================================
# Master Production Configuration Reference
# ==============================================================================

# Backend (Railway)
APP_ENV=production
PROJECT_NAME="SEPTERIA (SIH26186)"
DATABASE_URL=postgresql+psycopg2://postgres:<password>@<host>:<port>/railway
JWT_SECRET=REPLACE_WITH_SECURE_256BIT_HEX_SECRET
JWT_ALGORITHM=HS256
JWT_EXPIRY_MINUTES=480
CORS_ORIGINS=https://septeria-authority.vercel.app,https://septeria-personnel.vercel.app

# Authority Web (Vercel)
NEXT_PUBLIC_API_BASE_URL=https://septeria-backend-production.up.railway.app/api/v1
NEXT_PUBLIC_ENABLE_DEV_AUTH_QUICKFILL=true

# Personnel Mobile (Flutter Web compile-time injection)
API_BASE_URL=https://septeria-backend-production.up.railway.app/api/v1
```

---

## Part G: CORS Architecture & Regex Validation

The backend FastAPI server utilizes multi-origin regex defense in [`backend/app/main.py`](file:///d:/IITM/SIH/PROTOTYPE/ANTIGRAVITY/ANTI-INFO/backend/app/main.py#L74):
```python
allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1|.*\.vercel\.app|.*\.rlwy\.net|.*\.railway\.app)(:[0-9]+)?$"
```
- **Local Developer Testing:** Supports all ports on `localhost` and `127.0.0.1` (`3000`, `3001`, `8080`, `5000`, `5173`).
- **Cloud Preview Deployments:** Any Vercel preview or production domain (`https://*-yourusername.vercel.app`) is automatically allowed.
- **Custom Domains:** Additional domains can be passed dynamically via the `CORS_ORIGINS` environment variable.

---

## Part H: Automated Database Migration & Seeding

On every cold start, the FastAPI lifespan event automatically:
1. Creates all missing PostgreSQL relational tables (`Base.metadata.create_all(bind=engine)`).
2. Checks and seeds standard demonstration accounts with hashed passwords:

| Role | Production Demo Email | Password | Scope |
| :--- | :--- | :--- | :--- |
| **Welfare / Medical** | `welfare@septeria.gov.in` | `Welfare@1234` | Medical Triage (`/welfare`) |
| **Commander** | `commander@septeria.gov.in` | `Commander@1234` | Platoon Readiness (`/analytics`) |
| **Admin** | `admin@septeria.gov.in` | `Admin@1234` | System & Demo Controls (`/dashboard`) |
| **Soldier (Jawan)** | `soldier@septeria.gov.in` | `Rajesh@1234` | Personnel Self-Service App |

---

## Part I: Health Checks & Graceful Degradation

Verify the live backend health endpoints:

1. **Liveness & Readiness Probe:**
   ```bash
   curl -s https://septeria-backend-production.up.railway.app/api/v1/health
   ```
   *Expected Response:* `{"status": "ok", "app": "SEPTERIA API", "environment": "production"}`

2. **Full Multi-Subsystem Health Audit:**
   ```bash
   curl -s https://septeria-backend-production.up.railway.app/api/v1/system/health-audit
   ```
   *Expected Response:*
   ```json
   {
     "system_name": "SEPTERIA",
     "project_code": "SIH26186",
     "overall_status": "OPERATIONAL",
     "mode": "SYNTHETIC_DEMONSTRATION_MODE",
     "claim_boundaries": {
       "clinical_diagnostic_claim": false,
       "suicide_prediction_claim": false,
       "capf_field_validation_claim": false,
       "purpose": "Non-punitive AI decision-support for personnel welfare and recovery."
     },
     "components": {
       "database": {"status": "OPERATIONAL", "type": "PostgreSQL"},
       "ml_model_engine": {"status": "OPERATIONAL", "model": "XGBoost Stress Classifier v1.0.0"},
       "tri_layer_engine": {"status": "OPERATIONAL", "version": "v1.2.0-Configurable"},
       "contextual_graph": {"status": "OPERATIONAL", "graph_engine": "NetworkX + Graph Cache"},
       "voice_intelligence": {"status": "OPERATIONAL", "features": "Librosa PYIN + MFCC Stats", "privacy": "Strict Discard"},
       "edge_adapters": {"status": "OPERATIONAL", "adapters": ["Synthetic", "BLE-GATT", "HealthConnect"]},
       "offline_sync_queue": {"status": "OPERATIONAL", "deduplication": "SHA-256 Idempotency"}
     }
   }
   ```

---

## Part J: Final End-to-End Live Verification Checklist

Once all services are deployed, perform the final 10-point verification:

- [ ] **1. Swagger API Docs Active:** Navigate to `https://<YOUR_RAILWAY_URL>/api/v1/docs` and confirm documentation loads.
- [ ] **2. Authority Web Loads:** Open `https://<YOUR_VERCEL_AUTHORITY_URL>` in an incognito window.
- [ ] **3. Commander Login & Privacy Check:** Log in with `commander@septeria.gov.in` / `Commander@1234` -> Confirm cluster alert `PAT-BSF-BN-47-ZONE_2-Night-1` is visible and zero individual biometrics are exposed.
- [ ] **4. Medical & Welfare Review:** Log in with `welfare@septeria.gov.in` / `Welfare@1234` -> Confirm 5-stream multimodal evidence gauges, SHAP waterfall, and recovery recommendations load.
- [ ] **5. System Audit Modal:** Click "Audit Subsystems" in the top bar -> Confirm all 7 components report `OPERATIONAL`.
- [ ] **6. Reset Demo State:** Click "Demo State Controller" -> "Reset Demo State" -> Confirm clean baseline restored.
- [ ] **7. Personnel Mobile App Loads:** Open `https://<YOUR_VERCEL_PERSONNEL_URL>` in browser.
- [ ] **8. Jawan Authentication:** Log in with `soldier@septeria.gov.in` / `Rajesh@1234`.
- [ ] **9. Soldier Personal Recovery:** Confirm personal recovery burden score ($78\%$), $4.5\text{h}$ sleep debt, and plain-language explanation are displayed.
- [ ] **10. 10-Second Voice Check-In:** Tap the microphone icon -> Trigger voluntary check-in -> Confirm acoustic pitch shifts are processed in-memory and zero audio is persisted.
