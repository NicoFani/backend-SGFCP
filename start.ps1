# Script de inicio para Windows PowerShell que configura encoding UTF-8
# Uso: .\start.ps1

Write-Host "🔧 Configurando entorno UTF-8..." -ForegroundColor Cyan

# Establecer encoding UTF-8 para Python
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"

# Desactivar el passfile de PostgreSQL que puede causar problemas de encoding
$env:PGPASSFILE = ""

# Limpiar variables que puedan tener caracteres problemáticos
$env:LANG = "en_US.UTF-8"
$env:LC_ALL = "en_US.UTF-8"

Write-Host "✅ Variables de entorno configuradas" -ForegroundColor Green
Write-Host "🚀 Iniciando servidor Flask..." -ForegroundColor Cyan
Write-Host ""

# Ejecutar el servidor
python run.py
