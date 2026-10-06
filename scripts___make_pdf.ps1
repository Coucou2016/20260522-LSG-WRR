param(
  [string]$Html,
  [string]$Pdf
)
$ErrorActionPreference = 'Stop'
$candidates = @(
  'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
  'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
  'C:\Program Files\Google\Chrome\Application\chrome.exe',
  'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
)
$browser = $null
foreach ($c in $candidates) {
  if (Test-Path $c) { $browser = $c; break }
}
if ($null -eq $browser) { Write-Output 'NO_BROWSER'; exit 2 }
Write-Output ('BROWSER: ' + $browser)

$fileUri = ([System.Uri](Resolve-Path $Html).Path).AbsoluteUri
if (Test-Path $Pdf) { Remove-Item $Pdf -Force }
$args = @(
  '--headless=new',
  '--disable-gpu',
  '--no-pdf-header-footer',
  ('--print-to-pdf=' + $Pdf),
  $fileUri
)
& $browser @args
for ($i = 0; $i -lt 90; $i++) {
  if ((Test-Path $Pdf) -and ((Get-Item $Pdf).Length -gt 1000)) { break }
  Start-Sleep -Milliseconds 500
}
if (Test-Path $Pdf) {
  $len = (Get-Item $Pdf).Length
  Write-Output ('PDF_OK: ' + $Pdf + ' (' + $len + ' bytes)')
} else {
  Write-Output 'PDF_FAIL'
  exit 3
}
