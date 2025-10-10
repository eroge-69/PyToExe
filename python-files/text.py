import os
import platform

def shutdown_now():
    system = platform.system().lower()

    if system == "windows":
        os.system("shutdown /s /t 0")  # 0 = no delay
    elif system in ("linux", "darwin"):  # Linux or macOS
        os.system("shutdown -h now")
    else:
        print("Unsupported OS")

# Run immediately
shutdown_now()





