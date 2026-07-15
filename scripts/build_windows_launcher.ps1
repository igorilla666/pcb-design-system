param(
    [string]$Output,
    [switch]$InstallToDesktop
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$source = Join-Path $root 'launcher\PCBProjectLauncher.cs'
if (-not $Output) {
    $Output = Join-Path $root 'launcher\PCBProjectLauncher.exe'
}
$Output = [System.IO.Path]::GetFullPath($Output)
$compiler = Join-Path $env:WINDIR 'Microsoft.NET\Framework64\v4.0.30319\csc.exe'

if (-not (Test-Path -LiteralPath $compiler)) {
    throw "C# compiler not found: $compiler"
}
if (-not (Test-Path -LiteralPath $source)) {
    throw "Launcher source not found: $source"
}

$outputDirectory = Split-Path -Parent $Output
New-Item -ItemType Directory -Force -Path $outputDirectory | Out-Null

& $compiler /nologo /target:winexe /optimize+ "/out:$Output" `
    /reference:System.Windows.Forms.dll `
    /reference:System.Drawing.dll `
    $source
if ($LASTEXITCODE -ne 0) {
    throw "Launcher compilation failed with exit code $LASTEXITCODE"
}

Write-Output "Built: $Output"

if ($InstallToDesktop) {
    $desktop = [Environment]::GetFolderPath('Desktop')
    $desktopTarget = Join-Path $desktop 'PCB Project Launcher.exe'
    Copy-Item -LiteralPath $Output -Destination $desktopTarget -Force
    Write-Output "Installed: $desktopTarget"
}
