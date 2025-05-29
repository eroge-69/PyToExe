import subprocess
import os

# Útvonal az indítandó alkalmazáshoz
exe_path = r"C:\DigitalEng\app_launch\StartCreo8.bat"

# Ellenőrizzük, hogy létezik-e a fájl
if os.path.exists(exe_path):
    subprocess.Popen(exe_path)
else:
    print("A megadott fájl nem található:", exe_path)
