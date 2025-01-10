./scripts/load_python_env.ps1

Write-Host ""
Write-Host "Restoring frontend npm packages"
Write-Host ""
Set-Location ./app/frontend
npm install
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to restore frontend npm packages"
    exit $LASTEXITCODE
}

Write-Host ""
Write-Host "Building frontend"
Write-Host ""
npm audit fix
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to build frontend"
    exit $LASTEXITCODE
}


Write-Host ""
Write-Host "Starting backend"
Write-Host ""
Set-Location ../backend
$venvPythonPath = "./.venv/scripts/python.exe"
if (Test-Path -Path "/usr") {
  # fallback to Linux venv path
  $venvPythonPath = "./.venv/bin/python"
}

# Start the backend process using Gunicorn with AioHTTP worker
Start-Process -FilePath $venvPythonPath `
              -ArgumentList "-m gunicorn app:create_app -b 0.0.0.0:8000 --worker-class aiohttp.GunicornWebWorker" `
              -NoNewWindow `
              -PassThru | Out-Null

# Give some time for the backend to start and check if it's running
Start-Sleep -Seconds 5
# Optionally, add a health check here to verify the backend is up

Write-Host "Backend started successfully"

# Start API
Write-Host ""
Write-Host "Starting API"
Write-Host ""
Set-Location ../api

# Determine the Python executable path for API based on the operating system
$apiVenvPythonPath = "./.venv/scripts/python.exe"  # Windows path
if ($IsLinux) {
    # Fallback to Linux virtual environment path
    $apiVenvPythonPath = "./.venv/bin/python"
}

# Start the API process using Uvicorn
Start-Process -FilePath $apiVenvPythonPath `
              -ArgumentList "-m uvicorn main:app --host 0.0.0.0 --port 8765" `
              -NoNewWindow `
              -PassThru | Out-Null

# Give some time for the API to start and check if it's running
Start-Sleep -Seconds 5
# Optionally, add a health check here to verify the API is up

Write-Host "API started successfully"

# Return to the project root directory
Set-Location ../../

Write-Host ""
Write-Host "All services started successfully."