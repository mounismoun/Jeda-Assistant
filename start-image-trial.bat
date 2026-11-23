@echo off
setlocal
pushd "%~dp0" || exit /b 1
if not exist ".venv\Scripts\python.exe" (
    echo Run start-bot.bat once to install the bot environment.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" "tests\live\image_eval\trial-2026-11-22\run_candidate.py" %*
set "trial_status=%errorlevel%"
popd
if not "%trial_status%"=="0" pause
exit /b %trial_status%
