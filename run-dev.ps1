param(
    [bool]$SeedData = $true,
    [bool]$TrainModel = $true,
    # When true (default), calls POST /api/admin/sync-ingest-and-train (live API fetch + forecasts + RF training).
    # When false, only POST /api/admin/train-shock-model (faster; assumes DB already has fresh prices).
    [bool]$FullPipeline = $true,
    [bool]$OpenBrowser = $true,
    [bool]$InstallDeps = $true
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$doSeedData = $SeedData
$doTrainModel = $TrainModel
$doFullPipeline = $FullPipeline
$doOpenBrowser = $OpenBrowser
$doInstallDeps = $InstallDeps
$debugLogPath = Join-Path $projectRoot "debug-6d7972.log"

function Escape-SingleQuotedPath {
    param([string]$Path)
    if ($null -eq $Path) { return "" }
    return ($Path -replace "'", "''")
}

function Write-DebugLog {
    param(
        [string]$HypothesisId,
        [string]$Location,
        [string]$Message,
        [hashtable]$Data
    )
    $entry = @{
        sessionId = "6d7972"
        runId = "launcher-pre-fix"
        hypothesisId = $HypothesisId
        location = $Location
        message = $Message
        data = $Data
        timestamp = [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()
    } | ConvertTo-Json -Compress -Depth 6
    try {
        Add-Content -LiteralPath $debugLogPath -Value $entry -ErrorAction Stop
    } catch {
        Write-Warning "Debug log write failed: $($_.Exception.Message)"
    }
}

function Get-ActivateSnippet {
    $venvActivate = Join-Path $projectRoot ".venv\Scripts\Activate.ps1"
    if (Test-Path -LiteralPath $venvActivate) {
        $esc = Escape-SingleQuotedPath $venvActivate
        return ". '$esc'; "
    }
    return ""
}

function Wait-ForBackend {
    param(
        [string]$Url = "http://localhost:8000/",
        [int]$Retries = 25,
        [int]$DelaySeconds = 2
    )
    for ($i = 1; $i -le $Retries; $i++) {
        try {
            Invoke-RestMethod -Uri $Url -Method Get | Out-Null
            return $true
        } catch {
            Start-Sleep -Seconds $DelaySeconds
        }
    }
    return $false
}

Write-Host "Starting full development stack..." -ForegroundColor Cyan
Write-Host "Project root: $projectRoot" -ForegroundColor DarkCyan
#region agent log
Write-DebugLog -HypothesisId "H1" -Location "run-dev.ps1:init" -Message "launcher-start" -Data @{
    projectRoot = $projectRoot
    initialPwd = (Get-Location).Path
    seedData = $doSeedData
    trainModel = $doTrainModel
    fullPipeline = $doFullPipeline
    openBrowser = $doOpenBrowser
}
#endregion

$activateSnippet = Get-ActivateSnippet
#region agent log
Write-DebugLog -HypothesisId "H4" -Location "run-dev.ps1:activate" -Message "activate-snippet" -Data @{
    activateSnippet = $activateSnippet
}
#endregion

$sqRoot = Escape-SingleQuotedPath $projectRoot

if ($doInstallDeps) {
    Write-Host "Installing/updating Python packages from backend/requirements.txt..." -ForegroundColor Yellow
    $reqFile = Join-Path $projectRoot "backend\requirements.txt"
    if (-not (Test-Path -LiteralPath $reqFile)) {
        throw "Missing requirements file: $reqFile"
    }
    $venvPython = Join-Path $projectRoot ".venv\Scripts\python.exe"
    if (Test-Path -LiteralPath $venvPython) {
        & $venvPython -m pip install -r $reqFile
    } else {
        Push-Location -LiteralPath $projectRoot
        try {
            $env:PYTHONPATH = $projectRoot
            python -m pip install -r $reqFile
        } finally {
            Pop-Location
        }
    }
    Write-Host "Python dependencies ready." -ForegroundColor Green
}

if ($doSeedData) {
    Write-Host "Seeding database..." -ForegroundColor Yellow
    # Child session: PYTHONPATH + LiteralPath so spaces in username never break Set-Location (fixes H2/H3).
    $seedCommand = "& { `$env:PYTHONPATH='$sqRoot'; Set-Location -LiteralPath '$sqRoot'; ${activateSnippet}python -m backend.services.seeder }"
    #region agent log
    Write-DebugLog -HypothesisId "H2" -Location "run-dev.ps1:seed" -Message "seed-command-built" -Data @{
        seedCommand = $seedCommand
    }
    #endregion
    powershell -NoProfile -ExecutionPolicy Bypass -Command $seedCommand
    Write-Host "Seed step completed." -ForegroundColor Green
}

$backendCommand = "& { `$env:PYTHONPATH='$sqRoot'; Set-Location -LiteralPath '$sqRoot'; ${activateSnippet}python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload }"
$frontendCommand = "& { Set-Location -LiteralPath '$sqRoot'; npm run dev -- --host 0.0.0.0 --port 5173 }"
#region agent log
Write-DebugLog -HypothesisId "H2" -Location "run-dev.ps1:commands" -Message "service-commands-built" -Data @{
    backendCommand = $backendCommand
    frontendCommand = $frontendCommand
    sqRoot = $sqRoot
}
Write-DebugLog -HypothesisId "H2" -Location "run-dev.ps1:commands" -Message "post-fix-command-shape" -Data @{
    runId = "post-fix"
    backendStartsWithAmp = ($backendCommand.StartsWith("&"))
    backendContainsLiteralPath = ($backendCommand -match "LiteralPath")
}
#endregion

Write-Host "Launching backend terminal..." -ForegroundColor Yellow
$backendProcess = Start-Process powershell -PassThru -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command", $backendCommand
)
#region agent log
Write-DebugLog -HypothesisId "H3" -Location "run-dev.ps1:backend-start" -Message "backend-process-started" -Data @{
    pid = $backendProcess.Id
}
#endregion

Write-Host "Launching frontend terminal..." -ForegroundColor Yellow
$frontendProcess = Start-Process powershell -PassThru -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command", $frontendCommand
)
#region agent log
Write-DebugLog -HypothesisId "H3" -Location "run-dev.ps1:frontend-start" -Message "frontend-process-started" -Data @{
    pid = $frontendProcess.Id
}
#endregion

