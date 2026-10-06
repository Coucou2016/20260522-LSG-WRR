param([Parameter(Mandatory=$true)][string]$Path)
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$full = (Resolve-Path $Path).Path
$img = [System.Drawing.Image]::FromFile($full)
[System.Windows.Forms.Clipboard]::SetImage($img)
$img.Dispose()
Write-Output ("clipboard image set: " + $full)
