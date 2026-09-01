@echo off
REM ==============================================================================
REM SEPTERIA (SIH26186) - Production Flutter Web Build Script
REM Usage: build_production_flutter_web.bat [BACKEND_API_URL]
REM Example: build_production_flutter_web.bat https://septeria-backend.up.railway.app/api/v1
REM ==============================================================================

set API_URL=%1
if "%API_URL%"=="" (
    echo [ERROR] Please provide your deployed production backend API URL.
    echo Usage: build_production_flutter_web.bat https://your-railway-app.up.railway.app/api/v1
    exit /b 1
)

echo ==============================================================================
echo Building SEPTERIA Personnel Web for Production
echo Target Backend API: %API_URL%
echo ==============================================================================

cd /d "%~dp0\..\apps\personnel-mobile"
flutter clean
flutter build web --release --dart-define=API_BASE_URL=%API_URL%

if %ERRORLEVEL% equ 0 (
    echo.
    echo [SUCCESS] Production Flutter Web build completed in apps/personnel-mobile/build/web
    echo Ready for static deployment to Vercel, Cloudflare Pages, Netlify, or S3.
) else (
    echo.
    echo [ERROR] Flutter build failed.
    exit /b %ERRORLEVEL%
)
