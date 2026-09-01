#!/usr/bin/env python3
"""
SEPTERIA (SIH26186) - Pre-Deployment Security & Readiness Audit Script
Validates security invariants, dataset exclusion, model packaging, and configuration integrity before public cloud deployment.
"""

import os
import sys
import re

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def check_file_exists(rel_path: str, description: str) -> bool:
    full_path = os.path.join(ROOT_DIR, rel_path)
    exists = os.path.exists(full_path)
    status = "PASS" if exists else "FAIL"
    print(f"[{status}] {description} ({rel_path})")
    return exists

def check_file_contains(rel_path: str, pattern: str, description: str) -> bool:
    full_path = os.path.join(ROOT_DIR, rel_path)
    if not os.path.exists(full_path):
        print(f"[FAIL] File missing: {rel_path}")
        return False
    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    matches = re.search(pattern, content, re.MULTILINE)
    status = "PASS" if matches else "FAIL"
    print(f"[{status}] {description} in {rel_path}")
    return bool(matches)

def run_audit():
    print("=" * 80)
    print("SEPTERIA (SIH26186) - PRE-DEPLOYMENT SECURITY & READINESS AUDIT")
    print("=" * 80)
    print("")

    passed = True

    # 1. Dataset & Secret Exclusion in .gitignore
    print("--- 1. Git Ignore & Dataset Exclusion ---")
    passed &= check_file_contains(".gitignore", r"^Dataset", "Excludes raw Dataset folder")
    passed &= check_file_contains(".gitignore", r"^ml/data/processed", "Excludes processed training CSVs")
    passed &= check_file_contains(".gitignore", r"^\.env", "Excludes .env files")
    passed &= check_file_contains(".gitignore", r"septeria\.db", "Excludes local SQLite database")
    print("")

    # 2. Docker Build Context Isolation
    print("--- 2. Docker Context Isolation ---")
    passed &= check_file_contains(".dockerignore", r"^Dataset", "Docker ignores Dataset folder")
    passed &= check_file_contains(".dockerignore", r"^ml/data/", "Docker ignores ML training tables")
    passed &= check_file_contains(".dockerignore", r"^\.env\*", "Docker ignores .env files")
    passed &= check_file_contains(".dockerignore", r"^apps/", "Docker ignores frontend applications")
    print("")

    # 3. Model Weight Packaging
    print("--- 3. Production Model Packaging ---")
    passed &= check_file_exists("ml/models/xgboost_stress_model.joblib", "Trained XGBoost stress classifier (.joblib)")
    passed &= check_file_exists("ml/models/feature_preprocessor.joblib", "Feature schema preprocessor (.joblib)")
    passed &= check_file_contains("Dockerfile", r"COPY ml/models /app/ml/models", "Dockerfile copies ML models")
    passed &= check_file_contains("Dockerfile", r"\$\{PORT:-8000\}", "Dockerfile binds dynamically to $PORT")
    print("")

    # 4. Backend Cloud Settings ---
    print("--- 4. Backend Cloud Settings ---")
    passed &= check_file_contains("backend/app/core/config.py", r"PORT", "FastAPI reads dynamic $PORT")
    passed &= check_file_contains("backend/app/main.py", r"vercel", "CORS regex allows Vercel deployments")
    passed &= check_file_contains("railway.json", r"/api/v1/health", "Railway health check path configured")
    print("")

    # 5. Frontend Production Routing
    print("--- 5. Frontend Deployment Configurations ---")
    passed &= check_file_exists("apps/authority-web/vercel.json", "Authority Web Vercel configuration")
    passed &= check_file_exists("apps/authority-web/.env.production.example", "Authority Web production env template")
    passed &= check_file_exists("apps/personnel-mobile/vercel.json", "Personnel Mobile Vercel static configuration")
    passed &= check_file_exists("apps/personnel-mobile/.env.production.example", "Personnel Mobile production env template")
    passed &= check_file_contains("apps/personnel-mobile/lib/core/constants.dart", r"API_BASE_URL", "Flutter compile-time API_BASE_URL injection")
    passed &= check_file_exists("scripts/build_production_flutter_web.bat", "Flutter Web production Windows build script")
    passed &= check_file_exists("scripts/build_production_flutter_web.sh", "Flutter Web production Linux/macOS build script")
    print("")

    # 6. Sensitive Secrets Protection
    print("--- 6. Sensitive Secrets Protection ---")
    env_example_path = os.path.join(ROOT_DIR, ".env.production.example")
    with open(env_example_path, "r", encoding="utf-8") as f:
        env_ex_content = f.read()
    
    if "REPLACE_WITH_SECURE" in env_ex_content:
        print("[PASS] .env.production.example uses safe placeholder tokens")
    else:
        print("[FAIL] .env.production.example might contain real secrets")
        passed = False
    print("")

    print("=" * 80)
    if passed:
        print("AUDIT RESULT: ALL PRE-DEPLOYMENT SECURITY & INTEGRITY CHECKS PASSED")
        print("Repository is clean, isolated, and ready for public hosting.")
    else:
        print("AUDIT RESULT: SOME CHECKS FAILED. Please review the output above.")
    print("=" * 80)
    return passed

if __name__ == "__main__":
    success = run_audit()
    sys.exit(0 if success else 1)
