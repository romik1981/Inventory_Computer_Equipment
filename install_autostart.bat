@echo off
title Install AutoStart

echo.
echo  Installing CartridgeApp to autostart on Windows login...
echo.

set APPDIR=%~dp0
set TASKNAME=CartridgeApp

set PYTHON=
if exist "C:\Users\Shutyuk\AppData\Local\Programs\Python\Python314\python.exe" (
  set PYTHON=C:\Users\Shutyuk\AppData\Local\Programs\Python\Python314\python.exe
  goto :found
)
for %%V in (Python314 Python313 Python312 Python311 Python310) do (
  if exist "%LOCALAPPDATA%\Programs\Python\%%V\python.exe" (
    set PYTHON=%LOCALAPPDATA%\Programs\Python\%%V\python.exe
    goto :found
  )
)
py --version >nul 2>&1
if not errorlevel 1 ( set PYTHON=py && goto :found )
python --version >nul 2>&1
if not errorlevel 1 ( set PYTHON=python && goto :found )
echo [ERROR] Python not found
pause & exit /b 1

:found
echo  Python: %PYTHON%

REM Create scheduled task to run on system startup
schtasks /create /tn "%TASKNAME%" /tr "\"%PYTHON%\" \"%APPDIR%app.py\"" /sc onlogon /ru "%USERNAME%" /f >nul 2>&1

if errorlevel 1 (
  echo  [ERROR] Could not create scheduled task. Try running as Administrator.
  pause
  exit /b 1
)

echo.
echo  Done! CartridgeApp will start automatically on Windows login.
echo  Users can access it at: http://SERVER-IP:5000
echo.
echo  To remove autostart, run: schtasks /delete /tn CartridgeApp /f
echo.
pause
