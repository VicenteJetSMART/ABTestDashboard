@echo off
REM ============================================
REM Script para iniciar el AB Test Dashboard
REM ============================================

echo.
echo ============================================
echo   AB Test Dashboard - Iniciando...
echo ============================================
echo.

REM Cambiar al directorio del script
cd /d "%~dp0"

REM Verificar que existe el entorno virtual
if not exist "venv\Scripts\python.exe" (
    echo [ERROR] No se encontro el entorno virtual (venv)
    echo Por favor, asegurate de que el entorno virtual este creado.
    echo.
    pause
    exit /b 1
)

REM Verificar que existe app.py
if not exist "app.py" (
    echo [ERROR] No se encontro el archivo app.py
    echo.
    pause
    exit /b 1
)

echo [INFO] Verificando dependencias...
venv\Scripts\python.exe -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Instalando dependencias...
    venv\Scripts\python.exe -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Error al instalar dependencias
        pause
        exit /b 1
    )
)

echo.
echo [INFO] Iniciando Streamlit...
echo [INFO] La aplicacion se abrira en: http://localhost:8501
echo.
echo Presiona Ctrl+C para detener la aplicacion
echo.

REM Iniciar Streamlit
venv\Scripts\python.exe -m streamlit run app.py

REM Si se cierra la aplicacion, mantener la ventana abierta
echo.
echo [INFO] La aplicacion se ha cerrado.
pause

