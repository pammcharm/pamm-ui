$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$source = Join-Path $PSScriptRoot "main_engine.c"
$output = Join-Path $PSScriptRoot "main_engine.dll"
$packageCopy = Join-Path $repoRoot "py_engine\main_engine.dll"
$msysBash = "C:\msys64\usr\bin\bash.exe"

if (-not (Test-Path $msysBash)) {
    throw "MSYS2 bash was not found at $msysBash"
}

$buildCommand = @'
export PATH=/ucrt64/bin:$PATH
gcc -shared -std=c11 -O2 \
  -I/ucrt64/include/SDL2 \
  -I/ucrt64/include \
  -o /d/learn/lit_app/c_engine/main_engine.dll \
  /d/learn/lit_app/c_engine/main_engine.c \
  -L/ucrt64/lib \
  -lSDL2 -lSDL2_image -lSDL2_ttf -lSDL2_mixer \
  -lavformat -lavcodec -lavutil -lswscale
'@

& $msysBash -lc $buildCommand

Copy-Item -LiteralPath $output -Destination $packageCopy -Force

Write-Host "Built $output"
Write-Host "Copied engine DLL to $packageCopy"
