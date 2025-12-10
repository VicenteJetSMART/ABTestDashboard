# Script para subir el repositorio a GitHub de forma segura

Write-Host "=== Verificando Git ===" -ForegroundColor Cyan

# Buscar Git en ubicaciones comunes
$gitLocations = @(
    "C:\Program Files\Git\cmd\git.exe",
    "C:\Program Files (x86)\Git\cmd\git.exe",
    "$env:LOCALAPPDATA\Programs\Git\cmd\git.exe",
    "$env:ProgramFiles\Git\cmd\git.exe",
    "$env:ProgramFiles(x86)\Git\cmd\git.exe",
    "C:\Program Files\Git\bin\git.exe"
)

$gitExe = $null
foreach ($loc in $gitLocations) {
    if (Test-Path $loc) {
        $gitExe = $loc
        Write-Host "✅ Git encontrado en: $loc" -ForegroundColor Green
        break
    }
}

# Intentar con git directamente si está en PATH
if (-not $gitExe) {
    try {
        $null = git --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $gitExe = "git"
            Write-Host "✅ Git encontrado en PATH" -ForegroundColor Green
        }
    } catch {
        Write-Host "❌ Git no encontrado. Por favor, instala Git desde: https://git-scm.com/download/win" -ForegroundColor Red
        exit 1
    }
}

if (-not $gitExe) {
    Write-Host "❌ Git no encontrado. Por favor, instala Git o agrégalo al PATH." -ForegroundColor Red
    exit 1
}

Write-Host "`n=== Verificando estado del repositorio ===" -ForegroundColor Cyan

# Verificar que .env NO está siendo rastreado
Write-Host "Verificando que .env NO está siendo rastreado..." -ForegroundColor Yellow
$null = & $gitExe ls-files .env 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "⚠️  ADVERTENCIA: .env está siendo rastreado. Eliminándolo del índice..." -ForegroundColor Red
    & $gitExe rm --cached .env
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Error al eliminar .env del índice" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ .env eliminado del índice" -ForegroundColor Green
} else {
    Write-Host "✅ .env NO está siendo rastreado" -ForegroundColor Green
}

# Mostrar estado actual
Write-Host "`nEstado actual de Git:" -ForegroundColor Cyan
& $gitExe status --short

# Verificar remote
Write-Host "`n=== Verificando repositorio remoto ===" -ForegroundColor Cyan
$remoteUrl = & $gitExe remote get-url origin 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Remote configurado: $remoteUrl" -ForegroundColor Green
} else {
    Write-Host "⚠️  No hay remote configurado" -ForegroundColor Yellow
}

Write-Host "`n=== Agregando archivos ===" -ForegroundColor Cyan
& $gitExe add .
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error al agregar archivos" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Archivos agregados" -ForegroundColor Green

# Verificar qué se va a subir
Write-Host "`nArchivos que se van a subir:" -ForegroundColor Cyan
& $gitExe status --short

# Verificar que .env NO está en la lista
$statusOutput = & $gitExe status --short 2>&1 | Out-String
if ($statusOutput -match '\.env[^a-zA-Z]' -and $statusOutput -notmatch '\.env\.example') {
    Write-Host "`n⚠️  ADVERTENCIA: .env aparece en los cambios. Por favor, verifica manualmente." -ForegroundColor Red
    Write-Host "Ejecuta: git rm --cached .env" -ForegroundColor Yellow
    exit 1
}

Write-Host "`n=== ¿Deseas continuar con el commit y push? ===" -ForegroundColor Cyan
Write-Host "Presiona Enter para continuar o Ctrl+C para cancelar..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Write-Host "`n=== Haciendo commit ===" -ForegroundColor Cyan
$commitMessage = "Initial commit: AB Test Dashboard con filtros avanzados y precision horaria"
& $gitExe commit -m $commitMessage
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error al hacer commit" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Commit realizado" -ForegroundColor Green

Write-Host "`n=== Haciendo push ===" -ForegroundColor Cyan
& $gitExe push -u origin main
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Error al hacer push. Intentando con 'master'..." -ForegroundColor Yellow
    & $gitExe push -u origin master
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Error al hacer push. Verifica que el repositorio existe y tienes permisos." -ForegroundColor Red
        exit 1
    }
}
Write-Host "✅ Push completado exitosamente!" -ForegroundColor Green

Write-Host "`n=== Verificación final ===" -ForegroundColor Cyan
Write-Host "Repositorio: $remoteUrl" -ForegroundColor White
Write-Host "✅ El dashboard ha sido subido a GitHub de forma segura" -ForegroundColor Green

