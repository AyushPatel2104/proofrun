# Run ProofRun local product server (Windows)
$Root = Split-Path -Parent $PSScriptRoot
$env:PYTHONPATH = Join-Path $Root "python"
$env:PROOFRUN_PROJECT_ROOT = $Root
$cli = Join-Path $Root "build\cpp\proofrun_cli.exe"
if (Test-Path $cli) { $env:PROOFRUN_CLI = $cli }
$Port = if ($args.Count -ge 1) { $args[0] } else { "8080" }
Write-Host "Starting ProofRun product server on http://127.0.0.1:$Port/"
python -m proofrun_py.product.server $Port