if ($doTrainModel) {
    Write-Host "Waiting for backend to become healthy..." -ForegroundColor Yellow
    if (Wait-ForBackend) {
        try {
            if ($doFullPipeline) {
                Write-Host "Running full pipeline (Agmarknet fetch per crop + forecasts + shock model training). This may take a few minutes..." -ForegroundColor Yellow
                $trainResult = Invoke-RestMethod -Uri "http://localhost:8000/api/admin/sync-ingest-and-train" -Method Post -TimeoutSec 900
            } else {
                Write-Host "Training shock model only (no live API refresh)..." -ForegroundColor Yellow
                $trainResult = Invoke-RestMethod -Uri "http://localhost:8000/api/admin/train-shock-model" -Method Post -TimeoutSec 300
            }
            Write-Host "Pipeline result: $($trainResult | ConvertTo-Json -Compress -Depth 6)" -ForegroundColor Green
        } catch {
            Write-Warning "Backend is up but pipeline call failed: $($_.Exception.Message)"
        }
    } else {
        Write-Warning "Backend did not become healthy in time. Skipping pipeline/training trigger."
    }
}

if ($doOpenBrowser) {
    Start-Process "http://localhost:5173"
    Start-Process "http://localhost:8000/docs"
}

Write-Host ""
Write-Host "Done. Stack is launching in separate terminals." -ForegroundColor Green
Write-Host "Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host "Backend:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "Swagger:  http://localhost:8000/docs" -ForegroundColor Cyan
