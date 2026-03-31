@echo off
title Import Equipment from Excel

echo.
echo  ============================================
echo   Import equipment from Excel into database
echo  ============================================
echo.

set PYTHON=C:\Users\Shutyuk\AppData\Local\Programs\Python\Python314\python.exe
if not exist "%PYTHON%" set PYTHON=C:\Users\Shutyuk\AppData\Local\Programs\Python\Python313\python.exe

if "%~1"=="" (
  echo  Drag and drop your Excel file onto this bat file,
  echo  OR place Excel file in this folder and run.
  echo.
  cd /d "%~dp0"
  "%PYTHON%" import_from_excel.py
) else (
  cd /d "%~dp0"
  "%PYTHON%" import_from_excel.py "%~1"
)
