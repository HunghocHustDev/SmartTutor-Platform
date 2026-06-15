param(
    [ValidateSet("sample", "minimal", "fix")]
    [string]$Seed = "sample",
    [string]$Server = "localhost",
    [string]$Database = "TutorCenterDB",
    [string]$Username = "sa",
    [string]$Password = "123456"
)

$ErrorActionPreference = "Stop"

$scriptMap = @{
    sample  = "sample_data.sql"
    minimal = "minimal_seed.sql"
    fix     = "fix_unicode_demo_data.sql"
}

$scriptFile = Join-Path $PSScriptRoot $scriptMap[$Seed]

if (-not (Test-Path $scriptFile)) {
    throw "Seed file not found: $scriptFile"
}

Write-Host "Running $($scriptMap[$Seed]) against $Server / $Database with UTF-8 input..."

sqlcmd `
    -b `
    -S $Server `
    -d $Database `
    -U $Username `
    -P $Password `
    -C `
    -f 65001 `
    -i $scriptFile

if ($LASTEXITCODE -ne 0) {
    throw "sqlcmd failed with exit code $LASTEXITCODE"
}

Write-Host "Seed completed successfully."
