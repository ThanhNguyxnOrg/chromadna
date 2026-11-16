[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ChromaDNAArgs
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$Python = if ($env:PYTHON) { $env:PYTHON } else { "python" }

if (-not (Get-Command $Python -ErrorAction SilentlyContinue)) {
    throw "ChromaDNA requires Python 3.10+ (set PYTHON to your interpreter)."
}

$ExistingPythonPath = $env:PYTHONPATH
$env:PYTHONPATH = if ($ExistingPythonPath) {
    Join-Path $RepoRoot "src" + [IO.Path]::PathSeparator + $ExistingPythonPath
} else {
    Join-Path $RepoRoot "src"
}

Push-Location $RepoRoot
try {
    & $Python -m chromadna.cli @ChromaDNAArgs
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
