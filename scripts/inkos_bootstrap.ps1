[CmdletBinding()]
param(
  [switch] $SkipInstall
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$VendorRoot = Join-Path $ProjectRoot "vendor\inkos"
$CliEntry = Join-Path $VendorRoot "packages\cli\dist\index.js"

if (-not (Test-Path -LiteralPath (Join-Path $VendorRoot "package.json"))) {
  throw "Missing vendor\inkos\package.json. Copy InkOS into vendor\inkos first."
}

if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
  throw "Node.js is required to build InkOS."
}

if (-not (Get-Command pnpm -ErrorAction SilentlyContinue)) {
  throw "pnpm is required to build InkOS."
}

Push-Location $VendorRoot
try {
  if (-not $SkipInstall) {
    & pnpm install --frozen-lockfile
    if ($LASTEXITCODE -ne 0) {
      throw "pnpm install failed with exit code $LASTEXITCODE."
    }
  }

  & pnpm -r build
  if ($LASTEXITCODE -ne 0) {
    throw "pnpm build failed with exit code $LASTEXITCODE."
  }
}
finally {
  Pop-Location
}

if (-not (Test-Path -LiteralPath $CliEntry)) {
  throw "Build finished but InkOS CLI entry was not found: $CliEntry"
}

Write-Host "InkOS is ready. Try: powershell -ExecutionPolicy Bypass -File scripts\inkos.ps1 --help"
