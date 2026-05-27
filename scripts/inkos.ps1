[CmdletBinding()]
param(
  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]] $Args
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$RuntimeRoot = Join-Path $ProjectRoot ".inkos-runtime"
$CliEntry = Join-Path $ProjectRoot "vendor\inkos\packages\cli\dist\index.js"

if (-not (Test-Path -LiteralPath $RuntimeRoot)) {
  New-Item -ItemType Directory -Path $RuntimeRoot | Out-Null
}

if (-not (Test-Path -LiteralPath $CliEntry)) {
  throw "InkOS CLI is not built. Run scripts\inkos_bootstrap.ps1 first."
}

Push-Location $RuntimeRoot
try {
  & node $CliEntry @Args
  $exitCode = $LASTEXITCODE
}
finally {
  Pop-Location
}

if ($null -ne $exitCode -and $exitCode -ne 0) {
  exit $exitCode
}
