# scripts/check.ps1
# Run all available project checks.
$ErrorActionPreference = "Stop"
$exitCode = 0

function Get-PythonCommand {
    if (Get-Command "python" -ErrorAction SilentlyContinue) {
        return "python"
    }
    if (Get-Command "py" -ErrorAction SilentlyContinue) {
        return "py"
    }
    return $null
}

$pythonCmd = Get-PythonCommand
if (-not $pythonCmd) {
    Write-Host "ERROR: Neither 'python' nor 'py' found in PATH." -ForegroundColor Red
    exit 1
}

Write-Host "=== Running project checks ===" -ForegroundColor Cyan

$repoRoot = Split-Path -Parent $PSScriptRoot
$testDir = Join-Path $repoRoot "tests"
$harnessScript = Join-Path $repoRoot "harness\run_all.py"

# Run pytest if test files exist
if (Test-Path $testDir) {
    $pyFiles = Get-ChildItem -Path $testDir -Filter "test_*.py" -Recurse -ErrorAction SilentlyContinue
    if ($pyFiles) {
        Write-Host "--- Running pytest ---" -ForegroundColor Yellow
        & $pythonCmd -m pytest -q
        if ($LASTEXITCODE -ne 0) { $exitCode = 1 }
    } else {
        Write-Host "--- No test files found in tests/, skipping pytest ---" -ForegroundColor Yellow
    }
} else {
    Write-Host "--- tests/ directory not found, skipping pytest ---" -ForegroundColor Yellow
}

# Run harness if it exists
if (Test-Path $harnessScript) {
    Write-Host "--- Running harness ---" -ForegroundColor Yellow
    & $pythonCmd harness/run_all.py
    if ($LASTEXITCODE -ne 0) { $exitCode = 1 }
} else {
    Write-Host "--- harness/run_all.py not found, skipping harness ---" -ForegroundColor Yellow
}

if ($exitCode -eq 0) {
    Write-Host "=== All checks passed ===" -ForegroundColor Green
} else {
    Write-Host "=== Some checks failed ===" -ForegroundColor Red
}

exit $exitCode
