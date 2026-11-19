@echo off
setlocal
cd /d "%~dp0"
set PORT=8932
set PYTHONDONTWRITEBYTECODE=1
curl.exe --silent --fail --max-time 2 http://127.0.0.1:8932/health >nul
if not errorlevel 1 (
    start "" "http://127.0.0.1:8932/"
    exit /b 0
)
"..\review-repo\.review-python\python.exe" -X utf8 -c "import sys; sys.path.insert(0, '.'); from server import serve; serve(open_browser=True)"
if errorlevel 1 pause
