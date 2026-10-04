# Prints the three HTML documents to PDF with Microsoft Edge (headless).
# Run after: node docs\manual\build-docs.mjs ; node docs\manual\build-architecture.mjs
# The PDFs go to $out; copies are kept in docs\manual\pdf\ in the repo.
$ErrorActionPreference = "Continue"   # Edge writes harmless log lines to stderr
$docs = $PSScriptRoot
$out = "D:\Swapnil\Personel Project\Public Ship Log"
New-Item -ItemType Directory -Force $out | Out-Null
$edge = @("${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe",
          "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe") | Where-Object { Test-Path $_ } | Select-Object -First 1
$jobs = @{
  "architecture-deck.html"    = "Public Ship Log - Architecture Document.pdf"
  "user-manual-overview.html" = "Public Ship Log - User Manual (Overview).pdf"
  "user-manual.html"          = "Public Ship Log - User Manual.pdf"
}
foreach ($src in $jobs.Keys) {
  $pdf = Join-Path $out $jobs[$src]
  $url = "file:///" + ((Join-Path $docs $src) -replace '\\', '/' -replace ' ', '%20')
  & $edge --headless=new --disable-gpu --no-pdf-header-footer --print-to-pdf="$pdf" $url 2>&1 | Out-Null
  Start-Sleep -Seconds 2
  Write-Host "$($jobs[$src])  ($([math]::Round((Get-Item $pdf).Length/1KB)) KB)"
}
