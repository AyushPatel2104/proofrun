# Build ProofRun C++ (Windows / MinGW)
# Usage (from 01-PROOFRUN):
#   powershell -File scripts/build_cpp.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
if (-not (Get-Command cmake -ErrorAction SilentlyContinue)) {
  $pipCmake = Join-Path $env:APPDATA "Python\Python311\Scripts"
  if (Test-Path $pipCmake) { $env:Path = "$pipCmake;$env:Path" }
}
if (-not (Get-Command cmake -ErrorAction SilentlyContinue)) {
  throw "cmake not found on PATH"
}

$BuildDir = if ($env:PROOFRUN_BUILD_DIR) { $env:PROOFRUN_BUILD_DIR } else { Join-Path $Root "build\cpp" }
New-Item -ItemType Directory -Force -Path $BuildDir | Out-Null

cmake -S (Join-Path $Root "cpp") -B $BuildDir -G "MinGW Makefiles" -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_COMPILER=g++
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python (Join-Path $Root "scripts\generate_catalog_artifacts.py") --root $Root
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
cmake --build $BuildDir --config Release -j 4
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host "Build complete: $BuildDir"
