@echo off
setlocal enabledelayedexpansion
REM ============================================
REM Script para finalizar el AB Test Dashboard
REM ============================================

echo.
echo ============================================
echo   AB Test Dashboard - Finalizando...
echo ============================================
echo.

REM Cambiar al directorio del script
cd /d "%~dp0"

REM Buscar procesos de Streamlit en el puerto 8501
set FOUND=0

for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8501" ^| findstr "LISTENING"') do (
    set PID=%%a
    set FOUND=1
    echo [INFO] Proceso encontrado en puerto 8501 con PID: %%a
    echo [INFO] Finalizando proceso...
    taskkill /PID %%a /F >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] No se pudo finalizar el proceso %%a
    ) else (
        echo [OK] Proceso %%a finalizado correctamente
    )
)

REM También buscar procesos de Python ejecutando streamlit
for /f "tokens=2" %%a in ('tasklist /FI "IMAGENAME eq python.exe" /FO CSV ^| findstr /V "INFO:"') do (
    set "PID_VAR=%%a"
    set "PID_VAR=!PID_VAR:"=!"
    wmic process where "ProcessId=!PID_VAR!" get CommandLine 2>nul | findstr /i "streamlit" >nul
    if not errorlevel 1 (
        echo [INFO] Proceso de Streamlit encontrado con PID: !PID_VAR!
        echo [INFO] Finalizando proceso...
        taskkill /PID !PID_VAR! /F >nul 2>&1
        if errorlevel 1 (
            echo [ERROR] No se pudo finalizar el proceso !PID_VAR!
        ) else (
            echo [OK] Proceso !PID_VAR! finalizado correctamente
            set FOUND=1
        )
    )
)

REM Intentar leer el PID guardado si existe
if exist "streamlit_pid.txt" (
    set /p SAVED_PID=<streamlit_pid.txt
    if defined SAVED_PID (
        echo [INFO] Intentando finalizar proceso guardado: !SAVED_PID!
        taskkill /PID !SAVED_PID! /F >nul 2>&1
        if not errorlevel 1 (
            echo [OK] Proceso guardado finalizado correctamente
            set FOUND=1
        )
        del streamlit_pid.txt >nul 2>&1
    )
)

if !FOUND!==0 (
    echo [INFO] No se encontro ninguna instancia de la aplicacion corriendo
) else (
    echo.
    echo [OK] Aplicacion finalizada correctamente
)

echo.
pause

