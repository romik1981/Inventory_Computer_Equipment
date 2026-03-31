@echo off
title CartridgeApp

echo.
echo  CartridgeApp - starting...
echo.

set PYTHON=

for %%V in (Python314 Python313 Python312 Python311 Python310 Python39) do (
  if exist "%LOCALAPPDATA%\Programs\Python\%%V\python.exe" (
    set PYTHON=%LOCALAPPDATA%\Programs\Python\%%V\python.exe
    goto :found
  )
)
py --version >nul 2>&1
if not errorlevel 1 ( set PYTHON=py && goto :found )
python --version >nul 2>&1
if not errorlevel 1 ( set PYTHON=python && goto :found )

echo  [ERROR] Python not found! Install Python 3.9+ from https://python.org
pause
exit /b 1

:found
echo  Python: %PYTHON%
"%PYTHON%" --version
echo.

echo  Checking Flask...
"%PYTHON%" -c "import flask" >nul 2>&1
if not errorlevel 1 goto :flask_ok

echo  Installing dependencies...
"%PYTHON%" -m pip install -r requirements.txt
if errorlevel 1 (
  echo  [ERROR] Failed to install dependencies.
  pause
  exit /b 1
)

:flask_ok
echo  Flask: OK
echo.

echo  ============================================
echo   Server is running!
echo.
echo   Open browser: http://localhost:5000
echo.
echo   Login:    admin
echo   Password: admin123
echo.
echo   Change password after first login!
echo   To stop: close this window or Ctrl+C
echo  ============================================
echo.

cd /d "%~dp0"
"%PYTHON%" app.py
if errorlevel 1 (
  echo.
  echo  [ERROR] App crashed. See error above.
  pause
)

echo.
echo  Server stopped.
pause
