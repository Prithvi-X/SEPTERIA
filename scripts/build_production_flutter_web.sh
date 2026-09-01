#!/usr/bin/env bash
# ==============================================================================
# SEPTERIA (SIH26186) - Production Flutter Web Build Script
# Usage: ./build_production_flutter_web.sh [BACKEND_API_URL]
# Example: ./build_production_flutter_web.sh https://septeria-backend.up.railway.app/api/v1
# ==============================================================================

set -e

API_URL=$1
if [ -z "$API_URL" ]; then
    echo "[ERROR] Please provide your deployed production backend API URL."
    echo "Usage: ./build_production_flutter_web.sh https://your-railway-app.up.railway.app/api/v1"
    exit 1
fi

echo "=============================================================================="
echo "Building SEPTERIA Personnel Web for Production"
echo "Target Backend API: ${API_URL}"
echo "=============================================================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}/../apps/personnel-mobile"

flutter clean
flutter build web --release --dart-define=API_BASE_URL="${API_URL}"

echo ""
echo "[SUCCESS] Production Flutter Web build completed in apps/personnel-mobile/build/web"
echo "Ready for static deployment to Vercel, Cloudflare Pages, Netlify, or S3."
