# One-shot bootstrap: install deps, run tests, then launch the Flask server.
# Usage from repo root:  .\start.ps1

$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $MyInvocation.MyCommand.Path
$src  = Join-Path $repo 'urban-traffic-sim'

Write-Host '==> Installing dependencies'
python -m pip install -r (Join-Path $src 'requirements.txt')
if ($LASTEXITCODE) { exit $LASTEXITCODE }

Write-Host '==> Running tests'
python -m pytest (Join-Path $src 'tests')
if ($LASTEXITCODE) { exit $LASTEXITCODE }

Write-Host '==> Starting server at http://127.0.0.1:5000/'
python (Join-Path $src 'app.py')
