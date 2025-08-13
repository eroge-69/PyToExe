import os
import platform

system = platform.system()

if system == "Windows":
    os.system("shutdown /s /t 1")
elif system in ("Linux", "Darwin"):  # Darwin = macOS
    os.system("sudo shutdown now")
else:
    print(f"Unsupported OS: {system}")