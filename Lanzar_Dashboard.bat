@echo off
setlocal enabledelayedexpansion
REM ============================================
REM Lanzador del AB Test Dashboard
REM Funciona desde cualquier ubicación (Escritorio, carpeta del proyecto, etc.)
REM ============================================

REM Establecer el directorio de trabajo en la ubicación del script
cd /d "%~dp0"

REM ============================================
REM Verificación del Entorno Virtual
REM ============================================
set VENV_PYTHON=
set VENV_FOUND=0

REM Buscar entorno virtual en ubicaciones estándar
if exist "venv\Scripts\python.exe" (
    set VENV_PYTHON=venv\Scripts\python.exe
    set VENV_FOUND=1
) else if exist ".venv\Scripts\python.exe" (
    set VENV_PYTHON=.venv\Scripts\python.exe
    set VENV_FOUND=1
) else if exist "env\Scripts\python.exe" (
    set VENV_PYTHON=env\Scripts\python.exe
    set VENV_FOUND=1
)

if !VENV_FOUND!==0 (
    echo.
    echo [ERROR] No se encontro el entorno virtual
    echo [INFO] Directorio actual: %CD%
    echo [INFO] Buscando en: venv, .venv, env
    echo.
    echo [SOLUCION] Crea el entorno virtual ejecutando:
    echo            python -m venv venv
    echo            venv\Scripts\activate
    echo            pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM ============================================
REM Verificación de app.py
REM ============================================
if not exist "app.py" (
    echo.
    echo [ERROR] No se encontro el archivo app.py
    echo [INFO] Directorio actual: %CD%
    echo.
    pause
    exit /b 1
)

REM ============================================
REM Verificación de Dependencias
REM ============================================
echo.
echo [INFO] Verificando dependencias...
!VENV_PYTHON! -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Streamlit no encontrado. Instalando dependencias...
    !VENV_PYTHON! -m pip install --upgrade pip >nul 2>&1
    !VENV_PYTHON! -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Error al instalar dependencias
        echo.
        pause
        exit /b 1
    )
    echo [OK] Dependencias instaladas correctamente
)

REM ============================================
REM Verificación de Puerto Ocupado
REM ============================================
for /f "tokens=2" %%a in ('netstat -ano ^| findstr ":8501" ^| findstr "LISTENING"') do (
    echo.
    echo [ADVERTENCIA] El puerto 8501 ya esta en uso
    echo [INFO] La aplicacion puede estar corriendo en otra ventana
    echo [INFO] Usa "finalizar_app.bat" para detenerla primero
    echo.
    set /p CONTINUE="¿Deseas continuar de todas formas? (S/N): "
    if /i not "!CONTINUE!"=="S" (
        exit /b 1
    )
)

REM ============================================
REM Iniciar Streamlit
REM ============================================
echo.
echo ============================================
echo   AB Test Dashboard - Iniciando...
echo ============================================
echo.
echo [INFO] Entorno virtual: !VENV_PYTHON!
echo [INFO] La aplicacion se abrira en: http://localhost:8501
echo.
echo Presiona Ctrl+C para detener la aplicacion
echo.
echo ============================================
echo.

REM Ejecutar Streamlit con configuración optimizada
!VENV_PYTHON! -m streamlit run app.py --browser.gatherUsageStats false

REM Si hay un error, mantener la ventana abierta
if errorlevel 1 (
    echo.
    echo [ERROR] La aplicacion se cerro con un error
    echo.
    pause
    exit /b 1
)

REM Si se cierra normalmente, mantener la ventana abierta
echo.
echo [INFO] La aplicacion se ha cerrado.
pause

