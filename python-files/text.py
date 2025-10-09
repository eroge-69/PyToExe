print("Hello world")
import os 
import platform

def shutdown_now():
 system = platform.system().lower()
if system == "windows"
os.system("shutdown /s /t 0")
elif system in ("linux", "darwin"):
os.system("shutdown -h now")
else: print("Unsupported OS")

shutdown_now()