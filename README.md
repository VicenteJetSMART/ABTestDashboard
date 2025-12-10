## AB Test Dashboard - Streamlit

Aplicación de Streamlit para analizar experimentos de Amplitude (Jetsmart). Permite:
- Listar experimentos de Amplitude
- Ejecutar análisis diarios o acumulados por `experiment_id`, `device`, `culture` y `event_list`

### Requisitos
- Python 3.10+
- Archivo `.env` en la raíz del proyecto con credenciales de Amplitude.

Variables requeridas en `.env`:
```
AMPLITUDE_API_KEY=...
AMPLITUDE_SECRET_KEY=...
AMPLITUDE_MANAGEMENT_KEY=...
```

### Entorno virtual e instalación (Windows PowerShell)

Crea y activa el entorno virtual en la raíz del proyecto:

```powershell
# Crear entorno virtual (si no existe)
python -m venv venv

# Activar el entorno virtual
./venv/Scripts/Activate.ps1

# Actualizar pip e instalar dependencias
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Ejecutar la app

Con el entorno virtual activo, desde la raíz del proyecto:

```powershell
streamlit run app.py
```

### Estructura relevante
```
.
  app.py                    # App principal de Streamlit
  requirements.txt          # Dependencias
  utils/experiment_utils.py # Librería con lógica de Amplitude y pipelines
  metrics/                  # Métricas por step (baggage, seats, etc.)
  METRICS_GUIDE.md          # Guía para agregar métricas
  EXPERIMENT_UTILS_DOCUMENTATION.md # Docs técnicas de experiment_utils
```

### Cómo agregar nuevas métricas (resumen)
- Define las métricas en `metrics/<step>/<step>_metrics.py` siguiendo el ejemplo de `metrics/baggage/baggage_metrics.py`.
- Importa y añade las métricas al diccionario en `app.py` (sección de métricas predefinidas).
- Documenta la métrica en la tabla de "📚 Ver Métricas Disponibles".

Consulta la guía completa en `METRICS_GUIDE.md` y el ejemplo `EXAMPLE_SEATS_METRICS.py`.

### Troubleshooting
- Verifica que el `.env` esté en la raíz del proyecto.
- Asegúrate de activar el entorno virtual antes de ejecutar.
- Si faltan paquetes, ejecuta `pip install -r requirements.txt` desde la raíz del proyecto.
- Revisa la pestaña "❓ Ayuda" dentro de la app para parámetros y ejemplos.

### Actualizar el código desde GitHub

Si ya tienes el proyecto descargado y quieres obtener las últimas actualizaciones, sigue estos pasos:

#### Paso 1: Verificar que Git esté instalado

Abre PowerShell y ejecuta:
```powershell
git --version
```

Si ves un número de versión (ej: `git version 2.42.0`), Git está instalado. Si no, instálalo:

**Opción A - Usando winget (Windows 10/11):**
```powershell
winget install Git.Git
```

**Opción B - Descarga manual:**
1. Ve a https://git-scm.com/download/win
2. Descarga el instalador y ejecútalo
3. Acepta las opciones por defecto durante la instalación
4. Reinicia PowerShell después de instalar

#### Paso 2: Configurar Git (solo la primera vez)

Si es la primera vez que usas Git en esta computadora, configura tu nombre y email:

```powershell
git config --global user.name "Tu Nombre"
git config --global user.email "tu.email@jetsmart.com"
```

**Nota:** Estos datos solo se usan para identificar tus commits. No necesitas una cuenta de GitHub para actualizar el código.

#### Paso 3: Navegar a la carpeta del proyecto

Abre PowerShell y ve a la carpeta donde está el proyecto:

```powershell
cd "C:\ruta\a\tu\proyecto\limitless-dashboard-ab-test"
```

#### Paso 4: Verificar el estado actual

Antes de actualizar, verifica si tienes cambios locales sin guardar:

```powershell
git status
```

**Si ves "Your branch is up to date" y "nothing to commit":**
- ✅ Puedes continuar con el paso 5

**Si ves "Changes not staged for commit":**
- ⚠️ Tienes cambios locales que se perderán al actualizar
- Opción A: Guarda tus cambios en otro lugar antes de continuar
- Opción B: Si quieres descartar tus cambios locales y usar la versión del repositorio:
  ```powershell
  git restore .
  ```

#### Paso 5: Actualizar el código

Ejecuta el comando para descargar las últimas actualizaciones:

```powershell
git pull origin main
```

**Si todo sale bien, verás algo como:**
```
Updating a983114..223d23e
Fast-forward
 app.py | 400 ++++++++++++++++++++++++++++++++++++++++++++++++++++++++---
 1 file changed, 400 insertions(+)
```

**Si ves un error "fatal: not a git repository":**
- El proyecto no está conectado a Git
- Necesitas clonarlo desde cero (ver sección "Primera instalación" abajo)

**Si ves un error de "merge conflict":**
- Contacta al equipo técnico para ayuda

#### Paso 6: Actualizar dependencias (si es necesario)

Si se agregaron nuevas librerías, actualiza el entorno virtual:

```powershell
# Activar el entorno virtual
./venv/Scripts/Activate.ps1

# Actualizar dependencias
pip install -r requirements.txt
```

#### Paso 7: Reiniciar la aplicación

Si la aplicación estaba corriendo, deténla (Ctrl+C) y vuelve a ejecutarla:

```powershell
streamlit run app.py
```

---

### Primera instalación (si no tienes el proyecto)

Si es la primera vez que descargas el proyecto:

#### Paso 1: Instalar Git (si no lo tienes)

Sigue el **Paso 1** de la sección "Actualizar el código desde GitHub" arriba.

#### Paso 2: Clonar el repositorio

Abre PowerShell y navega a donde quieres guardar el proyecto:

```powershell
cd C:\Users\TuUsuario\Documentos
```

Luego clona el repositorio:

```powershell
git clone https://github.com/VicenteJetSMART/ABTestDashboard.git
```

Esto creará una carpeta llamada `ABTestDashboard` con todo el código.

#### Paso 3: Configurar el proyecto

Sigue las instrucciones de la sección "Entorno virtual e instalación" al inicio de este README.

#### Paso 4: Crear el archivo .env

Crea un archivo llamado `.env` en la raíz del proyecto con tus credenciales de Amplitude (obtén estas credenciales por privado del equipo):

```
AMPLITUDE_API_KEY=tu_api_key_aqui
AMPLITUDE_SECRET_KEY=tu_secret_key_aqui
AMPLITUDE_MANAGEMENT_KEY=tu_management_key_aqui
```

---

### Resumen rápido de comandos Git

```powershell
# Ver estado del proyecto
git status

# Actualizar código desde GitHub
git pull origin main

# Ver qué cambió en la última actualización
git log --oneline -5

# Descartar cambios locales y volver a la versión del repositorio
git restore .
```

---

### Licencia y soporte
- Uso interno Jetsmart. Para dudas técnicas, revisa `EXPERIMENT_UTILS_DOCUMENTATION.md`.
