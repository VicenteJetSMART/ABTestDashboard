@echo off
setlocal enabledelayedexpansion
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
set VENV_FOUND=0
if exist "venv\Scripts\python.exe" (
    set VENV_FOUND=1
    set VENV_PYTHON=venv\Scripts\python.exe
) else if exist "%CD%\venv\Scripts\python.exe" (
    set VENV_FOUND=1
    set VENV_PYTHON=%CD%\venv\Scripts\python.exe
)

if !VENV_FOUND!==0 (
    echo [ERROR] No se encontro el entorno virtual (venv)
    echo [DEBUG] Directorio actual: %CD%
    echo [DEBUG] Buscando en: %CD%\venv\Scripts\python.exe
    echo.
    echo [INFO] El entorno virtual no existe. ¿Deseas crearlo ahora?
    echo [INFO] Esto instalara Python y creara el entorno virtual automaticamente.
    echo.
    set /p CREATE_VENV="Crear entorno virtual? (S/N): "
    if /i "!CREATE_VENV!"=="S" (
        echo.
        echo [INFO] Verificando Python instalado...
        python --version >nul 2>&1
        if errorlevel 1 (
            echo [ERROR] Python no esta instalado o no esta en el PATH
            echo [ERROR] Por favor, instala Python desde https://www.python.org/
            echo.
            pause
            exit /b 1
        )
        
        echo [INFO] Creando entorno virtual...
        python -m venv venv
        if errorlevel 1 (
            echo [ERROR] Error al crear el entorno virtual
            echo.
            pause
            exit /b 1
        )
        
        echo [INFO] Entorno virtual creado correctamente
        echo [INFO] Instalando dependencias...
        call venv\Scripts\activate.bat
        venv\Scripts\python.exe -m pip install --upgrade pip
        venv\Scripts\python.exe -m pip install -r requirements.txt
        if errorlevel 1 (
            echo [ERROR] Error al instalar dependencias
            echo.
            pause
            exit /b 1
        )
        echo [OK] Entorno virtual configurado correctamente
        set VENV_PYTHON=venv\Scripts\python.exe
    ) else (
        echo [INFO] Saliendo. Crea el entorno virtual manualmente con:
        echo        python -m venv venv
        echo        venv\Scripts\activate
        echo        pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )
) else (
    echo [OK] Entorno virtual encontrado: !VENV_PYTHON!
)

REM Verificar que existe app.py
if not exist "app.py" (
    echo [ERROR] No se encontro el archivo app.py
    echo.
    pause
    exit /b 1
)

REM Verificar si la aplicación ya está corriendo
for /f "tokens=2" %%a in ('netstat -ano ^| findstr ":8501" ^| findstr "LISTENING"') do (
    echo [ADVERTENCIA] La aplicacion ya esta corriendo en el puerto 8501
    echo [INFO] Usa "finalizar_app.bat" para detenerla primero
    echo.
    pause
    exit /b 1
)

echo [INFO] Verificando dependencias...
!VENV_PYTHON! -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Instalando dependencias...
    !VENV_PYTHON! -m pip install -r requirements.txt
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
echo O ejecuta "finalizar_app.bat" desde otra ventana
echo.

REM Iniciar Streamlit
!VENV_PYTHON! -m streamlit run app.py

REM Si se cierra la aplicacion, mantener la ventana abierta
echo.
echo [INFO] La aplicacion se ha cerrado.
pause
