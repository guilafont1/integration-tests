Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "Lint..."
python -m flake8 app

Write-Host "Security (Bandit)..."
python -m bandit -r app

Write-Host "Tests..."
python -m pytest

Write-Host "Pipeline OK"

