# open_and_exit.py
import subprocess
import sys

# cmd üzerinden başlat: start kullanımı cmd'yi devreye sokar ve script'e geri döner
subprocess.run(["cmd", "/c", "start", "calc.exe"])

# script kendini kapatıyor
sys.exit(0)
