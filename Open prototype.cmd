@echo off
setlocal
cd /d "%~dp0"
set PORT=8953
set PYTHONDONTWRITEBYTECODE=1
curl.exe --silent --fail --max-time 2 http://127.0.0.1:%PORT%/health >nul
if not errorlevel 1 (
    start "" "http://127.0.0.1:%PORT%/"
    exit /b 0
)
set "YEONYEON_PYTHON=..\yeonyeon-evidence-preview\.local-runtime\python\python.exe"
if not exist "%YEONYEON_PYTHON%" set "YEONYEON_PYTHON=..\review-repo\.review-python\python.exe"
"%YEONYEON_PYTHON%" -B -X utf8 -c "import sys; sys.path.insert(0, '.'); from server import serve; serve(open_browser=True)"
if errorlevel 1 pause
