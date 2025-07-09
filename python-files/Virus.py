import subprocess
import os
import time
import random

# === 1. Viele Explorer-Fenster öffnen ===
def open_folders(amount=5):
    for _ in range(amount):
        subprocess.Popen("explorer")
        time.sleep(0.3)  # kleine Pause zwischen Tabs

# === 2. Matrix-Code in PowerShell anzeigen ===
def launch_matrix_powershell():
    matrix_code = '''
$host.UI.RawUI.ForegroundColor = "Green"
while ($true) {
    $chars = "01","∰","₪","Ψ","Ж","Л"
    $line = ""
    for ($i = 0; $i -lt 80; $i++) {
        $line += $chars | Get-Random
    }
    Write-Host $line
    Start-Sleep -Milliseconds 100
}
'''
    subprocess.Popen(["powershell", "-NoExit", "-Command", matrix_code])

# === Startprogramm ===
if __name__ == "__main__":
    open_folders(10)  # Öffne 10 Ordner-Tabs
    time.sleep(1)
    launch_matrix_powershell()
