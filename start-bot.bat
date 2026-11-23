@echo off
setlocal EnableExtensions DisableDelayedExpansion
chcp 65001 >nul
title Jeda Assistant
pushd "%~dp0" || goto :failed

set "bot_python=.venv\Scripts\python.exe"
if exist "%bot_python%" goto :dependencies

set "bootstrap=py -3"
%bootstrap% -c "import sys; sys.exit(sys.version_info < (3, 12))" >nul 2>&1
if not errorlevel 1 goto :create_env
set "bootstrap=python"
%bootstrap% -c "import sys; sys.exit(sys.version_info < (3, 12))" >nul 2>&1
if not errorlevel 1 goto :create_env
echo Python 3.12 이상을 설치한 뒤 이 파일을 다시 실행하세요.
goto :failed

:create_env
echo 봇 전용 Python 환경을 준비합니다.
%bootstrap% -m venv .venv
if errorlevel 1 goto :failed

:dependencies
if not exist ".venv\Scripts\assistant-bot.exe" goto :install
fc /b pyproject.toml ".venv\installed-pyproject.toml" >nul 2>&1
if not errorlevel 1 goto :run

:install
echo 봇 실행에 필요한 패키지를 설치합니다.
"%bot_python%" -m pip install -e .
if errorlevel 1 goto :failed
copy /y /b pyproject.toml ".venv\installed-pyproject.toml" >nul
if errorlevel 1 goto :failed

:run
echo Discord 봇을 시작합니다. 종료하려면 이 창에서 Ctrl+C를 누르세요.
echo 로컬 상태 관리창은 봇 시작 후 http://127.0.0.1:8766/ 에서 열 수 있습니다.
"%bot_python%" -m assistant_bot.main
if errorlevel 1 goto :failed
popd
exit /b 0

:failed
echo 실행을 마치지 못했습니다. 위의 오류 메시지를 확인하세요.
pause
exit /b 1
