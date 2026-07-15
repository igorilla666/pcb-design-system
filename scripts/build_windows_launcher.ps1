# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 igorilla666

param(
    [string]$Output,
    [switch]$InstallToDesktop
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$source = Join-Path $root 'launcher\PCBProjectLauncher.cs'
$icon = Join-Path $root 'launcher\llm_pcb_framework.ico'
$license = Join-Path $root 'LICENSE'
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
if (-not (Test-Path -LiteralPath $icon)) {
    throw "Launcher icon not found: $icon"
}
if (-not (Test-Path -LiteralPath $license)) {
    throw "License not found: $license"
}

$outputDirectory = Split-Path -Parent $Output
New-Item -ItemType Directory -Force -Path $outputDirectory | Out-Null

& $compiler /nologo /target:winexe /optimize+ "/out:$Output" `
    "/win32icon:$icon" `
    "/resource:$license,PCBDesignSystem.LICENSE.txt" `
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
