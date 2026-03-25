Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$HostUrl = $env:LOCUST_HOST
if (-not $HostUrl) { $HostUrl = "http://127.0.0.1:8000" }

$Users = $env:LOCUST_USERS
if (-not $Users) { $Users = "50" }

$SpawnRate = $env:LOCUST_SPAWN_RATE
if (-not $SpawnRate) { $SpawnRate = "2" }

$RunTime = $env:LOCUST_RUN_TIME
if (-not $RunTime) { $RunTime = "1m" }

$OutDir = "reports"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$HtmlReport = Join-Path $OutDir "locust-report.html"
$CsvPrefix = Join-Path $OutDir "locust"

Write-Host "Locust headless..."
Write-Host "Host=$HostUrl Users=$Users SpawnRate=$SpawnRate RunTime=$RunTime"

python -m locust `
  --headless `
  -H $HostUrl `
  -u $Users `
  -r $SpawnRate `
  -t $RunTime `
  --only-summary `
  --html $HtmlReport `
  --csv $CsvPrefix

Write-Host "Rapport généré : $HtmlReport"

