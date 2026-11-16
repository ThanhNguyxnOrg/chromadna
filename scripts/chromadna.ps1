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
$SourcePath = Join-Path $RepoRoot "src"
$env:PYTHONPATH = if ($ExistingPythonPath) {
    $SourcePath + [IO.Path]::PathSeparator + $ExistingPythonPath
} else {
    $SourcePath
}
Push-Location $RepoRoot
try {
    & $Python -m chromadna.cli @ChromaDNAArgs
    $ExitCode = $LASTEXITCODE
}
finally {
    Pop-Location
}
exit $ExitCode
