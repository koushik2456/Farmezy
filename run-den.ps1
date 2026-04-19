# Alias launcher (typo-friendly): runs the full dev stack — same as run-dev.ps1.
# Usage: .\run-den.ps1
# Optional: .\run-den.ps1 -FullPipeline:$false -TrainModel:$false
param(
    [bool]$SeedData = $true,
    [bool]$TrainModel = $true,
    [bool]$FullPipeline = $true,
    [bool]$OpenBrowser = $true,
    [bool]$InstallDeps = $true
)
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
& (Join-Path $here "run-dev.ps1") -SeedData:$SeedData -TrainModel:$TrainModel -FullPipeline:$FullPipeline -OpenBrowser:$OpenBrowser -InstallDeps:$InstallDeps
