# ===============================================
# PowerShell script to restart LabREI Docker stack
# Stops previous containers and brings up updated ones
# ===============================================

# Move to the script's directory (project root)
Set-Location -Path $PSScriptRoot

Write-Host "`n== Shutting down previous Docker Compose stack ==" -ForegroundColor Yellow
docker-compose down

Write-Host "`n== Building updated Docker images (no build cache) ==" -ForegroundColor Cyan
docker-compose build --no-cache

Write-Host "`n== Starting Docker Compose stack in detached mode ==" -ForegroundColor Cyan
docker-compose up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n[ERROR] Failed to start Docker Compose." -ForegroundColor Red
    Pause
    exit $LASTEXITCODE
}

Write-Host "`n== Showing running containers ==" -ForegroundColor Cyan
docker-compose ps

Write-Host "`n== Opening pgAdmin in the browser ==" -ForegroundColor Cyan
Start-Process "http://localhost:5050"

Write-Host "`n== Tailing logs (press CTRL+C to stop) ==" -ForegroundColor Green
docker-compose logs -f

Write-Host "`n== All done! Press any key to exit... ==" -ForegroundColor Green
Pause
